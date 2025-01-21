#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Dict, Mapping

import pytest
from destination_firestore import DestinationFirestore
from destination_firestore.writer import FirestoreWriter
from google.cloud import firestore

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}}}

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

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream])


@pytest.fixture(autouse=True)
def teardown(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    writer = FirestoreWriter(**config)
    for stream in configured_catalog.streams:
        writer.purge(stream.stream.name)


@pytest.fixture(name="writer")
def client_fixture(config) -> FirestoreWriter:
    writer = FirestoreWriter(**config)
    return writer


def test_check_valid_config(config: Mapping):
    outcome = DestinationFirestore().check(logging.getLogger("airbyte"), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationFirestore().check(logging.getLogger("airbyte"), {"project_id": "not_a_real_id"})
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, str_value: str, int_value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, "int_col": int_value}, emitted_at=0)
    )


def retrieve_all_records(client):
    return [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=collection.id, data=doc.to_dict(), emitted_at=0))
        for collection in client.collections()
        for doc in collection.order_by("int_col", direction=firestore.Query.ASCENDING).stream()
    ]


def test_write_append(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, writer: FirestoreWriter):
    """
    This test verifies that writing a stream in "append" mode appends new records without deleting the old ones

    It checks also if the correct state message is output by the connector at the end of the sync
    """
    stream = configured_catalog.streams[0].stream.name
    destination = DestinationFirestore()

    state_message = _state({"state": "3"})
    record_chunk = [_record(stream, str(i), i) for i in range(1, 3)]

    output_states = list(destination.write(config, configured_catalog, [*record_chunk, state_message]))
    assert [state_message] == output_states

    records_in_destination = retrieve_all_records(writer.client)

    expected_records = [_record(stream, str(i), i) for i in range(1, 3)]
    assert expected_records == records_in_destination


def test_write_overwrite(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, writer: FirestoreWriter):
    """
    This test verifies that writing a stream in "overwrite" overwrite all exiting ones
    """
    stream = configured_catalog.streams[1].stream.name
    destination = DestinationFirestore()

    state_message = _state({"state": "3"})

    list(destination.write(config, configured_catalog, [*[_record(stream, str(i), i) for i in range(1, 3)], state_message]))

    record_chunk = [_record(stream, str(i), i) for i in range(5, 10)]
    list(destination.write(config, configured_catalog, [*record_chunk, state_message]))

    records_in_destination = retrieve_all_records(writer.client)

    expected_records = [_record(stream, str(i), i) for i in range(5, 10)]
    assert expected_records == records_in_destination
