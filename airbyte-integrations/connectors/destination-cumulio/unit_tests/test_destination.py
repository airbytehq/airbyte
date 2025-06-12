#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from logging import Logger, getLogger
from typing import Any, Mapping
from unittest.mock import MagicMock, call, patch

import pytest
from destination_cumulio.destination import DestinationCumulio

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


@pytest.fixture(name="logger")
def logger_fixture() -> Logger:
    return getLogger("airbyte")


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    return {
        "api_key": "123abc",
        "api_token": "456def",
        "api_host": "https://api.cumul.io",
    }


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {
            "string_column": {"type": "integer"},
            "int_column": {"type": "integer"},
        },
    }

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="append_stream",
            json_schema=stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="overwrite_stream",
            json_schema=stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream])


@pytest.fixture(name="airbyte_message_1")
def airbyte_message_1_fixture() -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="append_stream",
            data={"string_column": "value_1", "int_column": 1},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@pytest.fixture(name="airbyte_message_2")
def airbyte_message_2_fixture() -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="overwrite_stream",
            data={"string_column": "value_2", "int_column": 2},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@pytest.fixture(name="airbyte_state_message")
def airbyte_state_message_fixture() -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={}))


def test_check(config: Mapping[str, Any], logger: MagicMock):
    with patch("destination_cumulio.destination.CumulioClient") as cumulio_client:
        destination_cumulio = DestinationCumulio()
        destination_cumulio.check(logger, config)
        assert cumulio_client.mock_calls == [
            call(config, logger),
            call().test_api_token(),
        ]


def test_write_no_input_messages(
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    airbyte_message_1: AirbyteMessage,
    airbyte_message_2: AirbyteMessage,
    airbyte_state_message: AirbyteMessage,
    logger: MagicMock,
):
    with patch("destination_cumulio.destination.CumulioWriter") as cumulio_writer:
        destination_cumulio = DestinationCumulio()

        input_messages = [airbyte_state_message]
        result = list(destination_cumulio.write(config, configured_catalog, input_messages))
        assert result == [airbyte_state_message]

        assert cumulio_writer.mock_calls == [
            call(config, configured_catalog, logger),
            call().delete_stream_entries("overwrite_stream"),
            call().flush_all(),  # The first flush_all is called before yielding the state message
            call().flush_all(),  # The second flush_all is called after going through all input messages
        ]


def test_write(
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    airbyte_message_1: AirbyteMessage,
    airbyte_message_2: AirbyteMessage,
    airbyte_state_message: AirbyteMessage,
    logger: MagicMock,
):
    with patch("destination_cumulio.destination.CumulioWriter") as cumulio_writer:
        input_messages = [airbyte_message_1, airbyte_message_2, airbyte_state_message]
        destination_cumulio = DestinationCumulio()
        result = list(destination_cumulio.write(config, configured_catalog, input_messages))
        assert result == [airbyte_state_message]
        assert cumulio_writer.mock_calls == [
            call(config, configured_catalog, logger),
            call().delete_stream_entries("overwrite_stream"),
            call().queue_write_operation("append_stream", {"string_column": "value_1", "int_column": 1}),
            call().queue_write_operation("overwrite_stream", {"string_column": "value_2", "int_column": 2}),
            call().flush_all(),  # The first flush_all is called before yielding the state message
            call().flush_all(),  # The second flush_all is called after going through all input messages
        ]
