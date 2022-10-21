#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import shutil
import time

import docker
import pytest

pytest_plugins = ("source_acceptance_test.plugin",)

TMP_FOLDER = "/tmp/test_sftp_source"


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    dir_path = os.getcwd() + "/integration_tests/files"

    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)
    shutil.copytree(dir_path, TMP_FOLDER)

    docker_client = docker.from_env()

    container = docker_client.containers.run(
        "atmoz/sftp",
        "foo:pass",
        name="mysftpacceptance",
        ports={22: 22},
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
