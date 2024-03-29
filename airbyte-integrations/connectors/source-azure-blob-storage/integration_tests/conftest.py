# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import os
import platform
import subprocess
import time
import uuid
from typing import Any, Mapping

import azure
import docker
import pytest
from airbyte_protocol.models import ConfiguredAirbyteCatalog
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.storage.blob._shared.authentication import SharedKeyCredentialPolicy
from source_azure_blob_storage import SourceAzureBlobStorage

from .utils import get_docker_ip, load_config

logger = logging.getLogger("airbyte")


def _format_shared_key_credential(account_name, credential):
    credentials = {'account_key': 'key1', 'account_name': 'account1'}
    return SharedKeyCredentialPolicy(**credentials)


azure.storage.blob._shared.base_client._format_shared_key_credential = _format_shared_key_credential


@pytest.fixture(scope="session")
def docker_client() -> docker.client.DockerClient:
    return docker.from_env()


# @pytest.fixture()
def get_container_client() -> ContainerClient:
    docker_ip = get_docker_ip()
    # blob_service_client = BlobServiceClient(f'http://localhost:10000/account1', credential='key1')
    blob_service_client = BlobServiceClient(f'http://{docker_ip}:10000/account1', credential='key1')
    container_client = blob_service_client.get_container_client('testcontainer')
    return container_client


def generate_random_csv_with_source_faker():
    """Generate csv files using source-faker and save output to folder: /tmp/csv"""
    subprocess.run(f'{os.path.dirname(__file__)}/csv_export/main.sh')
    subprocess.run(['ls', '-lah', '/tmp/csv'])
    subprocess.run(['tail', '-10', '/tmp/csv/products.csv'])


@pytest.fixture(scope="session", autouse=True)
def connector_setup_fixture(docker_client) -> None:
    # TODO: fix to make it work with dagger and not save
    generate_random_csv_with_source_faker()
    container = docker_client.containers.run(
        image="mcr.microsoft.com/azure-storage/azurite",
        command="azurite-blob --blobHost 0.0.0.0 -l /data --loose",
        name=f"azurite_integration_{uuid.uuid4().hex}",
        hostname="azurite",
        ports={10000: ("0.0.0.0", 10000),
               10001: ("0.0.0.0", 10001),
               10002: ("0.0.0.0", 10002)},
        environment={"AZURITE_ACCOUNTS": "account1:key1"},
        detach=True,
    )
    time.sleep(10)
    container_client = get_container_client()
    container_client.create_container()

    generate_and_upload_files(container_client)

    yield

    container.kill()
    container.remove()


def generate_and_upload_files(container_client):
    """create container and upload 1000 csv"""

    # TODO: change to /tmp/csv folder
    # generate files of different types
    for table in ("products", "purchases", "users"):
        csv_large_file = open(f'/tmp/csv/{table}.csv', "rb").read()
        for i in range(10):
            container_client.upload_blob(f'test_csv_{table}_{i}.csv', csv_large_file, validate_content=False)
            print('big csv file uploaded _i', i)


@pytest.fixture(name='configured_catalog_csv')
def configured_catalog_csv_fixture() -> ConfiguredAirbyteCatalog:
    return SourceAzureBlobStorage.read_catalog(f'{os.path.dirname(__file__)}/integration_configured_catalog/csv.json')


@pytest.fixture(name="config_csv", scope="session")
def config_csv_fixture() -> Mapping[str, Any]:
    config = load_config("config_integration.json")
    config["azure_blob_storage_endpoint"] = config["azure_blob_storage_endpoint"].replace('localhost', get_docker_ip())
    yield config
