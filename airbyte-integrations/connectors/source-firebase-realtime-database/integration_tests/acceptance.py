#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
import tarfile
from pathlib import Path

import docker
import pytest


pytest_plugins = ("source_acceptance_test.plugin",)


def create_setup_container(client):
    integration_tests_dir = Path(os.path.dirname(__file__))
    secrets_dir = integration_tests_dir.parent / "secrets"

    with open(secrets_dir / "config.json") as f:
        secrets = json.load(f)
        database_name = secrets["database_name"]

    container = client.containers.create(
        image="gcr.io/google.com/cloudsdktool/google-cloud-cli",
        command="/bin/sh",
        auto_remove=True,
        detach=True,
        tty=True,
        environment={"DB_NAME": database_name},
    )

    # The setup container is a docker in docker container.
    # It is necessary to mount volumes by specifying the file path of the host
    # that runs the container that runs the setup container, but there is no way to specify that path,
    # so we should copy the files into the container.
    archive_path = "./setup_files.tar"
    try:
        with tarfile.open(archive_path, "w") as f:
            f.add(integration_tests_dir / "setup_data.sh", "setup_data.sh")
            f.add(integration_tests_dir / "teardown.sh", "teardown.sh")
            f.add(integration_tests_dir / "records.json", "records.json")
            f.add(secrets_dir / "firebase-admin.json", "firebase-admin.json")

        with open(archive_path, "rb") as f:
            data = f.read()
    finally:
        os.remove(archive_path)

    container.put_archive("/", data)

    container.start()

    return container


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    client = docker.from_env()
    container = create_setup_container(client)
    container.exec_run("/setup_data.sh")

    yield

    container.exec_run("/teardown.sh")
    container.stop()
