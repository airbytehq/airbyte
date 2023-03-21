#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.logger import init_logger
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from source_harvest.source import SourceHarvest

logger = init_logger("airbyte")


def test_skip_stream_default_availability_strategy(config, requests_mock):
    requests_mock.get("https://api.harvestapp.com/v2/estimates", status_code=403, json={"error": "error"})
    catalog = ConfiguredAirbyteCatalog.parse_obj({
        "streams": [
            {
                "stream": {
                    "name": "estimates",
                    "json_schema": {},
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["updated_at"]
                },
                "sync_mode": "incremental",
                "cursor_field": ["updated_at"],
                "destination_sync_mode": "append"
            }
        ]
    })

    list(SourceHarvest().read(logger, config, catalog, {}))
