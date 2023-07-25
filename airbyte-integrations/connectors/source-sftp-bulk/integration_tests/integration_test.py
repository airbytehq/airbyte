#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
import shutil
import time
from io import StringIO
from socket import socket
from typing import Mapping

import docker
import paramiko
import pytest
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, Status, SyncMode, Type
from source_sftp_bulk import SourceFtp

pytest_plugins = ("connector_acceptance_test.plugin",)

logger = logging.getLogger("airbyte")


def generate_ssh_keys():
    key = paramiko.RSAKey.generate(2048)
    privateString = StringIO()
    key.write_private_key(privateString)

    return privateString.getvalue(), "ssh-rsa " + key.get_base64()


@pytest.fixture(scope="session")
def docker_client():
    return docker.from_env()


@pytest.fixture(scope="session")
def path_to_mount_to_sftp(tmp_path_factory):
    """
    Copy the integration_test/files folder to a tmp dir which is shared with the docker host.
    """
    path = tmp_path_factory.mktemp("sftp_files")
    shutil.copytree(f"{os.getcwd()}/integration_tests/files", path, dirs_exist_ok=True)
    return path


@pytest.fixture(scope="session")
def key_pair():
    return generate_ssh_keys()


@pytest.fixture(scope="session")
def public_key(key_pair):
    return key_pair[1]


@pytest.fixture(scope="session")
def private_key(key_pair):
    return key_pair[0]


@pytest.fixture(scope="session")
def public_key_path(tmp_path_factory, public_key):
    public_key_path = tmp_path_factory.mktemp("ssh") / "id_rsa.pub"
    public_key_path.write_text(public_key)
    return public_key_path


@pytest.fixture(name="config", scope="session")
def config_fixture(docker_client, docker_ip, path_to_mount_to_sftp):
    with socket() as s:
        s.bind(("", 0))
        available_port = s.getsockname()[1]

    config = {
        "host": docker_ip,
        "port": available_port,
        "username": "foo",
        "password": "pass",
        "file_type": "json",
        "start_date": "2021-01-01T00:00:00Z",
        "folder_path": "/files",
        "stream_name": "overwrite_stream",
    }

    try:

        container = docker_client.containers.run(
            "atmoz/sftp",
            f"{config['username']}:{config['password']}",
            name="mysftp",
            ports={22: config["port"]},
            volumes={
                path_to_mount_to_sftp: {"bind": "/home/foo/files", "mode": "rw"},
            },
            detach=True,
        )

        time.sleep(20)
        yield config
    finally:
        container.kill()
        container.remove()


@pytest.fixture(name="config_pk", scope="session")
def config_fixture_pk(docker_client, docker_ip, public_key_path, private_key, path_to_mount_to_sftp):

    with socket() as s:
        s.bind(("", 0))
        available_port = s.getsockname()[1]

    config = {
        "host": docker_ip,
        "port": available_port,
        "username": "foo",
        "password": "pass",
        "file_type": "json",
        "private_key": private_key,
        "start_date": "2021-01-01T00:00:00Z",
        "folder_path": "/files",
        "stream_name": "overwrite_stream",
    }

    try:
        container = docker_client.containers.run(
            "atmoz/sftp",
            f"{config['username']}:{config['password']}:1001",
            name="mysftpssh",
            ports={22: config["port"]},
            volumes={
                path_to_mount_to_sftp: {"bind": "/home/foo/files", "mode": "rw"},
                public_key_path: {"bind": "/home/foo/.ssh/keys/id_rsa.pub", "mode": "ro"},
            },
            detach=True,
        )

        time.sleep(20)
        yield config
    finally:
        container.kill()
        container.remove()


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}},
    }

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="overwrite_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])


def _read_records(source, config, catalog, state=None):
    return [m for m in list(source.read(logger, config, catalog, state)) if m.type == Type.RECORD]


def test_check_valid_config_pk(config_pk: Mapping):
    outcome = SourceFtp().check(logger, config_pk)
    assert outcome.status == Status.SUCCEEDED


def test_check_valid_config_pk_bad_pk(config_pk: Mapping):
    outcome = SourceFtp().check(
        logger, {**config_pk, "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\nbaddata\n-----END OPENSSH PRIVATE KEY-----"}
    )
    assert outcome.status == Status.FAILED


def test_check_invalid_config(config: Mapping):
    outcome = SourceFtp().check(logger, {**config, "password": "wrongpass"})
    assert outcome.status == Status.FAILED


def test_check_valid_config(config: Mapping):
    outcome = SourceFtp().check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_get_files_no_pattern_json(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = _read_records(source, config, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_json(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = _read_records(source, {**config, "file_pattern": "test_1.+"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 1
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] == "foo"
        assert res.record.data["int_col"] == 2


def test_get_files_pattern_json_new_separator(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = _read_records(source, {**config, "file_pattern": "test_2.+"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 1
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] == "hello"
        assert res.record.data["int_col"] == 1


def test_get_files_pattern_no_match_json(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result = _read_records(source, {**config, "file_pattern": "bad_pattern.+"}, configured_catalog, None)
    assert len(list(result)) == 0


def test_get_files_no_pattern_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = _read_records(source, {**config, "file_type": "csv", "folder_path": "files/csv"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 4
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = _read_records(
        source, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "test_1.+"}, configured_catalog, None
    )

    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv_new_separator(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = _read_records(
        source, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "test_2.+"}, configured_catalog, None
    )
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv_new_separator_with_config(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result_iter = _read_records(
        source,
        {**config, "file_type": "csv", "folder_path": "files/csv", "separator": ";", "file_pattern": "test_2.+"},
        configured_catalog,
        None,
    )
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_no_match_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result = _read_records(
        source, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "badpattern.+"}, configured_catalog, None
    )
    assert len(list(result)) == 0


def test_get_files_empty_files(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result = _read_records(source, {**config, "folder_path": "files/empty"}, configured_catalog, None)
    assert len(list(result)) == 0


def test_get_files_handle_null_values(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceFtp()
    result = _read_records(source, {**config, "folder_path": "files/null_values", "file_type": "csv"}, configured_catalog, None)
    assert len(result) == 5

    res = result[2]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] == "bar"
    assert res.record.data["int_col"] is None

    res = result[4]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] is None
    assert res.record.data["int_col"] == 4
