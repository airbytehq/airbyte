from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from source_dropbox.client import DropboxSharingAclError
from source_dropbox.normalizer import normalize_sharing_acl
from source_dropbox.path_scope import in_configured_scope
from source_dropbox.streams.base import DropboxStream, with_namespace

from airbyte_cdk.models import SyncMode


class SharingAcl(DropboxStream):
    """Full-refresh shared-folder membership inventory."""

    name = "sharing_acl"
    primary_key = "acl_key"

    @property
    def supports_incremental(self) -> bool:
        return False

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: list[str] | None = None,
        stream_slice: Mapping[str, Any] | None = None,
        stream_state: Mapping[str, Any] | None = None,
    ) -> Iterable[Mapping[str, Any]]:
        seen: dict[str, Mapping[str, Any]] = {}
        for folder_page in self.client.iter_shared_folders():
            for folder in folder_page.entries:
                if not in_configured_scope(folder.path_lower, self.config.get("path", "")):
                    self.logger.warning(
                        "Skipping Dropbox shared-folder ACLs because the folder is outside the configured root or has no safe target path."
                    )
                    continue
                if not isinstance(folder.shared_folder_id, str) or not folder.shared_folder_id:
                    raise DropboxSharingAclError("Dropbox returned an in-scope shared folder without a stable ID.")
                for member_page in self.client.iter_shared_folder_members(folder.shared_folder_id):
                    for member in [
                        *member_page.users,
                        *member_page.groups,
                        *member_page.invitees,
                    ]:
                        record = normalize_sharing_acl(folder, member)
                        record = with_namespace(record, folder_page.namespace)
                        acl_key = record["acl_key"]
                        duplicate = seen.get(acl_key)
                        if duplicate == record:
                            continue
                        if duplicate is not None:
                            raise DropboxSharingAclError(
                                f"Dropbox returned conflicting duplicate sharing ACL records for resource {record['resource_id']}."
                            )
                        seen[acl_key] = record
                        yield record
