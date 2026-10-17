# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any

from dropbox.exceptions import ApiError, AuthError, BadInputError, RateLimitError

from source_dropbox.errors import (
    DropboxNamespaceError,
    DropboxRateLimitError,
    raise_auth_or_refresh_error,
)


@dataclass(frozen=True)
class NamespaceInfo:
    namespace_id: str
    name: str | None = None
    namespace_type: str | None = None

    def provenance(self) -> dict[str, str | None]:
        return {
            "namespace_id": self.namespace_id,
            "namespace_name": self.name,
            "namespace_type": self.namespace_type,
        }


def namespace_selection(config: Mapping[str, Any]) -> Mapping[str, Any]:
    selection = config.get("namespace_selection", {"mode": "current"})
    if selection is None:
        return {"mode": "current"}
    if not isinstance(selection, Mapping):
        raise DropboxNamespaceError("namespace_selection must be an object.")
    return selection


def resolve_namespaces(
    config: Mapping[str, Any],
    *,
    list_accessible_namespaces: Any,
) -> list[NamespaceInfo]:
    selection = namespace_selection(config)
    mode = selection.get("mode", "current")
    if mode == "current":
        return []
    if mode == "selected":
        return selected_namespaces(selection)
    if mode == "all_accessible":
        return list_accessible_namespaces(config)
    raise DropboxNamespaceError("namespace_selection.mode must be one of: current, selected, all_accessible.")


def selected_namespaces(selection: Mapping[str, Any]) -> list[NamespaceInfo]:
    values = selection.get("namespace_ids")
    if not isinstance(values, list) or not values:
        raise DropboxNamespaceError("namespace_selection.namespace_ids must contain at least one namespace ID.")
    namespaces: list[NamespaceInfo] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value:
            raise DropboxNamespaceError("namespace IDs must be non-empty strings.")
        if value in seen:
            raise DropboxNamespaceError("namespace IDs must not contain duplicates.")
        seen.add(value)
        namespaces.append(NamespaceInfo(namespace_id=value))
    return sorted(namespaces, key=lambda namespace: namespace.namespace_id)


def build_namespace_clients(
    config: Mapping[str, Any],
    *,
    namespaces: list[NamespaceInfo],
    common_kwargs: Mapping[str, Any],
    build_client: Any,
) -> dict[str, Any]:
    clients: dict[str, Any] = {}
    for namespace in namespaces:
        namespace_config = {
            **config,
            "path_root": {"mode": "namespace_id", "namespace_id": namespace.namespace_id},
        }
        clients[namespace.namespace_id] = build_client(namespace_config, **common_kwargs)
    return clients


def list_accessible_namespaces(
    config: Mapping[str, Any],
    *,
    common_kwargs: Mapping[str, Any],
    build_team_client: Any,
) -> list[NamespaceInfo]:
    try:
        team = build_team_client(config, **common_kwargs)
        result = team.team_namespaces_list()
        namespaces = [namespace_info(entry) for entry in result.namespaces]
        while result.has_more:
            result = team.team_namespaces_list_continue(result.cursor)
            namespaces.extend(namespace_info(entry) for entry in result.namespaces)
    except (AuthError, BadInputError) as exc:
        raise_auth_or_refresh_error(exc)
    except RateLimitError as exc:
        raise DropboxRateLimitError("Dropbox rate limited namespace discovery.") from exc
    except ApiError as exc:
        raise DropboxNamespaceError("Dropbox could not list accessible Business namespaces.") from exc
    return sorted(namespaces, key=lambda namespace: namespace.namespace_id)


def iter_namespace_clients(
    *,
    is_multi_namespace: bool,
    base_client: Any,
    namespaces: list[NamespaceInfo],
    namespace_clients: Mapping[str, Any],
) -> Iterator[tuple[NamespaceInfo | None, Any]]:
    if not is_multi_namespace:
        yield None, base_client
        return
    for namespace in namespaces:
        yield namespace, namespace_clients[namespace.namespace_id]


def client_for_namespace(
    *,
    namespace_id: str | None,
    base_client: Any,
    namespace_clients: Mapping[str, Any],
) -> Any:
    if namespace_id is None:
        return base_client
    try:
        return namespace_clients[namespace_id]
    except KeyError as exc:
        raise DropboxNamespaceError(f"Dropbox namespace {namespace_id} is not configured for this sync.") from exc


def namespace_info(entry: Any) -> NamespaceInfo:
    namespace_id = getattr(entry, "namespace_id", None)
    if not isinstance(namespace_id, str) or not namespace_id:
        raise DropboxNamespaceError("Dropbox returned a namespace without a stable ID.")
    name = getattr(entry, "name", None)
    namespace_type = getattr(getattr(entry, "namespace_type", None), "_tag", None)
    return NamespaceInfo(
        namespace_id=namespace_id,
        name=name if isinstance(name, str) else None,
        namespace_type=namespace_type if isinstance(namespace_type, str) else None,
    )
