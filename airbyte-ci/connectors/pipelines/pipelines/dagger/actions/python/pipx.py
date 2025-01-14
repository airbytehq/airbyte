#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

from dagger import Container

from pipelines.airbyte_ci.connectors.context import PipelineContext
from pipelines.dagger.actions.python.common import with_pip_packages, with_python_package
from pipelines.dagger.actions.python.poetry import find_local_dependencies_in_pyproject_toml


def with_pipx(base_python_container: Container) -> Container:
    """Installs pipx in a python container.

    Args:
       base_python_container (Container): The container to install pipx on.

    Returns:
        Container: A python environment with pipx installed.
    """
    python_with_pipx = with_pip_packages(base_python_container, ["pipx"]).with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")

    return python_with_pipx


async def with_installed_pipx_package(
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    exclude: Optional[List] = None,
) -> Container:
    """Install a python package in a python environment container using pipx.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the python sources will be pulled.
        python_environment (Container): An existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        exclude (Optional[List]): A list of file or directory to exclude from the python package source code.

    Returns:
        Container: A python environment container with the python package installed.
    """
    pipx_python_environment = with_pipx(python_environment)
    container = with_python_package(context, pipx_python_environment, package_source_code_path, exclude=exclude)

    local_dependencies = await find_local_dependencies_in_pyproject_toml(context, container, package_source_code_path, exclude=exclude)
    for dependency_directory in local_dependencies:
        container = container.with_mounted_directory("/" + dependency_directory, context.get_repo_dir(dependency_directory))

    container = container.with_exec(["pipx", "install", f"/{package_source_code_path}"], use_entrypoint=True)

    return container
