#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

from ci_connector_ops.pipelines.utils import get_file_contents
from ci_connector_ops.utils import Connector
from dagger import CacheVolume, Client, Container, Directory

PYPROJECT_TOML_FILE_PATH = "pyproject.toml"

CONNECTOR_TESTING_REQUIREMENTS = [
    "pip==21.3.1",
    "mccabe==0.6.1",
    "flake8==4.0.1",
    "pyproject-flake8==0.0.1a2",
    "black==22.3.0",
    "isort==5.6.4",
    "pytest==6.2.5",
    "coverage[toml]==6.3.1",
]

INSTALL_LOCAL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
INSTALL_CONNECTOR_PACKAGE_CMD = ["python", "-m", "pip", "install", "."]
DEFAULT_PYTHON_EXCLUDE = [".venv"]
CI_CREDENTIALS_SOURCE_PATH = ["tools/ci_credentials"]


async def with_python_base(dagger_client: Client, python_image_name: str = "python:3.9-slim") -> Container:
    """Builds a Python container with a cache volume for pip cache.

    Args:
        dagger_client (Client): The dagger client to use.
        python_image_name (_type_, optional): The python image to use to build the python base environment. Defaults to "python:3.9-slim".

    Raises:
        ValueError: Raised if the python_image_name is not a python image.

    Returns:
        Container: The python base environment container.
    """
    if not python_image_name.startswith("python:3"):
        raise ValueError("You have to use a python image to build the python base environment")
    pip_cache: CacheVolume = dagger_client.cache_volume("pip_cache")
    return dagger_client.container().from_(python_image_name).with_mounted_cache("/root/.cache/pip", pip_cache)


async def with_testing_dependencies(dagger_client: Client) -> Container:
    """Builds a testing environment by installing testing dependencies on top of a python base environment.

    Args:
        dagger_client (Client): The dagger client.

    Returns:
        Container: The testing environment container.
    """
    python_environment: Container = await with_python_base(dagger_client)
    pyproject_toml_file = dagger_client.host().directory(".", include=[PYPROJECT_TOML_FILE_PATH]).file(PYPROJECT_TOML_FILE_PATH)
    return python_environment.with_exec(["pip", "install"] + CONNECTOR_TESTING_REQUIREMENTS).with_file(
        f"/{PYPROJECT_TOML_FILE_PATH}", pyproject_toml_file
    )


async def with_python_package(
    dagger_client: Client, python_environment: Container, package_source_code_path: str, additional_dependency_groups: Optional[List] = None
) -> Container:
    """Installs a python package in a python environment container.

    Args:
        dagger_client (Client): The dagger client.
        python_environment (Container): The existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        additional_dependency_groups (Optional[List], optional): extra_requires dependency of setup.py to install. Defaults to None.

    Returns:
        Container: A python environment container with the python package installed.
    """
    package_source_code_directory: Directory = dagger_client.host().directory(package_source_code_path, exclude=DEFAULT_PYTHON_EXCLUDE)
    container = python_environment.with_mounted_directory("/" + package_source_code_path, package_source_code_directory).with_workdir(
        "/" + package_source_code_path
    )

    if requirements_txt := await get_file_contents(container, "requirements.txt"):
        for line in requirements_txt.split("\n"):
            if line.startswith("-e ."):
                local_dependency_path = package_source_code_path + "/" + line[3:]
                container = container.with_mounted_directory(
                    "/" + local_dependency_path, dagger_client.host().directory(local_dependency_path, exclude=DEFAULT_PYTHON_EXCLUDE)
                )
        container = container.with_exec(INSTALL_LOCAL_REQUIREMENTS_CMD)

    container = container.with_exec(INSTALL_CONNECTOR_PACKAGE_CMD)

    if additional_dependency_groups:
        container = container.with_exec(
            INSTALL_CONNECTOR_PACKAGE_CMD[:-1] + [INSTALL_CONNECTOR_PACKAGE_CMD[-1] + f"[{','.join(additional_dependency_groups)}]"]
        )

    return container


async def with_airbyte_connector(dagger_client: Client, connector: Connector) -> Container:
    """Installs an airbyte connector python package in a testing environment.

    Args:
        dagger_client (Client): The dagger client.
        connector (Connector): The airbyte connector to install in the testing environment.
    """
    connector_source_path = str(connector.code_directory)
    testing_environment: Container = await with_testing_dependencies(dagger_client)
    return await with_python_package(dagger_client, testing_environment, connector_source_path, ["dev", "tests", "main"])
