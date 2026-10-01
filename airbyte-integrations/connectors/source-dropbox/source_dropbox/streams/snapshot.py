from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from typing import Any

from dropbox.files import Metadata
from source_dropbox.streams.base import DropboxStream, with_namespace

from airbyte_cdk.models import SyncMode


class SnapshotStream(DropboxStream, ABC):
    """A full-refresh current-state view built from Dropbox list_folder pages."""

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
        for page in self.client.iter_entries(
            path=self.config.get("path", ""),
            recursive=self.config.get("recursive", True),
            # Snapshots represent current Dropbox state and never contain deletes.
            include_deleted=False,
        ):
            for entry in page.entries:
                record = self.normalize_snapshot_entry(entry)
                if record is not None:
                    yield with_namespace(dict(record), page.namespace)

    @abstractmethod
    def normalize_snapshot_entry(self, entry: Metadata) -> Mapping[str, Any] | None:
        """Return a record for metadata owned by this snapshot stream."""
