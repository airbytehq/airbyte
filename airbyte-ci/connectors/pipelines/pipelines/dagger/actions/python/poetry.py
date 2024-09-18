#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import uuid
from pathlib import Path
from typing import List, Optional

import toml
from dagger import Container, Directory
from pipelines.airbyte_ci.connectors.context import PipelineContext
from pipelines.consts import AIRBYTE_SUBMODULE_DIR_NAME
from pipelines.dagger.actions.python.common import with_pip_packages, with_python_package
from pipelines.dagger.actions.system.common import with_debian_packages
from pipelines.dagger.containers.python import with_python_base
from pipelines.helpers.utils import get_file_contents


async def find_local_dependencies_in_pyproject_toml(
    context: PipelineContext,
    base_container: Container,
    pyproject_file_path: str,
    exclude: Optional[List] = None,
) -> list:
    """Find local dependencies of a python package in a pyproject.toml file.

    Args:
        python_package (Container): A python environment container with the python package source code.
        pyproject_file_path (str): The path to the pyproject.toml file.

    Returns:
        list: Paths to the local dependencies relative to the current directory.
    """
    python_package = with_python_package(context, base_container, pyproject_file_path)
    pyproject_content_raw = await get_file_contents(python_package, "pyproject.toml")
    if not pyproject_content_raw:
        return []

    pyproject_content = toml.loads(pyproject_content_raw)
    local_dependency_paths = []
    for value in pyproject_content["tool"]["poetry"]["dependencies"].values():
        if isinstance(value, dict) and "path" in value:
            local_dependency_path = str((Path(pyproject_file_path) / Path(value["path"])).resolve().relative_to(Path.cwd()))
            # Support the edge case where the airbyte repo is used as a git submodule.
            local_dependency_path = local_dependency_path.removeprefix(f"{AIRBYTE_SUBMODULE_DIR_NAME}/")
            local_dependency_paths.append(local_dependency_path)

            # Ensure we parse the child dependencies
            # TODO handle more than pyproject.toml
            child_local_dependencies = await find_local_dependencies_in_pyproject_toml(
                context, base_container, local_dependency_path, exclude=exclude
            )
            local_dependency_paths += child_local_dependencies

    return local_dependency_paths


def with_poetry(context: PipelineContext) -> Container:
    """Install poetry in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
    Returns:
        Container: A python environment with poetry installed.
    """
    python_base_environment: Container = with_python_base(context)
    python_with_git = with_debian_packages(python_base_environment, ["git"])
    python_with_poetry = with_pip_packages(python_with_git, ["poetry"])

    # poetry_cache: CacheVolume = context.dagger_client.cache_volume("poetry_cache")
    # poetry_with_cache = python_with_poetry.with_mounted_cache("/root/.cache/pypoetry", poetry_cache, sharing=CacheSharingMode.SHARED)

    return python_with_poetry


def with_poetry_module(context: PipelineContext, parent_dir: Directory, module_path: str) -> Container:
    """Sets up a Poetry module.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
    Returns:
        Container: A python environment with dependencies installed using poetry.
    """
    poetry_install_dependencies_cmd = ["poetry", "install"]

    python_with_poetry = with_poetry(context)
    return (
        python_with_poetry.with_mounted_directory("/src", parent_dir)
        .with_workdir(f"/src/{module_path}")
        .with_exec(poetry_install_dependencies_cmd)
        .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
    )
