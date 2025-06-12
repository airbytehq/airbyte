#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Dict, List, Mapping

import pytest
from destination_databend import DestinationDatabend
from destination_databend.client import DatabendClient

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


@pytest.fixture(name="databendConfig")
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
def teardown(databendConfig: Mapping):
    yield
    client = DatabendClient(**databendConfig)
    cursor = client.open()
    cursor.close()


@pytest.fixture(name="client")
def client_fixture(databendConfig) -> DatabendClient:
    return DatabendClient(**databendConfig)


def test_check_valid_config(databendConfig: Mapping):
    outcome = DestinationDatabend().check(logging.getLogger("airbyte"), databendConfig)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationDatabend().check(logging.getLogger("airbyte"), {"bucket_id": "not_a_real_id"})
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, str_value: str, int_value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, "int_col": int_value}, emitted_at=0)
    )


def retrieve_records(stream_name: str, client: DatabendClient) -> List[AirbyteRecordMessage]:
    cursor = client.open()
    cursor.execute(f"select * from _airbyte_raw_{stream_name}")
    all_records = cursor.fetchall()
    out = []
    for record in all_records:
        # key = record[0]
        # stream = key.split("__ab__")[0]
        value = json.loads(record[2])
        out.append(_record(stream_name, value["str_col"], value["int_col"]))
    return out


def retrieve_all_records(client: DatabendClient) -> List[AirbyteRecordMessage]:
    """retrieves and formats all records in databend as Airbyte messages"""
    overwrite_stream = "overwrite_stream"
    append_stream = "append_stream"
    overwrite_out = retrieve_records(overwrite_stream, client)
    append_out = retrieve_records(append_stream, client)
    return overwrite_out + append_out


def test_write(databendConfig: Mapping, configured_catalog: ConfiguredAirbyteCatalog, client: DatabendClient):
    """
    This test verifies that:
        1. writing a stream in "overwrite" mode overwrites any existing data for that stream
        2. writing a stream in "append" mode appends new records without deleting the old ones
        3. The correct state message is output by the connector at the end of the sync
    """
    append_stream, overwrite_stream = configured_catalog.streams[0].stream.name, configured_catalog.streams[1].stream.name
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_record(append_stream, str(i), i) for i in range(5)] + [_record(overwrite_stream, str(i), i) for i in range(5)]

    second_state_message = _state({"state": "2"})
    second_record_chunk = [_record(append_stream, str(i), i) for i in range(5, 10)] + [
        _record(overwrite_stream, str(i), i) for i in range(5, 10)
    ]

    destination = DestinationDatabend()

    expected_states = [first_state_message, second_state_message]
    output_states = list(
        destination.write(
            databendConfig, configured_catalog, [*first_record_chunk, first_state_message, *second_record_chunk, second_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

    expected_records = [_record(append_stream, str(i), i) for i in range(10)] + [_record(overwrite_stream, str(i), i) for i in range(10)]
    records_in_destination = retrieve_all_records(client)
    assert len(expected_records) == len(records_in_destination), "Records in destination should match records expected"

    # After this sync we expect the append stream to have 15 messages and the overwrite stream to have 5
    third_state_message = _state({"state": "3"})
    third_record_chunk = [_record(append_stream, str(i), i) for i in range(10, 15)] + [
        _record(overwrite_stream, str(i), i) for i in range(10, 15)
    ]

    output_states = list(destination.write(databendConfig, configured_catalog, [*third_record_chunk, third_state_message]))
    assert [third_state_message] == output_states

    records_in_destination = retrieve_all_records(client)
    expected_records = [_record(append_stream, str(i), i) for i in range(15)] + [
        _record(overwrite_stream, str(i), i) for i in range(10, 15)
    ]
    assert len(expected_records) == len(records_in_destination)

    tear_down(client)


def tear_down(client: DatabendClient):
    overwrite_stream = "overwrite_stream"
    append_stream = "append_stream"
    cursor = client.open()
    cursor.execute(f"DROP table _airbyte_raw_{overwrite_stream}")
    cursor.execute(f"DROP table _airbyte_raw_{append_stream}")
