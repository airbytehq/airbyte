#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from lib2to3.pgen2.literals import test
from typing import Any, List, Mapping, Optional
from unittest import TestCase

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_protocol.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from source_recharge import SourceRecharge

from .config import ConfigBuilder
from .request_builder import RequestBuilder


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


class StreamTestCase(TestCase, ABC):
    _STREAM_NAME: str

    def setUp(self):
        self._access_token = "an_access_token"
        self._config = config().with_access_token(self._access_token)

    def stream_request(self):
        return RequestBuilder.get_endpoint(self._STREAM_NAME).with_access_token(self._access_token)
