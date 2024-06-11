#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteCatalog
from unit_tests.sources.file_based.test_scenarios import _configured_catalog_from_mapping


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
    return _configured_catalog_from_mapping(create_configured_catalog_dict(stream_name))
