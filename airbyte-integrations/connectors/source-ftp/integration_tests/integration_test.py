#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import time
import pytest
import docker
import logging

from socket import socket
from typing import Mapping

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, Type, Status

from source_ftp import SourceFtp

pytest_plugins = ("source_acceptance_test.plugin",)

logger = logging.getLogger("airbyte")


@pytest.fixture(scope="module")
def docker_client():
    return docker.from_env()


@pytest.fixture(name="config", scope="module")
def config_fixture(docker_client):
    with socket() as s:
        s.bind(("", 0))
        available_port = s.getsockname()[1]

    dir_path = os.getcwd() + "/integration_tests"

    config = {
        "host": "0.0.0.0",
        "port": available_port,
        "username": "foo",
        "password": "pass",
        "file_type": "json",
        "start_date": "2021-01-01T00:00:00Z",
        "folder_path": "/files",
        "stream_name": "overwrite_stream",
    }

    container = docker_client.containers.run(
        "atmoz/sftp",
        f"{config['username']}:{config['password']}",
        name="mysftp",
        ports={22: config["port"]},
        volumes={
            f"{dir_path}/files": {"bind": "/home/foo/files", "mode": "rw"},
        },
        detach=True,
    )

    time.sleep(20)
    yield config

    container.kill()
    container.remove()


@pytest.fixture(name="config_pk", scope="module")
def config_fixture_pk(docker_client):
    with socket() as s:
        s.bind(("", 0))
        available_port = s.getsockname()[1]

    dir_path = os.getcwd() + "/integration_tests"
    pk = open(f"{dir_path}/ssh/id_rsa", "r").read()

    config = {
        "host": "0.0.0.0",
        "port": available_port,
        "username": "foo",
        "password": "pass",
        "file_type": "json",
        "private_key": pk,
        "start_date": "2021-01-01T00:00:00Z",
        "folder_path": "/files",
        "stream_name": "overwrite_stream",
    }

    container = docker_client.containers.run(
        "atmoz/sftp",
        f"{config['username']}:{config['password']}:1001",
        name="mysftpssh",
        ports={22: config["port"]},
        volumes={
            f"{dir_path}/files": {"bind": "/home/foo/files", "mode": "rw"},
            f"{dir_path}/ssh/id_rsa.pub": {"bind": "/home/foo/.ssh/keys/id_rsa.pub", "mode": "ro"},
        },
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

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="overwrite_stream", json_schema=stream_schema),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])


def test_check_valid_config_pk(config_pk: Mapping):
    outcome = SourceFtp().check(logger, config_pk)
    assert outcome.status == Status.SUCCEEDED


def test_check_valid_config_pk_bad_pk(config_pk: Mapping):
    outcome = SourceFtp().check(logger, {**config_pk, "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\nbaddata\n-----END OPENSSH PRIVATE KEY-----"})
    assert outcome.status == Status.FAILED


def test_check_invalid_config(config: Mapping):
    outcome = SourceFtp().check(logger, {**config, "password": "wrongpass"})
    assert outcome.status == Status.FAILED


def test_check_valid_config(config: Mapping):
    outcome = SourceFtp().check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_get_files_no_pattern_json(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = source.read(logger, config, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_json(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = source.read(logger, {**config, "file_pattern": "test_1.+"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 1
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] == "foo"
        assert res.record.data["int_col"] == 2


def test_get_files_pattern_no_match_json(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result = source.read(logger, {**config, "file_pattern": "bad_pattern.+"}, configured_catalog, None)
    assert len(list(result)) == 0


def test_get_files_no_pattern_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = source.read(logger, {**config, "file_type": "csv", "folder_path": "files/csv"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = source.read(
        logger, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "test_1.+"}, configured_catalog, None
    )
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_no_match_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result = source.read(
        logger, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "badpattern.+"}, configured_catalog, None
    )
    assert len(list(result)) == 0


def test_get_files_empty_files(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result = source.read(logger, {**config, "folder_path": "files/empty"}, configured_catalog, None)
    assert len(list(result)) == 0


def test_get_files_handle_null_values(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = source.read(logger, {**config, "folder_path": "files/null_values", "file_type": "csv"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 5

    res = result[2]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] == "bar"
    assert res.record.data["int_col"] == None

    res = result[4]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] == None
    assert res.record.data["int_col"] == 4
