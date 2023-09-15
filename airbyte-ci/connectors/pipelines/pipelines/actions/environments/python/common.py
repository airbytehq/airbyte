#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to create reusable environments packaged in dagger containers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from dagger import CacheSharingMode, CacheVolume, Container, DaggerError, Directory, Platform
from pipelines.actions.environments.common.finalize_build import finalize_build
from pipelines.consts import (
    CONNECTOR_TESTING_REQUIREMENTS,
    LICENSE_SHORT_FILE_PATH,
    PYPROJECT_TOML_FILE_PATH,
)
from pipelines.utils import check_path_in_workdir, get_file_contents, sh_dash_c

if TYPE_CHECKING:
    from pipelines.contexts import ConnectorContext, PipelineContext


def with_python_base(context: PipelineContext, python_version: str = "3.10") -> Container:
    """Build a Python container with a cache volume for pip cache.

    Args:
        context (PipelineContext): The current test context, providing a dagger client and a repository directory.
        python_image_name (str, optional): The python image to use to build the python base environment. Defaults to "python:3.9-slim".

    Raises:
        ValueError: Raised if the python_image_name is not a python image.

    Returns:
        Container: The python base environment container.
    """

    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")

    base_container = (
        context.dagger_client.container()
        .from_(f"python:{python_version}-slim")
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(
            sh_dash_c(
                [
                    "apt-get update",
                    "apt-get install -y build-essential cmake g++ libffi-dev libstdc++6 git",
                    "pip install pip==23.1.2",
                ]
            )
        )
    )

    return base_container


def with_testing_dependencies(context: PipelineContext) -> Container:
    """Build a testing environment by installing testing dependencies on top of a python base environment.

    Args:
        context (PipelineContext): The current test context, providing a dagger client and a repository directory.

    Returns:
        Container: The testing environment container.
    """
    python_environment: Container = with_python_base(context)
    pyproject_toml_file = context.get_repo_dir(".", include=[PYPROJECT_TOML_FILE_PATH]).file(PYPROJECT_TOML_FILE_PATH)
    license_short_file = context.get_repo_dir(".", include=[LICENSE_SHORT_FILE_PATH]).file(LICENSE_SHORT_FILE_PATH)

    return (
        python_environment.with_exec(["pip", "install"] + CONNECTOR_TESTING_REQUIREMENTS)
        .with_file(f"/{PYPROJECT_TOML_FILE_PATH}", pyproject_toml_file)
        .with_file(f"/{LICENSE_SHORT_FILE_PATH}", license_short_file)
    )


def with_python_package(
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    exclude: Optional[List] = None,
) -> Container:
    """Load a python package source code to a python environment container.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the python sources will be pulled.
        python_environment (Container): An existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        additional_dependency_groups (Optional[List]): extra_requires dependency of setup.py to install. Defaults to None.
        exclude (Optional[List]): A list of file or directory to exclude from the python package source code.

    Returns:
        Container: A python environment container with the python package source code.
    """
    package_source_code_directory: Directory = context.get_repo_dir(package_source_code_path, exclude=exclude)
    work_dir_path = f"/{package_source_code_path}"
    container = python_environment.with_mounted_directory(work_dir_path, package_source_code_directory).with_workdir(work_dir_path)
    return container


async def find_local_python_dependencies(
    context: PipelineContext,
    package_source_code_path: str,
    search_dependencies_in_setup_py: bool = True,
    search_dependencies_in_requirements_txt: bool = True,
) -> List[str]:
    """Find local python dependencies of a python package. The dependencies are found in the setup.py and requirements.txt files.

    Args:
        context (PipelineContext): The current pipeline context, providing a dagger client and a repository directory.
        package_source_code_path (str): The local path to the python package source code.
        search_dependencies_in_setup_py (bool, optional): Whether to search for local dependencies in the setup.py file. Defaults to True.
        search_dependencies_in_requirements_txt (bool, optional): Whether to search for local dependencies in the requirements.txt file. Defaults to True.

    Returns:
        List[str]: Paths to the local dependencies relative to the airbyte repo.
    """
    python_environment = with_python_base(context)
    container = with_python_package(context, python_environment, package_source_code_path)

    local_dependency_paths = []
    if search_dependencies_in_setup_py:
        local_dependency_paths += await find_local_dependencies_in_setup_py(container)
    if search_dependencies_in_requirements_txt:
        local_dependency_paths += await find_local_dependencies_in_requirements_txt(container, package_source_code_path)

    transitive_dependency_paths = []
    for local_dependency_path in local_dependency_paths:
        # Transitive local dependencies installation is achieved by calling their setup.py file, not their requirements.txt file.
        transitive_dependency_paths += await find_local_python_dependencies(context, local_dependency_path, True, False)

    all_dependency_paths = local_dependency_paths + transitive_dependency_paths
    if all_dependency_paths:
        context.logger.debug(f"Found local dependencies for {package_source_code_path}: {all_dependency_paths}")
    return all_dependency_paths


