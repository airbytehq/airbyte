# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping, Optional

from airbyte_cdk import AbstractSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_protocol.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode


def catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    """Create a catalog with a single stream."""
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def read_records(
    source: AbstractSource,
    config: Mapping[str, Any],
    stream_name: str,
    sync_mode: SyncMode,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    """Read records from a stream."""
    _catalog = catalog(stream_name, sync_mode)
    return read(source, config, _catalog, state, expecting_exception)
