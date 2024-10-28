#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Dict

import pytest
import responses
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
from destination_convex.client import ConvexClient
from destination_convex.config import ConvexConfig
from destination_convex.destination import DestinationConvex

DEDUP_TABLE_NAME = "dedup_stream"
DEDUP_INDEX_FIELD = "int_col"


@pytest.fixture(name="config")
def config_fixture() -> ConvexConfig:
    return {
        "deployment_url": "http://deployment_url.convex.cloud",
        "access_key": "abcdef01236789",
    }


@pytest.fixture(name="client")
def client_fixture(config) -> ConvexClient:
    return ConvexClient(config)


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"string_col": {"type": "str"}, DEDUP_INDEX_FIELD: {"type": "integer"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="overwrite_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    dedup_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=DEDUP_TABLE_NAME,
            json_schema=stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
        primary_key=[[DEDUP_INDEX_FIELD]],
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream, dedup_stream])


def state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def record(stream: str, str_value: str, int_value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, DEDUP_INDEX_FIELD: int_value}, emitted_at=0),
    )


def setup_good_responses(config):
    responses.add(responses.PUT, f"{config['deployment_url']}/api/streaming_import/clear_tables", status=200)
    responses.add(responses.POST, f"{config['deployment_url']}/api/streaming_import/import_airbyte_records", status=200)
    responses.add(responses.GET, f"{config['deployment_url']}/version", status=200)
    responses.add(responses.PUT, f"{config['deployment_url']}/api/streaming_import/add_primary_key_indexes", status=200)
    responses.add(
        responses.GET,
        f"{config['deployment_url']}/api/streaming_import/primary_key_indexes_ready",
        status=200,
        json={"indexesReady": True},
    )


def setup_bad_response(config):
    responses.add(
        responses.PUT,
        f"{config['deployment_url']}/api/streaming_import/clear_tables",
        status=400,
        body="error message",
    )


@responses.activate
def test_bad_write(config: ConvexConfig, configured_catalog: ConfiguredAirbyteCatalog):
    setup_bad_response(config)
    client = ConvexClient(config, {})
    with pytest.raises(Exception) as e:
        client.delete([])

    assert (
        "Request to `http://deployment_url.convex.cloud/api/streaming_import/clear_tables` failed with status code 400: error message"
        in str(e.value)
    )


@responses.activate
def test_check(config: ConvexConfig):
    setup_good_responses(config)
    destination = DestinationConvex()
    logger = logging.getLogger("airbyte")
    destination.check(logger, config)


@responses.activate
def test_write(config: ConvexConfig, configured_catalog: ConfiguredAirbyteCatalog):
    setup_good_responses(config)
    append_stream, overwrite_stream, dedup_stream = (
        configured_catalog.streams[0].stream.name,
        configured_catalog.streams[1].stream.name,
        configured_catalog.streams[2].stream.name,
    )

    first_state_message = state({"state": "1"})
    first_append_chunk = [record(append_stream, str(i), i) for i in range(5)]
    first_overwrite_chunk = [record(overwrite_stream, str(i), i) for i in range(5)]
    first_dedup_chunk = [record(dedup_stream, str(i), i) for i in range(10)]
    first_record_chunk = first_append_chunk + first_overwrite_chunk + first_dedup_chunk
    destination = DestinationConvex()
    output_state = list(
        destination.write(
            config,
            configured_catalog,
            [
                *first_record_chunk,
                first_state_message,
            ],
        )
    )[0]
    assert first_state_message == output_state

    second_state_message = state({"state": "2"})
    second_append_chunk = [record(append_stream, str(i), i) for i in range(5, 10)]
    second_overwrite_chunk = [record(overwrite_stream, str(i), i) for i in range(5, 10)]
    second_dedup_chunk = [record(dedup_stream, str(i + 2), i) for i in range(5)]
    second_record_chunk = second_append_chunk + second_overwrite_chunk + second_dedup_chunk
    output_state = list(
        destination.write(
            config,
            configured_catalog,
            [
                *second_record_chunk,
                second_state_message,
            ],
        )
    )[0]
    assert second_state_message == output_state
