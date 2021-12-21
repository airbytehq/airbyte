#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os.path
import shutil
import tempfile
import time
from zipfile import ZipFile

import docker
import pytest
import requests
from airbyte_cdk import AirbyteLogger
from docker.errors import APIError
from requests.exceptions import ConnectionError

pytest_plugins = ("source_acceptance_test.plugin",)
logger = AirbyteLogger()
TMP_FOLDER = tempfile.mkdtemp()


def minio_setup():
    with ZipFile("./integration_tests/minio_data.zip") as archive:
        archive.extractall(TMP_FOLDER)
    client = docker.from_env()
    try:
        container = client.containers.run(
            image="minio/minio:RELEASE.2021-10-06T23-36-31Z",
            command=f"server {TMP_FOLDER}",
            name="ci_test_minio",
            auto_remove=True,
            volumes=[f"/{TMP_FOLDER}/minio_data:/{TMP_FOLDER}"],
            detach=True,
            # ports={"9000/tcp": ("127.0.0.1", 9000)},
            network_mode="host",
        )
    except APIError as err:
        if err.status_code == 409:
            for container in client.containers.list():
                if container.name == "ci_test_minio":
                    logger.info("minio was started before")
                    break
        else:
            raise

    check_url = "http://127.0.0.1:9000/minio/health/live"
    while True:
        try:
            data = requests.get(check_url)
        except ConnectionError as err:
            logger.warn(f"minio error: {err}")
            time.sleep(0.5)
            continue
        if data.status_code == 200:
            break
        logger.info("Run a minio/minio container...")
    yield

    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)
        logger.info("minio was stopped")
    container.stop()


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    yield from minio_setup()
