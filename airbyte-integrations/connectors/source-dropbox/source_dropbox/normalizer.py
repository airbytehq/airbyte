from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from dropbox.files import DeletedMetadata, FileMetadata, FolderMetadata, Metadata
from dropbox.sharing import (
    FileLinkMetadata,
    FolderLinkMetadata,
    GroupMembershipInfo,
    InviteeMembershipInfo,
    SharedFolderMetadata,
    SharedLinkMetadata,
    UserMembershipInfo,
)


def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _isoformat_utc(value: object) -> str | None:
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None or value.utcoffset() is None:
        return None
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _metadata_base(entry: Metadata) -> dict[str, Any]:
    return {
        "name": entry.name,
        "path_lower": entry.path_lower,
        "path_display": entry.path_display,
    }


def _normalize_file_sharing_info(entry: FileMetadata) -> dict[str, Any] | None:
    if not entry.sharing_info:
        return None
    return {
        "read_only": entry.sharing_info.read_only,
        "parent_shared_folder_id": entry.sharing_info.parent_shared_folder_id,
        "modified_by": entry.sharing_info.modified_by,
    }


def _normalize_folder_sharing_info(entry: FolderMetadata) -> dict[str, Any] | None:
    if not entry.sharing_info:
        return None
    return {
        "read_only": entry.sharing_info.read_only,
        "parent_shared_folder_id": entry.sharing_info.parent_shared_folder_id,
        "shared_folder_id": entry.sharing_info.shared_folder_id,
        "traverse_only": entry.sharing_info.traverse_only,
        "no_access": entry.sharing_info.no_access,
    }


def normalize_file(entry: FileMetadata) -> dict[str, Any]:
    """Normalize Dropbox file metadata for the current-state snapshot stream."""
    file_lock_info = entry.file_lock_info
    return {
        **_metadata_base(entry),
        "id": entry.id,
        "rev": entry.rev,
        "client_modified": _isoformat(entry.client_modified),
        "server_modified": _isoformat(entry.server_modified),
        "size": entry.size,
        "content_hash": entry.content_hash,
        "is_downloadable": entry.is_downloadable,
        "has_explicit_shared_members": entry.has_explicit_shared_members,
        "sharing_info": _normalize_file_sharing_info(entry),
        "file_lock_info": (
            {
                "is_lockholder": file_lock_info.is_lockholder,
                "lockholder_name": file_lock_info.lockholder_name,
                "lockholder_account_id": file_lock_info.lockholder_account_id,
                "created": _isoformat(file_lock_info.created),
            }
            if file_lock_info
            else None
        ),
    }


def normalize_folder(entry: FolderMetadata) -> dict[str, Any]:
    """Normalize Dropbox folder metadata for the current-state snapshot stream."""
    return {
        **_metadata_base(entry),
        "id": entry.id,
        "shared_folder_id": entry.shared_folder_id,
        "sharing_info": _normalize_folder_sharing_info(entry),
    }


def normalize_file_property(
    entry: FileMetadata,
    property_group: Any,
    field: Any,
    *,
    template_name: str | None,
) -> dict[str, Any]:
    """Normalize one Dropbox File Properties field attached to a file."""
    template_id = getattr(property_group, "template_id", None)
    field_name = getattr(field, "name", None)
    field_value = getattr(field, "value", None)
    if not isinstance(entry.id, str) or not entry.id:
        raise ValueError("Dropbox file property record is missing a file ID.")
    if not isinstance(template_id, str) or not template_id:
        raise ValueError("Dropbox file property record is missing a template ID.")
    if not isinstance(field_name, str) or not field_name:
        raise ValueError("Dropbox file property record is missing a field name.")
    if field_value is not None and not isinstance(field_value, str):
        raise ValueError("Dropbox file property record has a non-string field value.")

    field_id = None
    field_identity = field_id or field_name
    return {
        "property_key": f"{entry.id}|{template_id}|{field_identity}",
        "file_id": entry.id,
        "file_name": entry.name,
        "path_lower": entry.path_lower,
        "path_display": entry.path_display,
        "template_id": template_id,
        "template_name": template_name,
        "field_id": field_id,
        "field_name": field_name,
        "field_value": field_value,
    }


