#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteCatalogSerializer


def create_configured_catalog_dict(stream_name: str) -> Mapping[str, Any]:
    return {
        "streams": [
            {
                "stream": {
                    "name": stream_name,
                    "json_schema": {},
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
                "sync_mode": "full_refresh",
                "destination_sync_mode": "overwrite",
            }
        ]
    }


def create_configured_catalog(stream_name: str) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalogSerializer.load(create_configured_catalog_dict(stream_name))
