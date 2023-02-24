#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.utils import Connector
from dagger.api.gen import Container

PYPROJECT_TOML_FILE_PATH = "pyproject.toml"

DOCKER_IMAGE = "python:3.9-slim"
REQUIREMENTS = [
    "pip==21.3.1",
    "mccabe==0.6.1",
    "flake8==4.0.1",
    "pyproject-flake8==0.0.1a2",
    "black==22.3.0",
    "isort==5.6.4",
    "pytest==6.2.5",
    "coverage[toml]==6.3.1",
    "pytest-custom_exit_code",
]


def get_build_context(client, connector: Connector) -> Container:
    connector_code_directory = client.host().directory(connector.code_directory, exclude=[".venv"])
    pyproject_toml_file = client.host().directory().file(PYPROJECT_TOML_FILE_PATH)
    return (
        client.container()
        .from_(DOCKER_IMAGE)
        .with_exec(["pip", "install"] + REQUIREMENTS)
        .with_file(f"/{PYPROJECT_TOML_FILE_PATH}", pyproject_toml_file)
        .with_mounted_directory(connector.code_directory[1:], connector_code_directory)
        .workdir(connector.code_directory[1:])
    )
