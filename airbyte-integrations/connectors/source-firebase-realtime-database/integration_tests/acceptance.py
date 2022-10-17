#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import os
from pathlib import Path

import docker
import pytest

pytest_plugins = ("source_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    client = docker.from_env()
    integration_tests_dir = Path(os.path.dirname(__file__))
    secrets_dir = integration_tests_dir.parent / "secrets"

    with open(secrets_dir / "config.json") as f:
        secrets = json.load(f)
        database_name = secrets["database_name"]

    client.containers.run(
        "gcr.io/google.com/cloudsdktool/google-cloud-cli",
        "/integration_tests/setup_data.sh",
        auto_remove=True,
        environment={"DB_NAME": database_name},
        volumes={
            str(integration_tests_dir): {
                "bind": "/integration_tests",
                "mode": "rw",
            },
            str(secrets_dir): {
                "bind": "/secrets",
                "mode": "rw",
            },
        },
    )

    yield

    client.containers.run(
        "gcr.io/google.com/cloudsdktool/google-cloud-cli",
        "/integration_tests/teardown.sh",
        auto_remove=True,
        environment={"DB_NAME": database_name},
        volumes={
            str(integration_tests_dir): {
                "bind": "/integration_tests",
                "mode": "rw",
            },
            str(secrets_dir): {
                "bind": "/secrets",
                "mode": "rw",
            },
        },
    )
