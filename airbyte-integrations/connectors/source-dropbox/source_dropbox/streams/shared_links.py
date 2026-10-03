# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from source_dropbox.normalizer import normalize_shared_link
from source_dropbox.path_scope import in_configured_scope
from source_dropbox.streams.base import DropboxStream, with_namespace

from airbyte_cdk.models import SyncMode


class SharedLinks(DropboxStream):
    """Full shared-link inventory for the authenticated Dropbox account."""

    name = "shared_links"
    primary_key = "link_key"

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
        for page in self.client.iter_shared_links():
            for link in page.links:
                record = normalize_shared_link(link)
                target_path = record["target"]["path_lower"]
                if in_configured_scope(target_path, self.config.get("path", "")):
                    yield with_namespace(record, page.namespace)
                else:
                    self.logger.warning(
                        "Skipping Dropbox shared link because its target is outside the configured root or has no safe target path."
                    )