async def find_local_dependencies_in_setup_py(python_package: Container) -> List[str]:
    """Find local dependencies of a python package in its setup.py file.

    Args:
        python_package (Container): A python package container.

    Returns:
        List[str]: Paths to the local dependencies relative to the airbyte repo.
    """
    setup_file_content = await get_file_contents(python_package, "setup.py")
    if not setup_file_content:
        return []

    local_setup_dependency_paths = []
    with_egg_info = python_package.with_exec(["python", "setup.py", "egg_info"])
    egg_info_output = await with_egg_info.stdout()
    dependency_in_requires_txt = []
    for line in egg_info_output.split("\n"):
        if line.startswith("writing requirements to"):
            # Find the path to the requirements.txt file that was generated by calling egg_info
            requires_txt_path = line.replace("writing requirements to", "").strip()
            requirements_txt_content = await with_egg_info.file(requires_txt_path).contents()
            dependency_in_requires_txt = requirements_txt_content.split("\n")

    for dependency_line in dependency_in_requires_txt:
        if "file://" in dependency_line:
            match = re.search(r"file:///(.+)", dependency_line)
            if match:
                local_setup_dependency_paths.append([match.group(1)][0])
    return local_setup_dependency_paths


async def find_local_dependencies_in_requirements_txt(python_package: Container, package_source_code_path: str) -> List[str]:
    """Find local dependencies of a python package in a requirements.txt file.

    Args:
        python_package (Container): A python environment container with the python package source code.
        package_source_code_path (str): The local path to the python package source code.

    Returns:
        List[str]: Paths to the local dependencies relative to the airbyte repo.
    """
    requirements_txt_content = await get_file_contents(python_package, "requirements.txt")
    if not requirements_txt_content:
        return []

    local_requirements_dependency_paths = []
    for line in requirements_txt_content.split("\n"):
        # Some package declare themselves as a requirement in requirements.txt,
        # #Without line != "-e ." the package will be considered a dependency of itself which can cause an infinite loop
        if line.startswith("-e .") and line != "-e .":
            local_dependency_path = Path(line[3:])
            package_source_code_path = Path(package_source_code_path)
            local_dependency_path = str((package_source_code_path / local_dependency_path).resolve().relative_to(Path.cwd()))
            local_requirements_dependency_paths.append(local_dependency_path)
    return local_requirements_dependency_paths


async def with_installed_python_package(
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    additional_dependency_groups: Optional[List] = None,
    exclude: Optional[List] = None,
) -> Container:
    """Install a python package in a python environment container.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the python sources will be pulled.
        python_environment (Container): An existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        additional_dependency_groups (Optional[List]): extra_requires dependency of setup.py to install. Defaults to None.
        exclude (Optional[List]): A list of file or directory to exclude from the python package source code.

    Returns:
        Container: A python environment container with the python package installed.
    """
    install_requirements_cmd = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
    install_connector_package_cmd = ["python", "-m", "pip", "install", "."]

    container = with_python_package(context, python_environment, package_source_code_path, exclude=exclude)

    local_dependencies = await find_local_python_dependencies(context, package_source_code_path)

    for dependency_directory in local_dependencies:
        container = container.with_mounted_directory("/" + dependency_directory, context.get_repo_dir(dependency_directory))

    has_setup_py, has_requirements_txt = await check_path_in_workdir(container, "setup.py"), await check_path_in_workdir(
        container, "requirements.txt"
    )

    if has_setup_py:
        container = container.with_exec(install_connector_package_cmd)
    if has_requirements_txt:
        container = container.with_exec(install_requirements_cmd)

    if additional_dependency_groups:
        container = container.with_exec(
            install_connector_package_cmd[:-1] + [install_connector_package_cmd[-1] + f"[{','.join(additional_dependency_groups)}]"]
        )

    return container


def with_python_connector_source(context: ConnectorContext) -> Container:
    """Load an airbyte connector source code in a testing environment.

    Args:
        context (ConnectorContext): The current test context, providing the repository directory from which the connector sources will be pulled.
    Returns:
        Container: A python environment container (with the connector source code).
    """
    connector_source_path = str(context.connector.code_directory)
    testing_environment: Container = with_testing_dependencies(context)

    return with_python_package(context, testing_environment, connector_source_path)


