# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import logging
import os
import shutil
import time
import uuid
import zipfile
from io import StringIO
from pathlib import Path
from typing import Any, Mapping, Tuple

import docker
import paramiko
import pytest

from airbyte_cdk import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode

from .utils import get_docker_ip, load_config


logger = logging.getLogger("airbyte")

PRIVATE_KEY = str()
TMP_FOLDER = "/tmp/test_sftp_source"


# HELPERS
def generate_ssh_keys() -> Tuple[str, str]:
    key = paramiko.RSAKey.generate(2048)
    privateString = StringIO()
    key.write_private_key(privateString)

    return privateString.getvalue(), "ssh-rsa " + key.get_base64()


@pytest.fixture(scope="session")
def docker_client() -> docker.client.DockerClient:
    return docker.from_env()


def prepare_test_files(tmp_path: str | Path):
    """
    Fixture to prepare test files by unzipping a base CSV file and replicating it with different names.
    """
    tmp_path = Path(tmp_path)
    base_zip_path = tmp_path / "file_transfer/file_transfer_base.csv.zip"  # Path to the pre-created ZIP file
    extracted_path = tmp_path / "file_transfer"
    os.makedirs(extracted_path, exist_ok=True)

    # Step 1: Extract the base CSV file from the ZIP archive
    with zipfile.ZipFile(base_zip_path, "r") as zip_ref:
        zip_ref.extractall(extracted_path)

    base_file_path = extracted_path / "file_transfer_base.csv"
    file_names = [
        "file_transfer_1.csv",
        "file_transfer_2.csv",
        "file_transfer_3.csv",
        "file_transfer_4.csv",
        "file_transfer_5.csv",
    ]

    # Step 2: Create duplicates with different names
    for file_name in file_names:
        shutil.copy(base_file_path, extracted_path / file_name)


@pytest.fixture(scope="session", autouse=True)
def connector_setup_fixture(docker_client) -> None:
    ssh_path = TMP_FOLDER + "/ssh"
    dir_path = os.path.dirname(__file__)
    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)

    shutil.copytree(f"{dir_path}/files", TMP_FOLDER)
    prepare_test_files(TMP_FOLDER)
    os.makedirs(ssh_path)
    private_key, public_key = generate_ssh_keys()
    global PRIVATE_KEY
    PRIVATE_KEY = private_key
    pub_key_path = ssh_path + "/id_rsa.pub"
    with open(pub_key_path, "w") as f:
        f.write(public_key)
    config = load_config("config_password.json")
    container = docker_client.containers.run(
        "atmoz/sftp",
        f"{config['username']}:{config['credentials']['password']}",
        name=f"mysftp_integration_{uuid.uuid4().hex}",
        ports={22: ("0.0.0.0", config["port"])},
        volumes={
            f"{TMP_FOLDER}": {"bind": "/home/foo/files", "mode": "rw"},
            f"{pub_key_path}": {"bind": "/home/foo/.ssh/keys/id_rsa.pub", "mode": "ro"},
        },
        detach=True,
    )
    time.sleep(10)

    yield

    container.kill()
    container.remove()


@pytest.fixture(name="config", scope="session")
def config_fixture(docker_client) -> Mapping[str, Any]:
    config = load_config("config_password.json")
    config["host"] = get_docker_ip()
    yield config


@pytest.fixture(name="config_fixture_use_file_transfer", scope="session")
def config_fixture_use_file_transfer(docker_client) -> Mapping[str, Any]:
    config = load_config("config_use_file_transfer.json")
    config["host"] = get_docker_ip()
    yield config


@pytest.fixture(name="config_fixture_use_all_files_transfer", scope="session")
def config_fixture_use_all_files_transfer(docker_client) -> Mapping[str, Any]:
    config = load_config("config_use_all_files_transfer.json")
    config["host"] = get_docker_ip()
    yield config


@pytest.fixture(name="config_private_key", scope="session")
def config_fixture_private_key(docker_client) -> Mapping[str, Any]:
    config = load_config("config_private_key.json") | {
        "credentials": {"auth_type": "private_key", "private_key": PRIVATE_KEY},
    }
    config["host"] = get_docker_ip()
    yield config


@pytest.fixture(name="config_private_key_csv", scope="session")
def config_fixture_private_key_csv(config_private_key) -> Mapping[str, Any]:
    yield config_private_key


@pytest.fixture(name="config_password_all_csv", scope="session")
def config_fixture_password_all_csv(config) -> Mapping[str, Any]:
    yield config | load_config("stream_csv.json")


@pytest.fixture(name="config_password_all_jsonl", scope="session")
def config_fixture_password_all_jsonl(config) -> Mapping[str, Any]:
    yield config | load_config("stream_jsonl.json")


@pytest.fixture(name="config_password_all_excel_xlsx", scope="session")
def config_fixture_password_all_excel_xlsx(config) -> Mapping[str, Any]:
    yield config | load_config("stream_excel_xlsx.json")


@pytest.fixture(name="config_password_all_excel_xls", scope="session")
def config_fixture_password_all_excel_xls(config) -> Mapping[str, Any]:
    yield config | load_config("stream_excel_xls.json")


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
