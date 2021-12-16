#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os.path
import shutil
import tempfile
from zipfile import ZipFile

import docker
import pytest
from airbyte_cdk import AirbyteLogger

pytest_plugins = ("source_acceptance_test.plugin",)
logger = AirbyteLogger()
TMP_FOLDER = tempfile.mkdtemp()


def minio_setup():
    with ZipFile("./integration_tests/minio_data.zip") as archive:
        archive.extractall(TMP_FOLDER)
    client = docker.from_env()
    minio_container = None
    for container in client.containers.list():
        if container.name == "ci_test_minio":
            minio_container = container
            logger.info("minio was started before")
            break
    if not minio_container:
        container = client.containers.run(
            "minio/minio",
            f"server {TMP_FOLDER}",
            name="ci_test_minio",
            auto_remove=True,
            volumes=[f"/{TMP_FOLDER}/minio_data:/{TMP_FOLDER}"],
            detach=True,
            ports={"9000/tcp": ("127.0.0.1", 9000)},
        )
        logger.info("Run a minio/minio container")
    yield
    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)
    container.stop()


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    yield from minio_setup()
