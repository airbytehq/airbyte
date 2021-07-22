# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
from typing import Any, Dict, List, Mapping
from unittest import mock

import pytest
from airbyte_cdk import AirbyteLogger
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
from destination_sftp_json import DestinationSftpJson
from destination_sftp_json.client import SftpClient


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog", params=["append", "overwrite"])
def configured_catalog_fixture(request) -> ConfiguredAirbyteCatalog:
    stream_schema = {}
    destination_sync_mode = request.param
    mode = getattr(DestinationSyncMode, destination_sync_mode)
    stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=f"{destination_sync_mode}_stream", json_schema=stream_schema
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=mode,
    )
    return ConfiguredAirbyteCatalog(streams=[stream])


@pytest.fixture(name="client")
def client_fixture(config) -> SftpClient:
    # with mock.patch("patchramiko.SSHClient"), mock.patch("smart_open.open"):
    client = SftpClient(**config)
    yield client
    client.delete()
    client.close()


def test_check_valid_config(config: Mapping):
    outcome = DestinationSftpJson().check(AirbyteLogger(), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config(config):
    outcome = DestinationSftpJson().check(
        AirbyteLogger(), {**config, "destination_path": "/doesnotexist"}
    )
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, value: Any) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream=stream, data={"data": value}, emitted_at=0),
    )


def test_write(
    config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, client: SftpClient
):
    """
    This test verifies that:
        1. writing a stream in "overwrite" mode overwrites any existing data for that stream
        2. writing a stream in "append" mode appends new records without deleting the old ones
        3. The correct state message is output by the connector at the end of the sync
    """
    stream = configured_catalog.streams[0].stream.name
    overwrite = "overwrite" in stream
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_record(stream, i) for i in range(5)]

    second_state_message = _state({"state": "2"})
    second_record_chunk = [_record(stream, i) for i in range(5, 10)]

    destination = DestinationSftpJson()

    expected_states = [first_state_message, second_state_message]
    output_states = list(
        destination.write(
            config,
            configured_catalog,
            [
                *first_record_chunk,
                first_state_message,
                *second_record_chunk,
                second_state_message,
            ],
        )
    )
    assert (
        expected_states == output_states
    ), "Checkpoint state messages were expected from the destination"

    expected_records = [_record(stream, i) for i in range(10)]
    records_in_destination = [
        _record(stream, line["data"]) for line in client.read_data()
    ]
    assert (
        expected_records == records_in_destination
    ), "Records in destination should match records expected"

    # After this sync we expect the append stream to have 15 messages and the overwrite stream to have 5
    third_state_message = _state({"state": "3"})
    third_record_chunk = [_record(stream, i) for i in range(10, 15)]

    # Need to close the file so the destination can flush the buffer
    client.close()

    output_states = list(
        destination.write(
            config, configured_catalog, [*third_record_chunk, third_state_message]
        )
    )
    assert [third_state_message] == output_states

    records_in_destination = [
        _record(stream, line["data"]) for line in client.read_data()
    ]
    expected_range = range(10, 15) if overwrite else range(15)
    expected_records = [_record(stream, i) for i in expected_range]
    assert expected_records == records_in_destination
