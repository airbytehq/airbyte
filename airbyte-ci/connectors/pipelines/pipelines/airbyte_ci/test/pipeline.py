# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import asyncer
import dagger
import toml
from pipelines.airbyte_ci.test.models import deserialize_airbyte_ci_config
from pipelines.consts import DOCKER_HOST_NAME, DOCKER_HOST_PORT, DOCKER_VERSION, POETRY_CACHE_VOLUME_NAME
from pipelines.dagger.actions.system import docker
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.steps import PoeTaskResult, StepStatus

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path
    from typing import List

    from pipelines.airbyte_ci.test.models import AirbyteCiPackageConfiguration

# The following directories are always mounted because a lot of tests rely on them
DIRECTORIES_TO_ALWAYS_MOUNT = [
    ".git",  # This is needed as some package tests rely on being in a git repo
    ".github",
    "docs",
    "airbyte-integrations",
    "airbyte-ci",
    "airbyte-cdk",
    "pyproject.toml",
    "LICENSE_SHORT",
    "poetry.lock",
    "spotless-maven-pom.xml",
    "tools/gradle/codestyle/java-google-style.xml",
]

DEFAULT_EXCLUDE = ["**/__pycache__", "**/.pytest_cache", "**/.venv", "**.log", "**/.gradle"]


async def get_filtered_airbyte_repo_dir(dagger_client: dagger.Client, poetry_package_path: Path) -> dagger.Directory:
    directories_to_mount = list(set([str(poetry_package_path), *DIRECTORIES_TO_ALWAYS_MOUNT]))
    return dagger_client.host().directory(
        ".",
        exclude=DEFAULT_EXCLUDE,
        include=directories_to_mount,
    )


async def get_poetry_package_dir(airbyte_repo_dir: dagger.Directory, poetry_package_path: Path) -> dagger.Directory:
    """Validate that the given package is a poetry package."""
    try:
        package_directory = await airbyte_repo_dir.directory(str(poetry_package_path))
        if "pyproject.toml" not in await package_directory.entries():
            raise FileNotFoundError(f"Could not find pyproject.toml in {poetry_package_path}, are you sure this is a poetry package?")
    except dagger.DaggerError:
        raise FileNotFoundError(f"Could not find {poetry_package_path} in the repository, are you sure this path is correct?")
    return package_directory


async def get_airbyte_ci_package_config(poetry_package_dir: dagger.Directory) -> AirbyteCiPackageConfiguration:
    raw_pyproject_toml = await poetry_package_dir.file("pyproject.toml").contents()
    pyproject_toml = toml.loads(raw_pyproject_toml)
    return deserialize_airbyte_ci_config(pyproject_toml)


def get_poetry_base_container(dagger_client: dagger.Client) -> dagger.Container:
    """Get a base container with system dependencies to run poetry package CI:
    - git: required for packages using GitPython
    - poetry
    - poethepoet
    - docker: required for packages using docker in their tests
    """
    poetry_cache_volume: dagger.CacheVolume = dagger_client.cache_volume(POETRY_CACHE_VOLUME_NAME)
    poetry_cache_path = "/root/.cache/poetry"
    return (
        dagger_client.container()
        .from_("python:3.10.12")
        .with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")
        .with_env_variable("POETRY_CACHE_DIR", poetry_cache_path)
        .with_mounted_cache(poetry_cache_path, poetry_cache_volume)
        .with_exec(
            sh_dash_c(
                [
                    "apt-get update",
                    "apt-get install -y bash git curl",
                    "pip install pipx",
                    "pipx ensurepath",
                    "pipx install poetry",
                    "pipx install poethepoet",
                ]
            )
        )
        .with_env_variable("VERSION", DOCKER_VERSION)
        .with_exec(sh_dash_c(["curl -fsSL https://get.docker.com | sh"]))
    )


