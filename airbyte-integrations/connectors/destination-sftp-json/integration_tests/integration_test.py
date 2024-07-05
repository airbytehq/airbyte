#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import logging
import time
from pathlib import Path
from socket import socket
from typing import Any, Dict, List, Mapping

import paramiko
import paramiko.client
import pytest
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


def is_sftp_ready(ip: str, port: str) -> bool:
    """
    Checks if sftp is served on provided ip address and port.
    """
    try:
        with paramiko.client.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            ssh.connect(
                ip,
                port=port,
                username="user1",
                password="abc123",
            )
        return True
    except paramiko.SSHException:
        return False


# NOTE: I'm not sure if specifying the docker-compose file is required or if it would be picked up automatically,
# but I've copied this approach from source-file.
@pytest.fixture(scope="session")
def docker_compose_file() -> Path:
    return Path(__file__).parent.absolute() / "docker-compose.yml"


@pytest.fixture(name="config", scope="module")
def config_fixture(docker_ip, docker_services):
    """
    Provides the SFTP configuration using docker_services.
    Waits for the docker container to become available before returning the config.
    """
    port = docker_services.port_for("sftp", 22)
    config = {"host": docker_ip, "port": port, "username": "user1", "password": "abc123", "destination_path": "upload"}
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_sftp_ready(docker_ip, port))
    return config


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}},
    }

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


@pytest.fixture(name="client")
def client_fixture(config, configured_catalog) -> SftpClient:
    with SftpClient(**config) as client:
        yield client
        for stream in configured_catalog.streams:
            client.delete(stream.stream.name)


def test_check_valid_config(config: Mapping):
    outcome = DestinationSftpJson().check(logging.getLogger("airbyte-destination"), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config(config):
    outcome = DestinationSftpJson().check(logging.getLogger("airbyte-destination"), {**config, "destination_path": "/doesnotexist"})
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteStateMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, str_value: str, int_value: int) -> AirbyteRecordMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream,
            data={"str_col": str_value, "int_col": int_value},
            emitted_at=0,
        ),
    )


def _sort(messages: List[AirbyteRecordMessage]) -> List[AirbyteRecordMessage]:
    return sorted(messages, key=lambda x: x.record.stream)


def retrieve_all_records(client: SftpClient, streams: List[str]) -> List[AirbyteRecordMessage]:
    """retrieves and formats all records on the SFTP server as Airbyte messages"""
    all_records = []
    for stream in streams:
        for data in client.read_data(stream):
            all_records.append((stream, data))
    out = []
    for stream, record in all_records:
        out.append(_record(stream, record["str_col"], record["int_col"]))
    return _sort(out)


def test_write(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, client: SftpClient):
    """
    This test verifies that:
        1. writing a stream in "overwrite" mode overwrites any existing data for that stream
        2. writing a stream in "append" mode appends new records without deleting the old ones
        3. The correct state message is output by the connector at the end of the sync
    """
    append_stream, overwrite_stream = (
        configured_catalog.streams[0].stream.name,
        configured_catalog.streams[1].stream.name,
    )
    streams = [append_stream, overwrite_stream]
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_record(append_stream, str(i), i) for i in range(5)] + [_record(overwrite_stream, str(i), i) for i in range(5)]

    second_state_message = _state({"state": "2"})
    second_record_chunk = [_record(append_stream, str(i), i) for i in range(5, 10)] + [
        _record(overwrite_stream, str(i), i) for i in range(5, 10)
    ]

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
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

    expected_records = [_record(append_stream, str(i), i) for i in range(10)] + [_record(overwrite_stream, str(i), i) for i in range(10)]
    records_in_destination = retrieve_all_records(client, streams)
    assert _sort(expected_records) == records_in_destination, "Records in destination should match records expected"

    # After this sync we expect the append stream to have 15 messages and the overwrite stream to have 5
    third_state_message = _state({"state": "3"})
    third_record_chunk = [_record(append_stream, str(i), i) for i in range(10, 15)] + [
        _record(overwrite_stream, str(i), i) for i in range(10, 15)
    ]

    output_states = list(destination.write(config, configured_catalog, [*third_record_chunk, third_state_message]))
    assert [third_state_message] == output_states

    records_in_destination = retrieve_all_records(client, streams)
    expected_records = [_record(append_stream, str(i), i) for i in range(15)] + [
        _record(overwrite_stream, str(i), i) for i in range(10, 15)
    ]
    assert _sort(expected_records) == records_in_destination
