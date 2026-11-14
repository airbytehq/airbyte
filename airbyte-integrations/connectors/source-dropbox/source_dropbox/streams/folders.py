# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dropbox.files import FolderMetadata, Metadata
from source_dropbox.normalizer import normalize_folder
from source_dropbox.streams.snapshot import SnapshotStream


class Folders(SnapshotStream):
    name = "folders"
    primary_key = "id"

    def normalize_snapshot_entry(self, entry: Metadata) -> Mapping[str, Any] | None:
        return normalize_folder(entry) if isinstance(entry, FolderMetadata) else None
