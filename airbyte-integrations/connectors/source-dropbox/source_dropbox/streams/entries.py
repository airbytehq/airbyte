# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from typing import Any

from source_dropbox.client import NamespaceInfo
from source_dropbox.normalizer import normalize_entry
from source_dropbox.streams.base import DropboxStream, with_namespace

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import CheckpointMixin
from airbyte_cdk.sources.streams.checkpoint import CheckpointMode


class Entries(DropboxStream, CheckpointMixin):
    name = "entries"
    primary_key = "entry_key"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._state: MutableMapping[str, Any] = {}
        self._pages: dict[str, tuple[list[Any], NamespaceInfo | None, str]] = {}
        self._context_scope = _client_context_scope(self.client)

    @property
    def cursor_field(self) -> list[str]:
        # The cursor is connector state only; it is never added to a destination
        # record or to the public stream schema. Advertising a synthetic cursor
        # field breaks destinations that validate configured cursor fields
        # against the stream JSON schema.
        return []

    @property
    def supports_incremental(self) -> bool:
        return True

    @property
    def _checkpoint_mode(self) -> CheckpointMode:
        # CDK 6.x treats an incremental stream with an empty cursor_field as
        # resumable full refresh by default. entries deliberately has no public
        # record cursor, but it does have stream-managed incremental state.
        return CheckpointMode.INCREMENTAL

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        incoming = dict(value or {})
        context = incoming.get("context")
        if context is not None and context != self._context_scope:
            raise ValueError("Dropbox entries state context does not match the configured root.")
        if _is_multi_namespace(self.client) and incoming.get("cursor"):
            raise ValueError(
                "Dropbox entries single-namespace state cannot be reused with namespace_selection selected/all_accessible; reset state."
            )
        self._state = incoming

    def _cursor_for_sync(self, sync_mode: SyncMode) -> Mapping[str, str] | str | None:
        """Return a saved cursor only for an incremental change sync.

        A full refresh is always a new snapshot from the configured root. It may
        emit page checkpoints for Airbyte during that job, but it must never use a
        prior full-refresh checkpoint as a Dropbox change cursor.
        """
        if sync_mode == SyncMode.incremental:
            if _is_multi_namespace(self.client):
                namespaces = self.state.get("namespaces", {})
                if not isinstance(namespaces, Mapping):
                    raise ValueError("Dropbox entries namespace state must be an object.")
                cursors: dict[str, str] = {}
                for namespace_id, state in namespaces.items():
                    if not isinstance(namespace_id, str) or not isinstance(state, Mapping):
                        raise ValueError("Dropbox entries namespace state is invalid.")
                    cursor = state.get("cursor")
                    if isinstance(cursor, str) and cursor:
                        cursors[namespace_id] = cursor
                return cursors
            if _requires_context_scope(self._context_scope):
                context = self.state.get("context")
                if context is None and self.state.get("cursor"):
                    raise ValueError(
                        "Dropbox entries state has no Business/Path Root context; reset state before using this configured root."
                    )
            return self.state.get("cursor")
        return None

    def stream_slices(
        self,
        *,
        sync_mode: SyncMode,
        cursor_field: list[str] | None = None,
        stream_state: Mapping[str, Any] | None = None,
    ) -> Iterable[Mapping[str, Any]]:
        cursor = self._cursor_for_sync(sync_mode)

        for page in self.client.iter_entries(
            path=self.config.get("path", ""),
            recursive=self.config.get("recursive", True),
            include_deleted=self.config.get("include_deleted", True),
            cursor=cursor,
        ):
            # Keep Dropbox SDK metadata out of slice logs. The opaque cursor lets
            # read_records retrieve exactly one complete Dropbox page.
            page_id = _page_id(page.cursor, page.namespace)
            self._pages[page_id] = (page.entries, page.namespace, page.cursor)
            yield {"cursor": page_id}
            if not self._page_was_checkpointed(page.cursor, page.namespace):
                # The CDK can stop consuming a slice when an internal record limit
                # is reached. Do not advance to a later Dropbox page unless this
                # page completed and updated its state.
                return

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: list[str] | None = None,
        stream_slice: Mapping[str, Any] | None = None,
        stream_state: Mapping[str, Any] | None = None,
    ) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            return

        page_cursor = stream_slice["cursor"]
        cached_page = self._pages[page_cursor]
        if isinstance(cached_page, tuple):
            entries, page_namespace, dropbox_cursor = cached_page
        else:
            entries, page_namespace, dropbox_cursor = cached_page, None, page_cursor
        try:
            for entry in entries:
                yield with_namespace(normalize_entry(entry), page_namespace)

            # The CDK observes this state and emits a checkpoint after
            # read_records() finishes for the slice. A Dropbox cursor therefore
            # never advances until every record in its page has been yielded.
            self._checkpoint_page(dropbox_cursor, page_namespace)
        finally:
            # A normalization or downstream read failure must not retain Dropbox
            # metadata in memory for the lifetime of the stream instance.
            self._pages.pop(page_cursor, None)

    def _page_was_checkpointed(self, cursor: str, namespace: NamespaceInfo | None) -> bool:
        if namespace is None:
            return self.state.get("cursor") == cursor
        namespaces = self.state.get("namespaces", {})
        if not isinstance(namespaces, Mapping):
            return False
        state = namespaces.get(namespace.namespace_id)
        return isinstance(state, Mapping) and state.get("cursor") == cursor

    def _checkpoint_page(self, cursor: str, namespace: NamespaceInfo | None) -> None:
        if namespace is None:
            state = {"cursor": cursor}
            if _requires_context_scope(self._context_scope):
                state["context"] = self._context_scope
            self.state = state
            return
        namespaces = dict(self.state.get("namespaces", {}))
        namespaces[namespace.namespace_id] = {"cursor": cursor}
        self.state = {
            "context": self._context_scope,
            "namespaces": {namespace_id: namespaces[namespace_id] for namespace_id in sorted(namespaces)},
        }


def _requires_context_scope(context: Mapping[str, Any]) -> bool:
    return context != {
        "team_mode": "none",
        "path_root_mode": "default",
    }


def _client_context_scope(client: Any) -> dict[str, Any]:
    try:
        context = client.context_scope()
    except AttributeError:
        context = None
    if isinstance(context, Mapping):
        return dict(context)
    return {"team_mode": "none", "path_root_mode": "default"}


def _is_multi_namespace(client: Any) -> bool:
    return getattr(client, "is_multi_namespace", False) is True


def _page_id(cursor: str, namespace: NamespaceInfo | None) -> str:
    if namespace is None:
        return cursor
    return f"{namespace.namespace_id}:{cursor}"
