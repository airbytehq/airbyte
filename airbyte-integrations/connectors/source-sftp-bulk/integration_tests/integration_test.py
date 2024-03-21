#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
import os
import shutil
import time
from io import StringIO
from socket import socket
from typing import Mapping, Any

import docker
import paramiko
import pytest
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, Status, SyncMode, Type
from source_sftp_bulk import SourceSFTPBulk

# pytest_plugins = ("connector_acceptance_test.plugin",)

logger = logging.getLogger("airbyte")

TMP_FOLDER = "/tmp/test_sftp_source"


# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(f"{os.path.dirname(__file__)}/{config_path}", "r") as config:
        return json.load(config)


def generate_ssh_keys():
    key = paramiko.RSAKey.generate(2048)
    privateString = StringIO()
    key.write_private_key(privateString)

    return privateString.getvalue(), "ssh-rsa " + key.get_base64()


@pytest.fixture(scope="session")
def docker_client():
    return docker.from_env()


@pytest.fixture(name="config", scope="session")
def config_fixture(docker_client):
    with socket() as s:
        s.bind(("", 0))
        available_port = s.getsockname()[1]

    dir_path = os.getcwd()

    config = load_config('config_password.json') | {"port": available_port}

    container = docker_client.containers.run(
        "atmoz/sftp",
        f"{config['username']}:{config['credentials']['password']}",
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


@pytest.fixture(name="config_private_key", scope="session")
def config_fixture_private_key(docker_client):
    with socket() as s:
        s.bind(("", 0))
        available_port = s.getsockname()[1]

    ssh_path = TMP_FOLDER + "/ssh"
    dir_path = os.getcwd()

    if os.path.exists(ssh_path):
        shutil.rmtree(ssh_path)

    os.makedirs(ssh_path)

    private_key, public_key = generate_ssh_keys()

    pub_key_path = ssh_path + "/id_rsa.pub"
    with open(pub_key_path, "w") as f:
        f.write(public_key)

    config = load_config("config_private_key.json") | {"port": available_port, "credentials": {
        "auth_type": "private_key",
        "private_key": private_key
    }}

    container = docker_client.containers.run(
        "atmoz/sftp",
        f"{config['username']}:{config['credentials'].get('password', 'pass')}:1001",
        name="mysftpssh",
        ports={22: config["port"]},
        volumes={
            f"{dir_path}/files": {"bind": "/home/foo/files", "mode": "rw"},
            f"{pub_key_path}": {"bind": "/home/foo/.ssh/keys/id_rsa.pub", "mode": "ro"},
        },
        detach=True,
    )

    time.sleep(20)
    yield config

    shutil.rmtree(ssh_path)
    container.kill()
    container.remove()


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {
            "_ab_source_file_last_modified": {
                "type": "string"
            },
            "_ab_source_file_url": {
                "type": "string"
            },
            "f0": {
                "type": ["null", "string"]
            },
            "f1": {
                "type": ["null", "string"]
            }
        }
    }

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="test_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])


def test_check_invalid_private_key_config(configured_catalog: ConfiguredAirbyteCatalog, config_private_key: Mapping[str, Any]):
    invalid_config = config_private_key | {"credentials": {
        "auth_type": "private_key",
        "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\nbaddata\n-----END OPENSSH PRIVATE KEY-----"
    }}
    outcome = SourceSFTPBulk(
        catalog=configured_catalog,
        config=invalid_config,
        state=None
    ).check(logger, invalid_config)
    assert outcome.status == Status.FAILED


def test_check_invalid_config(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]):
    config['credentials']['password'] = 'wrongpass'
    outcome = SourceSFTPBulk(
        catalog=configured_catalog,
        config=config,
        state=None
    ).check(logger, config)
    assert outcome.status == Status.FAILED


def test_check_valid_config(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]):
    outcome = SourceSFTPBulk(
        catalog=configured_catalog,
        config=config,
        state=None
    ).check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_get_files_no_pattern_json(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]):
    source = SourceSFTPBulk(
        catalog=configured_catalog,
        config=config,
        state=None
    )
    result_iter = source.read(logger, config, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_json(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(logger, {**config, "file_pattern": "test_1.+"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 1
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] == "foo"
        assert res.record.data["int_col"] == 2


def test_get_files_pattern_json_new_separator(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(logger, {**config, "file_pattern": "test_2.+"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 1
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] == "hello"
        assert res.record.data["int_col"] == 1


def test_get_files_pattern_no_match_json(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result = source.read(logger, {**config, "file_pattern": "bad_pattern.+"}, configured_catalog, None)
    assert len(list(result)) == 0


def test_get_files_no_pattern_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(logger, {**config, "file_type": "csv", "folder_path": "files/csv"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 4
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(
        logger, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "test_1.+"}, configured_catalog, None
    )
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv_new_separator(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(
        logger, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "test_2.+"}, configured_catalog, None
    )
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv_new_separator_with_config(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(
        logger,
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
    source = SourceSFTPBulk()
    result = source.read(
        logger, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "badpattern.+"}, configured_catalog, None
    )
    assert len(list(result)) == 0


def test_get_files_empty_files(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result = source.read(logger, {**config, "folder_path": "files/empty"}, configured_catalog, None)
    assert len(list(result)) == 0


def test_get_files_handle_null_values(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(logger, {**config, "folder_path": "files/null_values", "file_type": "csv"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 5

    res = result[2]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] == "bar"
    assert res.record.data["int_col"] is None

    res = result[4]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] is None
    assert res.record.data["int_col"] == 4
