#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import shutil
import tempfile
from zipfile import ZipFile

import docker
from airbyte_cdk import AirbyteLogger

pytest_plugins = ("source_acceptance_test.plugin",)
logger = AirbyteLogger()
TMP_FOLDER = tempfile.mkdtemp()


def minio_setup():
    with ZipFile("./integration_tests/minio_data.zip") as archive:
        archive.extractall(TMP_FOLDER)
    client = docker.from_env()
    for container in client.containers.list():
        if container.name == "ci_test_minio":
            container.stop()
            break

    container = client.containers.run(
        "minio/minio",
        f"server {TMP_FOLDER}",
        name="ci_test_minio",
        auto_remove=True,
        # network_mode="host",
        volumes=[f"/{TMP_FOLDER}/minio_data:/{TMP_FOLDER}", "/var/run/docker.sock:/var/run/docker.sock"],
        detach=True,
        ports={"9000/tcp": ("127.0.0.1", 9000)},
    )
    logger.info("Run a minio/minio container")
    yield
    shutil.rmtree(TMP_FOLDER)
    container.stop()
