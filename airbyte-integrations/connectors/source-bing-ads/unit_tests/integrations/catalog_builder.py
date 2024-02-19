# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder


class BingAdsCatalogBuilder(CatalogBuilder):

    def with_stream(self, name: str, sync_mode: SyncMode, pk: list[str]) -> "CatalogBuilder":
        self._streams.append(
            {
                "stream": {
                    "name": name,
                    "json_schema": {},
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_primary_key": [pk],
                },
                "primary_key": [pk],
                "sync_mode": sync_mode.name,
                "destination_sync_mode": "overwrite",
            }
        )
        return self