def _tag(value: Any) -> str | None:
    return getattr(value, "_tag", None) if value is not None else None


def _optional_attr(value: Any, name: str) -> Any:
    try:
        return getattr(value, name)
    except AttributeError:
        return None


def _team(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    return {"id": value.id, "name": value.name}


def _team_member(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "display_name": value.display_name,
        "member_id": value.member_id,
        "team_info": _team(value.team_info),
    }


def normalize_shared_link(entry: SharedLinkMetadata) -> dict[str, Any]:
    """Normalize shared-link metadata without exposing Dropbox SDK objects."""
    permissions = _optional_attr(entry, "link_permissions")
    target_type = _shared_link_target_type(entry)
    path_lower = _optional_attr(entry, "path_lower")
    link_access_level = _tag(_optional_attr(permissions, "link_access_level")) if permissions else None
    requested_visibility = _tag(_optional_attr(permissions, "requested_visibility")) if permissions else None
    effective_visibility = _tag(_optional_attr(permissions, "resolved_visibility")) if permissions else None
    allow_download = _optional_attr(permissions, "allow_download") if permissions else None
    return {
        # Dropbox identifies the target, rather than the link itself. The URL is
        # the deterministic identity for an account's shared-link inventory.
        "link_key": entry.url,
        "link_id": entry.url,
        "url": entry.url,
        "target_id": entry.id,
        "name": entry.name,
        "path_lower": path_lower,
        "path_display": None,
        "link_type": target_type,
        "visibility": effective_visibility,
        "expires": _isoformat_utc(entry.expires),
        "allow_download": allow_download,
        "effective_audience": _tag(_optional_attr(permissions, "effective_audience")) if permissions else None,
        "requested_visibility": requested_visibility,
        "access_level": link_access_level,
        "target": {
            "id": entry.id,
            "type": target_type,
            "path_lower": path_lower,
            "path_display": None,
        },
        "settings": {
            "requested_visibility": requested_visibility,
            "effective_visibility": effective_visibility,
            "link_access_level": link_access_level,
            "allow_download": allow_download,
        },
        "client_modified": _isoformat_utc(_optional_attr(entry, "client_modified")),
        "server_modified": _isoformat_utc(_optional_attr(entry, "server_modified")),
        "rev": _optional_attr(entry, "rev"),
        "size": _optional_attr(entry, "size"),
        "team_member_info": _team_member(_optional_attr(entry, "team_member_info")),
        "content_owner_team_info": _team(_optional_attr(entry, "content_owner_team_info")),
    }


def _shared_link_target_type(entry: SharedLinkMetadata) -> str:
    if isinstance(entry, FileLinkMetadata):
        return "file"
    if isinstance(entry, FolderLinkMetadata):
        return "folder"
    class_name = type(entry).__name__.removesuffix("LinkMetadata").lower()
    if class_name in {"file", "folder"}:
        return class_name
    return "other"


def normalize_shared_folder(entry: SharedFolderMetadata) -> dict[str, Any]:
    """Normalize shared-folder metadata with structured policy and team data."""
    policy = entry.policy
    return {
        "shared_folder_id": entry.shared_folder_id,
        "folder_id": entry.folder_id,
        "name": entry.name,
        "path_lower": entry.path_lower,
        "path_display": entry.path_display,
        "access_type": _tag(entry.access_type),
        "is_inside_team_folder": entry.is_inside_team_folder,
        "is_team_folder": entry.is_team_folder,
        "preview_url": entry.preview_url,
        "time_invited": _isoformat(entry.time_invited),
        "parent_shared_folder_id": entry.parent_shared_folder_id,
        "owner_team": _team(entry.owner_team),
        "policy": (
            {
                "acl_update_policy": _tag(policy.acl_update_policy),
                "shared_link_policy": _tag(policy.shared_link_policy),
                "member_policy": _tag(policy.member_policy),
                "resolved_member_policy": _tag(policy.resolved_member_policy),
                "viewer_info_policy": _tag(policy.viewer_info_policy),
            }
            if policy
            else None
        ),
    }


def normalize_sharing_acl(
    resource: SharedFolderMetadata,
    member: Any,
) -> dict[str, Any]:
    """Normalize one shared-folder resource/principal membership relationship."""
    resource_id = resource.shared_folder_id
    if not isinstance(resource_id, str) or not resource_id:
        raise ValueError("Dropbox shared-folder ACL record is missing a resource ID.")
    principal = _sharing_acl_principal(member)
    access_level = _tag(_optional_attr(member, "access_type"))
    principal_identity = principal["identity"]
    return {
        "acl_key": f"{resource_id}|{principal['type']}|{principal_identity}",
        "resource_id": resource_id,
        "resource_type": "shared_folder",
        "path_lower": resource.path_lower,
        "path_display": resource.path_display,
        "principal_type": principal["type"],
        "principal_id": principal["id"],
        "principal_email": principal["email"],
        "principal_display_name": principal["display_name"],
        "access_level": access_level,
        "is_inherited": _optional_attr(member, "is_inherited"),
        "is_external": principal["is_external"],
    }


def _sharing_acl_principal(member: Any) -> dict[str, Any]:
    if isinstance(member, UserMembershipInfo):
        user = member.user
        principal_id = _optional_attr(user, "account_id")
        email = _optional_attr(user, "email")
        display_name = _optional_attr(user, "display_name")
        same_team = _optional_attr(user, "same_team")
        return {
            "type": "user",
            "id": principal_id,
            "email": email,
            "display_name": display_name,
            "is_external": (not same_team) if isinstance(same_team, bool) else None,
            "identity": _required_principal_identity(principal_id, email, "user"),
        }
    if isinstance(member, GroupMembershipInfo):
        group = member.group
        principal_id = _optional_attr(group, "group_id")
        display_name = _optional_attr(group, "group_name")
        same_team = _optional_attr(group, "same_team")
        return {
            "type": "group",
            "id": principal_id,
            "email": None,
            "display_name": display_name,
            "is_external": (not same_team) if isinstance(same_team, bool) else None,
            "identity": _required_principal_identity(principal_id, None, "group"),
        }
    if isinstance(member, InviteeMembershipInfo):
        invitee = member.invitee
        user = _optional_attr(member, "user")
        email = invitee.get_email() if invitee and invitee.is_email() else None
        principal_id = _optional_attr(user, "account_id")
        display_name = _optional_attr(user, "display_name")
        same_team = _optional_attr(user, "same_team")
        return {
            "type": "invitee",
            "id": principal_id,
            "email": email,
            "display_name": display_name,
            "is_external": (not same_team) if isinstance(same_team, bool) else None,
            "identity": _required_principal_identity(principal_id, email, "invitee"),
        }
    return {
        "type": "other",
        "id": None,
        "email": None,
        "display_name": None,
        "is_external": None,
        "identity": type(member).__name__,
    }


def _required_principal_identity(
    primary: object,
    fallback: object,
    principal_type: str,
) -> str:
    if isinstance(primary, str) and primary:
        return primary
    if isinstance(fallback, str) and fallback:
        return fallback
    raise ValueError(f"Dropbox shared-folder ACL {principal_type} member is missing a stable identity.")


def normalize_entry(entry: Metadata) -> dict[str, Any]:
    """Normalize a Dropbox listing entry without changing the public entries contract."""
    if isinstance(entry, FileMetadata):
        file = normalize_file(entry)
        return {
            "entry_key": f"file:{file['id']}",
            "entry_type": "file",
            "operation": "upsert",
            **{
                field: file[field]
                for field in (
                    "id",
                    "name",
                    "path_lower",
                    "path_display",
                    "rev",
                    "client_modified",
                    "server_modified",
                    "size",
                    "content_hash",
                    "is_downloadable",
                )
            },
        }

    if isinstance(entry, FolderMetadata):
        folder = normalize_folder(entry)
        return {
            "entry_key": f"folder:{folder['id']}",
            "entry_type": "folder",
            "operation": "upsert",
            **{field: folder[field] for field in ("id", "name", "path_lower", "path_display", "shared_folder_id")},
        }

    if isinstance(entry, DeletedMetadata):
        return {
            **_metadata_base(entry),
            "entry_key": f"deleted:{entry.path_lower}",
            "entry_type": "deleted",
            "operation": "delete",
            "id": None,
        }

    raise TypeError(f"Unsupported Dropbox metadata type: {type(entry).__name__}")