async def with_python_connector_installed(context: ConnectorContext) -> Container:
    """Install an airbyte connector python package in a testing environment.

    Args:
        context (ConnectorContext): The current test context, providing the repository directory from which the connector sources will be pulled.
    Returns:
        Container: A python environment container (with the connector installed).
    """
    connector_source_path = str(context.connector.code_directory)
    testing_environment: Container = with_testing_dependencies(context)
    exclude = [
        f"{context.connector.code_directory}/{item}"
        for item in [
            "secrets",
            "metadata.yaml",
            "bootstrap.md",
            "icon.svg",
            "README.md",
            "Dockerfile",
            "acceptance-test-docker.sh",
            "build.gradle",
            ".hypothesis",
            ".dockerignore",
        ]
    ]
    return await with_installed_python_package(
        context, testing_environment, connector_source_path, additional_dependency_groups=["dev", "tests", "main"], exclude=exclude
    )


def with_pip_packages(base_container: Container, packages_to_install: List[str]) -> Container:
    """Installs packages using pip
    Args:
        context (Container): A container with python installed

    Returns:
        Container: A container with the pip packages installed.

    """
    package_install_command = ["pip", "install"]
    return base_container.with_exec(package_install_command + packages_to_install)


async def get_cdk_version_from_python_connector(python_connector: Container) -> Optional[str]:
    pip_freeze_stdout = await python_connector.with_entrypoint("pip").with_exec(["freeze"]).stdout()
    pip_dependencies = [dep.split("==") for dep in pip_freeze_stdout.split("\n")]
    for package_name, package_version in pip_dependencies:
        if package_name == "airbyte-cdk":
            return package_version
    return None


async def with_airbyte_python_connector(context: ConnectorContext, build_platform: Platform) -> Container:
    if context.connector.technical_name == "source-file-secure":
        return await with_airbyte_python_connector_full_dagger(context, build_platform)

    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")
    connector_container = (
        context.dagger_client.container(platform=build_platform)
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .build(await context.get_connector_dir())
        .with_label("io.airbyte.name", context.metadata["dockerRepository"])
    )
    cdk_version = await get_cdk_version_from_python_connector(connector_container)
    if cdk_version:
        connector_container = connector_container.with_label("io.airbyte.cdk_version", cdk_version)
        context.cdk_version = cdk_version
    if not await connector_container.label("io.airbyte.version") == context.metadata["dockerImageTag"]:
        raise DaggerError(
            "Abusive caching might be happening. The connector container should have been built with the correct version as defined in metadata.yaml"
        )
    return await finalize_build(context, connector_container)


async def with_airbyte_python_connector_full_dagger(context: ConnectorContext, build_platform: Platform) -> Container:
    setup_dependencies_to_mount = await find_local_python_dependencies(
        context, str(context.connector.code_directory), search_dependencies_in_setup_py=True, search_dependencies_in_requirements_txt=False
    )

    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")
    base = context.dagger_client.container(platform=build_platform).from_("python:3.9-slim")
    snake_case_name = context.connector.technical_name.replace("-", "_")
    entrypoint = ["python", "/airbyte/integration_code/main.py"]
    builder = (
        base.with_workdir("/airbyte/integration_code")
        .with_env_variable("DAGGER_BUILD", "1")
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(
            sh_dash_c(
                [
                    "apt-get update",
                    "apt-get install -y tzdata",
                    "pip install --upgrade pip",
                ]
            )
        )
        .with_file("setup.py", (await context.get_connector_dir(include="setup.py")).file("setup.py"))
    )

    for dependency_path in setup_dependencies_to_mount:
        in_container_dependency_path = f"/local_dependencies/{Path(dependency_path).name}"
        builder = builder.with_mounted_directory(in_container_dependency_path, context.get_repo_dir(dependency_path))

    builder = builder.with_exec(["pip", "install", "--prefix=/install", "."])

    connector_container = (
        base.with_workdir("/airbyte/integration_code")
        .with_exec(
            sh_dash_c(
                [
                    "apt-get update",
                    "apt-get install -y bash",
                ]
            )
        )
        .with_directory("/usr/local", builder.directory("/install"))
        .with_file("/usr/localtime", builder.file("/usr/share/zoneinfo/Etc/UTC"))
        .with_new_file("/etc/timezone", contents="Etc/UTC")
        .with_file("main.py", (await context.get_connector_dir(include="main.py")).file("main.py"))
        .with_directory(snake_case_name, (await context.get_connector_dir(include=snake_case_name)).directory(snake_case_name))
        .with_env_variable("AIRBYTE_ENTRYPOINT", " ".join(entrypoint))
        .with_entrypoint(entrypoint)
        .with_label("io.airbyte.version", context.metadata["dockerImageTag"])
        .with_label("io.airbyte.name", context.metadata["dockerRepository"])
    )
    return await finalize_build(context, connector_container)