def prepare_container_for_poe_tasks(
    dagger_client: dagger.Client,
    airbyte_repo_dir: dagger.Directory,
    airbyte_ci_package_config: AirbyteCiPackageConfiguration,
    poetry_package_path: Path,
    is_ci: bool,
) -> dagger.Container:
    """Prepare the container to run the poe task"""

    # Start from the base container
    container = get_poetry_base_container(dagger_client)

    # Set the CI environment variable
    if is_ci:
        container = container.with_env_variable("CI", "true")

    # Set the required environment variables according to the package configuration
    for required_env_var in airbyte_ci_package_config.required_environment_variables:
        # We consider any environment variable as a secret for safety reasons
        secret_env_var = dagger_client.set_secret(required_env_var, os.environ[required_env_var])
        container = container.with_secret_variable(required_env_var, secret_env_var)

    # Mount the airbyte repo directory
    container = container.with_mounted_directory("/airbyte", airbyte_repo_dir)

    # Set working directory to the poetry package directory
    container = container.with_workdir(f"/airbyte/{poetry_package_path}")

    # Bind to dockerd service if needed
    if airbyte_ci_package_config.side_car_docker_engine:
        dockerd_service = docker.with_global_dockerd_service(dagger_client)
        container = (
            container.with_env_variable("DOCKER_HOST", f"tcp://{DOCKER_HOST_NAME}:{DOCKER_HOST_PORT}")
            .with_env_variable("DOCKER_HOST_NAME", DOCKER_HOST_NAME)
            .with_service_binding(DOCKER_HOST_NAME, dockerd_service)
        )

    # Mount the docker socket if needed
    if airbyte_ci_package_config.mount_docker_socket:
        container = container.with_unix_socket("/var/run/docker.sock", dagger_client.host().unix_socket("/var/run/docker.sock"))

    # Install the poetry package
    container = container.with_exec(["poetry", "install"] + [f"--with={group}" for group in airbyte_ci_package_config.extra_poetry_groups])
    return container


async def run_poe_task(container: dagger.Container, poe_task: str) -> PoeTaskResult:
    """Run the poe task in the container and return the stdout and stderr

    Args:
        container (dagger.Container): The container to run the poe task in.
        poe_task (str): The poe task to run.

    Returns:
        PoeTaskResult: The result of the command execution.
    """
    try:
        executed_container = await container.pipeline(f"Run poe {poe_task}").with_exec(["poe", poe_task])
        return PoeTaskResult(
            task_name=poe_task,
            status=StepStatus.SUCCESS,
            stdout=await executed_container.stdout(),
            stderr=await executed_container.stderr(),
        )
    except dagger.ExecError as e:
        return PoeTaskResult(task_name=poe_task, status=StepStatus.FAILURE, exc_info=e)


async def run_and_log_poe_task_results(container: dagger.Container, poe_task: str, logger: Logger) -> PoeTaskResult:
    logger.info(f"Running poe task: {poe_task}")
    result = await run_poe_task(container, poe_task)
    result.log(logger)

    return result


async def run_poe_tasks_for_package(dagger_client: dagger.Client, poetry_package_path: Path, is_ci: bool) -> List[PoeTaskResult]:
    dagger_client = dagger_client.pipeline(f"Run poe tasks for {poetry_package_path}")
    airbyte_repo_dir = await get_filtered_airbyte_repo_dir(dagger_client, poetry_package_path)
    package_dir = await get_poetry_package_dir(airbyte_repo_dir, poetry_package_path)
    package_config = await get_airbyte_ci_package_config(package_dir)
    container = prepare_container_for_poe_tasks(dagger_client, airbyte_repo_dir, package_config, poetry_package_path, is_ci)
    logger = logging.getLogger(str(poetry_package_path))

    if not package_config.poe_tasks:
        logger.warning("No poe tasks to run.")
        return []

    poe_task_results = []
    async with asyncer.create_task_group() as poe_tasks_task_group:
        for task in package_config.poe_tasks:
            poe_task_results.append(poe_tasks_task_group.soonify(run_and_log_poe_task_results)(container, task, logger))
    return [result.value for result in poe_task_results]
