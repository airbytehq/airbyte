# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional

from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder


def read_stream(
    stream: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
) -> EntrypointOutput:
    config = ConfigBuilder().build()
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


def records_data(output: EntrypointOutput) -> List[Dict[str, Any]]:
    return [message.record.data for message in output.records]
