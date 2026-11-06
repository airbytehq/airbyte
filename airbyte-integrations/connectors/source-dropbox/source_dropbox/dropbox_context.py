# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import dropbox
from dropbox import common
from dropbox.exceptions import AuthError, BadInputError


class DropboxContextError(ValueError):
    """Raised when Dropbox team/path-root context is invalid."""


@dataclass(frozen=True)
class DropboxContextKey:
    team_mode: str = "none"
    selected_member_id: str | None = None
    path_root_mode: str = "default"
    namespace_id: str | None = None

    def as_state_scope(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "team_mode": self.team_mode,
            "path_root_mode": self.path_root_mode,
        }
        if self.selected_member_id:
            value["selected_member_id"] = self.selected_member_id
        if self.namespace_id:
            value["namespace_id"] = self.namespace_id
        return value


def build_dropbox_client(config: Mapping[str, Any], **kwargs: Any) -> Any:
    """Build a Dropbox SDK client with optional Business member/admin and Path Root context."""
    credentials = _credentials(config)
    base = _base_client(credentials, config, **kwargs)
    return _apply_path_root(base, config)


def build_dropbox_team_client(config: Mapping[str, Any], **kwargs: Any) -> Any:
    """Build a DropboxTeam client for Business namespace discovery."""
    credentials = _credentials(config)
    return _team_client(credentials, **kwargs)


def context_key(config: Mapping[str, Any]) -> DropboxContextKey:
    team_context = _team_context(config)
    path_root = _path_root(config)
    team_mode = team_context.get("mode", "none")
    path_root_mode = path_root.get("mode", "default")
    namespace_id = path_root.get("namespace_id") if path_root_mode == "namespace_id" else None
    selected = (
        team_context.get("select_user") if team_mode == "user" else team_context.get("select_admin") if team_mode == "admin" else None
    )
    return DropboxContextKey(
        team_mode=team_mode,
        selected_member_id=selected,
        path_root_mode=path_root_mode,
        namespace_id=namespace_id,
    )


def effective_context_key(config: Mapping[str, Any], client: Any) -> DropboxContextKey:
    """Return state-safe Dropbox context, resolving home/root to effective namespace IDs."""
    key = context_key(config)
    if key.path_root_mode not in {"home", "root"}:
        return key
    namespace_id = _effective_namespace_id(client, key.path_root_mode)
    return DropboxContextKey(
        team_mode=key.team_mode,
        selected_member_id=key.selected_member_id,
        path_root_mode=key.path_root_mode,
        namespace_id=namespace_id,
    )


def _credentials(config: Mapping[str, Any]) -> Mapping[str, Any]:
    credentials = config.get("credentials")
    if not isinstance(credentials, Mapping):
        raise DropboxContextError("Dropbox credentials are required.")
    return credentials


def _base_client(credentials: Mapping[str, Any], config: Mapping[str, Any], **kwargs: Any) -> Any:
    team_context = _team_context(config)
    mode = team_context.get("mode", "none")
    if mode == "none":
        return _user_client(credentials, **kwargs)
    team = _team_client(credentials, **kwargs)
    if mode == "user":
        return team.as_user(_required_context_string(team_context, "select_user"))
    if mode == "admin":
        return team.as_admin(_required_context_string(team_context, "select_admin"))
    raise DropboxContextError("team_context.mode must be one of: none, user, admin.")


def _user_client(credentials: Mapping[str, Any], **kwargs: Any) -> dropbox.Dropbox:
    auth_type = credentials.get("auth_type")
    if auth_type == "oauth2_pkce":
        return dropbox.Dropbox(
            oauth2_refresh_token=_required_credential(credentials, "refresh_token"),
            app_key=_required_credential(credentials, "app_key"),
            **kwargs,
        )
    if auth_type == "access_token":
        return dropbox.Dropbox(
            oauth2_access_token=_required_credential(credentials, "access_token"),
            **kwargs,
        )
    raise DropboxContextError(f"Unsupported auth_type: {auth_type}")


def _team_client(credentials: Mapping[str, Any], **kwargs: Any) -> dropbox.DropboxTeam:
    auth_type = credentials.get("auth_type")
    if auth_type == "oauth2_pkce":
        return dropbox.DropboxTeam(
            oauth2_refresh_token=_required_credential(credentials, "refresh_token"),
            app_key=_required_credential(credentials, "app_key"),
            **kwargs,
        )
    if auth_type == "access_token":
        return dropbox.DropboxTeam(
            oauth2_access_token=_required_credential(credentials, "access_token"),
            **kwargs,
        )
    raise DropboxContextError(f"Unsupported auth_type: {auth_type}")


def _apply_path_root(client: Any, config: Mapping[str, Any]) -> Any:
    path_root = _path_root(config)
    mode = path_root.get("mode", "default")
    if mode == "default":
        return client
    if mode == "namespace_id":
        namespace_id = _required_context_string(path_root, "namespace_id")
        return client.with_path_root(common.PathRoot.namespace_id(namespace_id))
    try:
        account = client.users_get_current_account()
    except (AuthError, BadInputError) as exc:
        raise DropboxContextError("Dropbox could not resolve account root information for Path Root.") from exc
    root_info = getattr(account, "root_info", None)
    if mode == "home":
        namespace_id = getattr(root_info, "home_namespace_id", None)
        if not isinstance(namespace_id, str) or not namespace_id:
            raise DropboxContextError("Dropbox account does not expose a home namespace ID.")
        return client.with_path_root(common.PathRoot.home)
    if mode == "root":
        namespace_id = getattr(root_info, "root_namespace_id", None)
        if not isinstance(namespace_id, str) or not namespace_id:
            raise DropboxContextError("Dropbox account does not expose a root namespace ID.")
        return client.with_path_root(common.PathRoot.root(namespace_id))
    raise DropboxContextError("path_root.mode must be one of: default, home, root, namespace_id.")


def _effective_namespace_id(client: Any, mode: str) -> str:
    try:
        account = client.users_get_current_account()
    except (AuthError, BadInputError) as exc:
        raise DropboxContextError("Dropbox could not resolve account root information for Path Root.") from exc
    root_info = getattr(account, "root_info", None)
    field = "home_namespace_id" if mode == "home" else "root_namespace_id"
    namespace_id = getattr(root_info, field, None)
    if not isinstance(namespace_id, str) or not namespace_id:
        raise DropboxContextError(f"Dropbox account does not expose a {mode} namespace ID.")
    return namespace_id


def _team_context(config: Mapping[str, Any]) -> Mapping[str, Any]:
    value = config.get("team_context", {"mode": "none"})
    if value is None:
        return {"mode": "none"}
    if not isinstance(value, Mapping):
        raise DropboxContextError("team_context must be an object.")
    return value


def _path_root(config: Mapping[str, Any]) -> Mapping[str, Any]:
    value = config.get("path_root", {"mode": "default"})
    if value is None:
        return {"mode": "default"}
    if not isinstance(value, Mapping):
        raise DropboxContextError("path_root must be an object.")
    return value


def _required_context_string(config: Mapping[str, Any], field: str) -> str:
    value = config.get(field)
    if not isinstance(value, str) or not value:
        raise DropboxContextError(f"{field} must be a non-empty string.")
    return value


def _required_credential(credentials: Mapping[str, Any], field: str) -> str:
    value = credentials.get(field)
    if not isinstance(value, str) or not value:
        raise DropboxContextError(f"Dropbox credential {field} is required.")
    return value
