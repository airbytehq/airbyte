from __future__ import annotations

from typing import Any

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_dropbox.client import DropboxClient
from source_dropbox.streams.entries import Entries
from source_dropbox.streams.file_properties import FileProperties
from source_dropbox.streams.files import Files
from source_dropbox.streams.folders import Folders
from source_dropbox.streams.shared_folders import SharedFolders
from source_dropbox.streams.shared_links import SharedLinks
from source_dropbox.streams.sharing_acl import SharingAcl


class SourceDropbox(AbstractSource):
    def check_connection(self, logger: Any, config: dict[str, Any]) -> tuple[bool, Any]:
        try:
            DropboxClient(config).current_account()
            return True, None
        except Exception as exc:  # Airbyte expects a user-facing failure message.
            return False, f"Unable to connect to Dropbox: {exc}"

    def streams(self, config: dict[str, Any]) -> list[Stream]:
        client = DropboxClient(config)
        return [
            Entries(client, config),
            Files(client, config),
            Folders(client, config),
            FileProperties(client, config),
            SharedLinks(client, config),
            SharedFolders(client, config),
            SharingAcl(client, config),
        ]
