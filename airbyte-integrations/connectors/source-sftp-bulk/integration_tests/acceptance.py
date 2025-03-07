#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import os
import shutil
import time
import uuid

import docker
import pytest


pytest_plugins = ("connector_acceptance_test.plugin",)

TMP_FOLDER = "/tmp/test_sftp_source"


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)
    shutil.copytree(f"{os.path.dirname(__file__)}/files", TMP_FOLDER)
    docker_client = docker.from_env()
    container = docker_client.containers.run(
        "atmoz/sftp",
        "foo:pass",
        name=f"mysftp_acceptance_{uuid.uuid4().hex}",
        ports={22: ("0.0.0.0", 2222)},
        volumes={
            f"{TMP_FOLDER}": {"bind": "/home/foo/files", "mode": "rw"},
        },
        detach=True,
    )
    time.sleep(5)
    yield

    shutil.rmtree(TMP_FOLDER)
    container.kill()
    container.remove()
