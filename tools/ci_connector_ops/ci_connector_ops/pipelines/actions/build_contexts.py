#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.utils import Connector
from dagger import CacheVolume, Client, Container, Directory

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
]


def get_build_context(dagger_client: Client, connector: Connector) -> Container:
    """Create a Python container in which the connector source code will be mounted alongside with the pyproject.toml.
    We install the dependency required for our testing tools: formatting, unit tests, pip etc.
    The pyproject.toml file gathers configurations for the formatting and testing tools eventually used downstream.

    Args:
        client (Client): The dagger client to use.
        connector (Connector): The connector for which the build context is created.

    Returns:
        Container: A container with a ready to use build context: connector source code and required artifacts are mounted.
    """
    connector_code_path = str(connector.code_directory)
    connector_code_directory: Directory = dagger_client.host().directory(connector_code_path, exclude=[".venv"])
    pyproject_toml_file = dagger_client.host().directory(".", include=[PYPROJECT_TOML_FILE_PATH]).file(PYPROJECT_TOML_FILE_PATH)
    pip_cache: CacheVolume = dagger_client.cache_volume("pip_cache")
    return (
        dagger_client.container()
        .from_(DOCKER_IMAGE)
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(["pip", "install"] + REQUIREMENTS)
        .with_file(f"/{PYPROJECT_TOML_FILE_PATH}", pyproject_toml_file)
        .with_mounted_directory("/" + connector_code_path, connector_code_directory)
        .with_workdir("/" + connector_code_path)
    )
