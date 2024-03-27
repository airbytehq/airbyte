import logging
import os

import docker
from azure.storage.blob import BlobServiceClient

import pytest
import time

from .utils import get_docker_ip, load_config

logger = logging.getLogger("airbyte")


@pytest.fixture(scope="session")
def docker_client() -> docker.client.DockerClient:
    return docker.from_env()


@pytest.fixture(scope="session", autouse=True)
def connector_setup_fixture(docker_client) -> None:
    container = docker_client.containers.run(
        image="mcr.microsoft.com/azure-storage/azurite",
        command="azurite-blob --blobHost 0.0.0.0 -l /data --loose",
        name="azurite_test",
        hostname="azurite",
        ports={10000: ("0.0.0.0", 10000),
               10001: ("0.0.0.0", 10001),
               10002: ("0.0.0.0", 10002)},
        environment={"AZURITE_ACCOUNTS": "account1:key1"},
        volumes={
            f"{os.path.dirname(__file__)}/files": {"bind": "/files", "mode": "rw"},
        },
        detach=True,
    )
    time.sleep(5)
    # create container and upload 1000 csv
    blob_service_client = BlobServiceClient('http://localhost:10000/account1', credential='key1')
    container_client = blob_service_client.get_container_client('testcontainer')
    container_client.create_container()
    started_at = time.time()
    print('=' * 40, f"started at: {started_at}")
    csv_data = open(
                '/Users/artem.inzhyyants/PycharmProjects/airbyte/airbyte-integrations/connectors/source-azure-blob-storage/integration_tests/data/test_1.csv',
                "rb").read()
    for i in range(1000):
        container_client.upload_blob(f'test_{i}.csv', csv_data, validate_content=False)
        print('file uploaded', i)

    finished_at = time.time()
    print('=' * 40, f"finished at: {finished_at}")
    print('=' * 40, f"elapsed: {finished_at - started_at}")
    yield

    container.kill()
    container.remove()
