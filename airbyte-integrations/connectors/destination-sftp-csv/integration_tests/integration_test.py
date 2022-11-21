#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import time
from socket import socket
from typing import Any, Dict, List, Mapping

import docker
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
from destination_sftp_csv import DestinationSftpCsv
from destination_sftp_csv.client import SFTPClient


@pytest.fixture(scope="module")
def docker_client():
    return docker.from_env()


@pytest.fixture(name="config", scope="module")
def config_fixture(docker_client):
    with socket() as s:
        s.bind(("", 0))
        available_port = s.getsockname()[1]

    config = {"host": "0.0.0.0", "port": available_port, "username": "foo", "password": "pass", "destination_path": "upload"}
    container = docker_client.containers.run(
        "atmoz/sftp",
        f"{config['username']}:{config['password']}:::{config['destination_path']}",
        name="mysftp",
        ports={22: config["port"]},
        detach=True,
    )
    time.sleep(20)
    yield config
    container.kill()
    container.remove()


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
def client_fixture(config, configured_catalog) -> SFTPClient:
    client = _get_connection(**config)
    client.connect()
    for stream in configured_catalog.streams:
        client.delete(stream.stream.name)

def _get_connection(self, config: Mapping[str, Any]) -> SFTPClient:
    return SFTPClient(
        host=config["host"],
        username=config["username"],
        destination_path=config.get("destination_path", "/"),
        password=config.get("password", None),
        private_key=config.get("private_key", None),
        port=config["port"],
    )

def test_check_valid_config(config: Mapping):
    outcome = DestinationSftpCsv().check(AirbyteLogger(), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config(config):
    outcome = DestinationSftpCsv().check(AirbyteLogger(), {**config, "destination_path": "/doesnotexist"})
    assert outcome.status == Status.FAILED

