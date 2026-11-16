# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional

from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover, read
from airbyte_cdk.test.state_builder import StateBuilder


def read_stream(
    stream_name: str,
    sync_mode: SyncMode,
    config: Dict[str, Any],
    state: Optional[List[AirbyteStateMessage]] = None,
) -> EntrypointOutput:
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


def discover_schema(stream_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    output = discover(get_source(config=config), config=config)
    return next(stream.json_schema for stream in output.catalog.catalog.streams if stream.name == stream_name)
