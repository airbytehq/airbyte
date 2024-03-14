#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from lib2to3.pgen2.literals import test
from typing import Any, List, Mapping, Optional

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_protocol.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from source_recharge import SourceRecharge

from .config import ConfigBuilder


def config() -> ConfigBuilder:
    return ConfigBuilder()


def catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def source() -> SourceRecharge:
    return SourceRecharge()


def read_output(
    config_builder: ConfigBuilder,
    stream_name: str,
    sync_mode: SyncMode,
    state: Optional[List[AirbyteStateMessage]] = None,
    expected_exception: Optional[bool] = False,
) -> EntrypointOutput:
    _catalog = catalog(stream_name, sync_mode)
    _config = config_builder.build()
    return read(source(), _config, _catalog, state, expected_exception)


def read_full_refresh(
    config_: ConfigBuilder,
    stream_name: str,
    expected_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_,
        stream_name=stream_name,
        sync_mode=SyncMode.full_refresh,
        expected_exception=expected_exception,
    )


def read_incremental(
    config_: ConfigBuilder,
    stream_name: str,
    state: Optional[List[AirbyteStateMessage]] = None,
    expected_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_,
        stream_name=stream_name,
        sync_mode=SyncMode.incremental,
        state=state,
        expected_exception=expected_exception,
    )


def get_cursor_value_from_state_message(
    test_output: Mapping[str, Any],
    cursor_field: Optional[str] = None,
) -> str:
    return dict(test_output.most_recent_state.stream_state).get(cursor_field)
