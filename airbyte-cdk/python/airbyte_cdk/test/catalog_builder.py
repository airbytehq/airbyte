# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List

from airbyte_protocol.models import ConfiguredAirbyteCatalog, SyncMode


class CatalogBuilder:
    def __init__(self) -> None:
        self._streams: List[Dict[str, Any]] = []

    def with_stream(self, name: str, sync_mode: SyncMode) -> "CatalogBuilder":
        self._streams.append(
            {
                "stream": {
                    "name": name,
                    "json_schema": {},
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_primary_key": [["id"]],
                },
                "primary_key": [["id"]],
                "sync_mode": sync_mode.name,
                "destination_sync_mode": "overwrite",
            }
        )
        return self

    def build(self) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog.parse_obj({"streams": self._streams})
