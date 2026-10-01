from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dropbox.files import FileMetadata, Metadata
from source_dropbox.normalizer import normalize_file
from source_dropbox.streams.snapshot import SnapshotStream


class Files(SnapshotStream):
    name = "files"
    primary_key = "id"

    def normalize_snapshot_entry(self, entry: Metadata) -> Mapping[str, Any] | None:
        return normalize_file(entry) if isinstance(entry, FileMetadata) else None
