from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any

from dropbox.exceptions import ApiError, AuthError, BadInputError, RateLimitError
from dropbox.file_properties import GetTemplateResult, TemplateFilterBase
from dropbox.files import ListFolderContinueError, ListFolderResult, Metadata

from source_dropbox.dropbox_context import (
    build_dropbox_client,
    build_dropbox_team_client,
    effective_context_key,
)
from source_dropbox.errors import (
    DropboxAuthenticationError,
    DropboxCursorResetError,
    DropboxFilePropertiesError,
    DropboxNamespaceError,
    DropboxRateLimitError,
    DropboxSharedFoldersCursorResetError,
    DropboxSharedLinksCursorResetError,
    DropboxSharingAclError,
    DropboxSharingPermissionError,
    raise_auth_or_refresh_error,
)
from source_dropbox.namespaces import (
    NamespaceInfo,
    build_namespace_clients,
    client_for_namespace,
    iter_namespace_clients,
    list_accessible_namespaces,
    namespace_selection,
    resolve_namespaces,
)
from source_dropbox.sharing import (
    SharedFolderMembersPage,
    SharedFoldersPage,
    SharedLinksPage,
    iter_shared_folder_members,
    iter_shared_folders,
    iter_shared_links,
    list_shared_folders,
    to_shared_folder_members_page,
    to_shared_folders_page,
    to_shared_links_page,
)


__all__ = [
    "DropboxAuthenticationError",
    "DropboxClient",
    "DropboxCursorResetError",
    "DropboxFilePropertiesError",
    "DropboxNamespaceError",
    "DropboxPage",
    "DropboxRateLimitError",
    "DropboxSharedFoldersCursorResetError",
    "DropboxSharedLinksCursorResetError",
    "DropboxSharingAclError",
    "DropboxSharingPermissionError",
    "NamespaceInfo",
    "SharedFolderMembersPage",
    "SharedFoldersPage",
    "SharedLinksPage",
    "build_dropbox_client",
    "build_dropbox_team_client",
]


@dataclass(frozen=True)
class DropboxPage:
    entries: list[Metadata]
    cursor: str
    has_more: bool
    namespace: NamespaceInfo | None = None


