# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from copy import deepcopy
from typing import Mapping, Optional

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


def read_stream(config: Mapping, stream_name: str, stream_state: Optional[Mapping] = None) -> EntrypointOutput:
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": stream_name, "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = StateBuilder().with_stream_state(stream_name, deepcopy(stream_state or {})).build()
    return read(get_source(config, stream_name, state), config=config, catalog=catalog, state=state)
