from typing import Optional, List, Mapping, Any

from airbyte_cdk import AbstractSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_protocol.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


def catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def read_records(
        source: AbstractSource,
        config: Mapping[str, Any],
        stream_name: str,
        sync_mode: SyncMode,
        state: Optional[List[AirbyteStateMessage]] = None,
        expecting_exception: Optional[bool] = False,
) -> EntrypointOutput:
    _catalog = catalog(stream_name, sync_mode)
    return read(source, config, _catalog, state, expecting_exception)