class DropboxClient:
    def __init__(
        self,
        config: dict[str, Any],
    ) -> None:
        common_kwargs = {
            "max_retries_on_error": 5,
            "max_retries_on_rate_limit": 5,
        }

        self._config = config
        self._common_kwargs = common_kwargs
        self._client = build_dropbox_client(config, **common_kwargs)
        self._context_scope = effective_context_key(config, self._client).as_state_scope()
        self._namespaces = self._resolve_namespaces(config)
        self._namespace_clients = self._build_namespace_clients(config)
        self._shared_folder_clients: dict[str, Any] = {}

    def context_scope(self) -> dict[str, Any]:
        return dict(self._context_scope)

    @property
    def namespace_mode(self) -> str:
        return namespace_selection(getattr(self, "_config", {})).get("mode", "current")

    @property
    def is_multi_namespace(self) -> bool:
        return self.namespace_mode != "current"

    @property
    def namespaces(self) -> list[NamespaceInfo]:
        return list(self._namespaces)

    def current_account(self) -> Any:
        try:
            account = self._client.users_get_current_account()
            if self.is_multi_namespace:
                for _, client in self._iter_namespace_clients():
                    client.files_list_folder(
                        path=self._config.get("path", ""),
                        recursive=False,
                        include_deleted=False,
                    )
            return account
        except (AuthError, BadInputError) as exc:
            self._raise_auth_or_refresh_error(exc)
        except ApiError as exc:
            raise DropboxNamespaceError("Dropbox namespace selection is invalid or inaccessible.") from exc
        except RateLimitError as exc:
            raise DropboxRateLimitError("Dropbox rate limited the connection check.") from exc

    def list_folder(self, path: str, recursive: bool, include_deleted: bool) -> DropboxPage:
        return self._list_folder_for_client(self._client, path=path, recursive=recursive, include_deleted=include_deleted)

    def _list_folder_for_client(
        self,
        client: Any,
        *,
        path: str,
        recursive: bool,
        include_deleted: bool,
        namespace: NamespaceInfo | None = None,
    ) -> DropboxPage:
        try:
            result = client.files_list_folder(
                path=path,
                recursive=recursive,
                include_deleted=include_deleted,
            )
        except (AuthError, BadInputError) as exc:
            self._raise_auth_or_refresh_error(exc)
        except RateLimitError as exc:
            raise DropboxRateLimitError("Dropbox rate limited folder synchronization.") from exc
        return self._to_page(result, namespace=namespace)

    def list_folder_with_property_groups(self, path: str, recursive: bool) -> DropboxPage:
        return self._list_folder_with_property_groups_for_client(self._client, path=path, recursive=recursive)

    def _list_folder_with_property_groups_for_client(
        self,
        client: Any,
        *,
        path: str,
        recursive: bool,
        include_property_groups: TemplateFilterBase,
        namespace: NamespaceInfo | None = None,
    ) -> DropboxPage:
        """List live folder entries with all attached Dropbox File Properties."""
        try:
            result = client.files_list_folder(
                path=path,
                recursive=recursive,
                include_deleted=False,
                include_property_groups=include_property_groups,
            )
        except (AuthError, BadInputError) as exc:
            self._raise_auth_or_refresh_error(exc)
        except RateLimitError as exc:
            raise DropboxRateLimitError("Dropbox rate limited file-property synchronization.") from exc
        except ApiError as exc:
            raise DropboxFilePropertiesError("Dropbox could not list files with File Properties.") from exc
        return self._to_page(result, namespace=namespace)

    def list_folder_continue(self, cursor: str) -> DropboxPage:
        return self._list_folder_continue_for_client(self._client, cursor)

    def _list_folder_continue_for_client(self, client: Any, cursor: str, namespace: NamespaceInfo | None = None) -> DropboxPage:
        try:
            result = client.files_list_folder_continue(cursor)
        except (AuthError, BadInputError) as exc:
            self._raise_auth_or_refresh_error(exc)
        except ApiError as exc:
            if isinstance(exc.error, ListFolderContinueError) and exc.error.is_reset():
                raise DropboxCursorResetError("Dropbox invalidated the saved folder cursor.") from exc
            raise
        except RateLimitError as exc:
            raise DropboxRateLimitError("Dropbox rate limited folder synchronization.") from exc
        return self._to_page(result, namespace=namespace)

    def iter_entries(
        self,
        *,
        path: str,
        recursive: bool,
        include_deleted: bool,
        cursor: Mapping[str, str] | str | None = None,
    ) -> Iterator[DropboxPage]:
        if self.is_multi_namespace:
            cursor_by_namespace = cursor if isinstance(cursor, dict) else {}
            for namespace, client in self._iter_namespace_clients():
                namespace_cursor = cursor_by_namespace.get(namespace.namespace_id)
                yield from self._iter_entries_for_client(
                    client,
                    path=path,
                    recursive=recursive,
                    include_deleted=include_deleted,
                    cursor=namespace_cursor,
                    namespace=namespace,
                )
            return
        if not hasattr(self, "_client"):
            yield from self._iter_entries_legacy(
                path=path,
                recursive=recursive,
                include_deleted=include_deleted,
                cursor=cursor if isinstance(cursor, str) else None,
            )
            return
        yield from self._iter_entries_for_client(
            self._client,
            path=path,
            recursive=recursive,
            include_deleted=include_deleted,
            cursor=cursor if isinstance(cursor, str) else None,
        )

    def _iter_entries_for_client(
        self,
        client: Any,
        *,
        path: str,
        recursive: bool,
        include_deleted: bool,
        cursor: str | None = None,
        namespace: NamespaceInfo | None = None,
    ) -> Iterator[DropboxPage]:
        reset_recovered = False
        try:
            page = (
                self._list_folder_continue_for_client(client, cursor, namespace)
                if cursor
                else self._list_folder_for_client(
                    client,
                    path=path,
                    recursive=recursive,
                    include_deleted=include_deleted,
                    namespace=namespace,
                )
            )
        except DropboxCursorResetError:
            page = self._list_folder_for_client(
                client,
                path=path,
                recursive=recursive,
                include_deleted=include_deleted,
                namespace=namespace,
            )
            reset_recovered = True

        while True:
            yield page
            if not page.has_more:
                break
            try:
                page = self._list_folder_continue_for_client(client, page.cursor, namespace)
            except DropboxCursorResetError:
                if reset_recovered:
                    raise
                # A reset cannot safely resume a partial listing. Restarting from the
                # configured root may replay records, but cannot skip records.
                page = self._list_folder_for_client(
                    client,
                    path=path,
                    recursive=recursive,
                    include_deleted=include_deleted,
                    namespace=namespace,
                )
                reset_recovered = True

    def _iter_entries_legacy(
        self,
        *,
        path: str,
        recursive: bool,
        include_deleted: bool,
        cursor: str | None = None,
    ) -> Iterator[DropboxPage]:
        reset_recovered = False
        try:
            page = self.list_folder_continue(cursor) if cursor else self.list_folder(path, recursive, include_deleted)
        except DropboxCursorResetError:
            page = self.list_folder(path, recursive, include_deleted)
            reset_recovered = True

        while True:
            yield page
            if not page.has_more:
                break
            try:
                page = self.list_folder_continue(page.cursor)
            except DropboxCursorResetError:
                if reset_recovered:
                    raise
                page = self.list_folder(path, recursive, include_deleted)
                reset_recovered = True

    def iter_entries_with_property_groups(
        self,
        *,
        path: str,
        recursive: bool,
    ) -> Iterator[DropboxPage]:
        template_ids = self.list_property_template_ids()
        if not template_ids:
            return

        include_property_groups = TemplateFilterBase.filter_some(template_ids)
        for namespace, client in self._iter_namespace_clients():
            page = self._list_folder_with_property_groups_for_client(
                client,
                path=path,
                recursive=recursive,
                include_property_groups=include_property_groups,
                namespace=namespace,
            )
            while True:
                yield page
                if not page.has_more:
                    break
                page = self._list_folder_continue_for_client(client, page.cursor, namespace)

    def list_property_template_ids(self) -> list[str]:
        try:
            result = self._client.file_properties_templates_list_for_user()
        except (AuthError, BadInputError) as exc:
            self._raise_auth_or_refresh_error(exc)
        except RateLimitError as exc:
            raise DropboxRateLimitError("Dropbox rate limited file-property template synchronization.") from exc
        except ApiError as exc:
            raise DropboxFilePropertiesError("Dropbox could not list File Properties templates.") from exc

        template_ids = getattr(result, "template_ids", None)
        if template_ids is None:
            return []
        if not isinstance(template_ids, list) or not all(isinstance(template_id, str) and template_id for template_id in template_ids):
            raise DropboxFilePropertiesError("Dropbox returned malformed File Properties template IDs.")
        return template_ids

    def get_property_template(self, template_id: str) -> GetTemplateResult | None:
        try:
            return self._client.file_properties_templates_get_for_user(template_id)
        except (AuthError, BadInputError) as exc:
            self._raise_auth_or_refresh_error(exc)
        except RateLimitError as exc:
            raise DropboxRateLimitError("Dropbox rate limited file-property template synchronization.") from exc
        except ApiError:
            # Property values remain valid even when the human-readable template
            # schema is unavailable. The stream emits a null template_name.
            return None

    def iter_shared_links(self) -> Iterator[SharedLinksPage]:
        yield from iter_shared_links(self._iter_namespace_clients)

    def _iter_shared_links_for_client(self, client: Any, namespace: NamespaceInfo | None = None) -> Iterator[SharedLinksPage]:
        from source_dropbox.sharing import iter_shared_links_for_client

        yield from iter_shared_links_for_client(client, namespace=namespace)

    def iter_shared_folders(self) -> Iterator[SharedFoldersPage]:
        shared_folder_clients = getattr(self, "_shared_folder_clients", None)
        if shared_folder_clients is None:
            self._shared_folder_clients = {}
            shared_folder_clients = self._shared_folder_clients
        yield from iter_shared_folders(
            self._iter_namespace_clients,
            shared_folder_clients=shared_folder_clients,
        )

    def _iter_shared_folders_for_client(self, client: Any, namespace: NamespaceInfo | None = None) -> Iterator[SharedFoldersPage]:
        from source_dropbox.sharing import iter_shared_folders_for_client

        shared_folder_clients = getattr(self, "_shared_folder_clients", None)
        if shared_folder_clients is None:
            self._shared_folder_clients = {}
            shared_folder_clients = self._shared_folder_clients
        yield from iter_shared_folders_for_client(client, namespace=namespace, shared_folder_clients=shared_folder_clients)

    def iter_shared_folder_members(self, shared_folder_id: str) -> Iterator[SharedFolderMembersPage]:
        yield from iter_shared_folder_members(
            shared_folder_id,
            base_client=self._client,
            shared_folder_clients=getattr(self, "_shared_folder_clients", {}),
        )

    def _list_shared_folders(self, client: Any) -> Any:
        return list_shared_folders(client)

    @classmethod
    def _raise_auth_or_refresh_error(cls, exc: AuthError | BadInputError, *, required_scope: str | None = None) -> None:
        raise_auth_or_refresh_error(exc, required_scope=required_scope)

    @staticmethod
    def _to_page(result: ListFolderResult, namespace: NamespaceInfo | None = None) -> DropboxPage:
        return DropboxPage(
            entries=list(result.entries),
            cursor=result.cursor,
            has_more=result.has_more,
            namespace=namespace,
        )

    @staticmethod
    def _to_shared_links_page(result: Any, namespace: NamespaceInfo | None = None) -> SharedLinksPage:
        return to_shared_links_page(result, namespace=namespace)

    @staticmethod
    def _to_shared_folders_page(result: Any, namespace: NamespaceInfo | None = None) -> SharedFoldersPage:
        return to_shared_folders_page(result, namespace=namespace)

    @staticmethod
    def _to_shared_folder_members_page(
        result: Any,
    ) -> SharedFolderMembersPage:
        return to_shared_folder_members_page(result)

    def _iter_namespace_clients(self) -> Iterator[tuple[NamespaceInfo | None, Any]]:
        if self.is_multi_namespace:
            yield from iter_namespace_clients(
                is_multi_namespace=True,
                base_client=None,
                namespaces=getattr(self, "_namespaces", []),
                namespace_clients=getattr(self, "_namespace_clients", {}),
            )
            return
        yield from iter_namespace_clients(
            is_multi_namespace=False,
            base_client=self._client,
            namespaces=getattr(self, "_namespaces", []),
            namespace_clients=getattr(self, "_namespace_clients", {}),
        )

    def _client_for_namespace(self, namespace_id: str | None) -> Any:
        return client_for_namespace(
            namespace_id=namespace_id,
            base_client=self._client,
            namespace_clients=getattr(self, "_namespace_clients", {}),
        )

    def _resolve_namespaces(self, config: Mapping[str, Any]) -> list[NamespaceInfo]:
        return resolve_namespaces(
            config,
            list_accessible_namespaces=self._list_accessible_namespaces,
        )

    def _build_namespace_clients(self, config: Mapping[str, Any]) -> dict[str, Any]:
        return build_namespace_clients(
            config,
            namespaces=self._namespaces,
            common_kwargs=self._common_kwargs,
            build_client=build_dropbox_client,
        )

    def _list_accessible_namespaces(self, config: Mapping[str, Any]) -> list[NamespaceInfo]:
        return list_accessible_namespaces(
            config,
            common_kwargs=self._common_kwargs,
            build_team_client=build_dropbox_team_client,
        )
