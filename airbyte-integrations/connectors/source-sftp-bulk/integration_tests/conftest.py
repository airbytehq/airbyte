# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import json
import logging
import os
import shutil
import time
from io import StringIO
from socket import socket
from typing import Any, Mapping

import docker
import paramiko
import pytest
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode

logger = logging.getLogger("airbyte")

TMP_FOLDER = "/tmp/test_sftp_source"


# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(f"{os.path.dirname(__file__)}/configs/{config_path}", "r") as config:
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

    config = load_config("config_password.json") | {"port": available_port}

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

    config = load_config("config_private_key.json") | {
        "port": available_port,
        "credentials": {"auth_type": "private_key", "private_key": private_key},
    }

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


@pytest.fixture(name="config_private_key_csv", scope="session")
def config_fixture_private_key_csv(config_private_key):
    yield config_private_key


@pytest.fixture(name="config_password_all_csv", scope="session")
def config_fixture_password_all_csv(config):
    yield config | load_config("stream_csv.json")


@pytest.fixture(name="config_password_all_jsonl", scope="session")
def config_fixture_password_all_jsonl(config):
    yield config | load_config("stream_jsonl.json")


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {
            "_ab_source_file_last_modified": {"type": "string"},
            "_ab_source_file_url": {"type": "string"},
            "string_col": {"type": ["null", "string"]},
            "int_col": {"type": ["null", "integer"]},
        },
    }

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="test_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])
