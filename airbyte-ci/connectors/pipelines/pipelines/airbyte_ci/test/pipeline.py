# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import asyncer
import dagger
import toml

from pipelines.airbyte_ci.test.models import deserialize_airbyte_ci_config
from pipelines.consts import DOCKER_HOST_NAME, DOCKER_HOST_PORT, DOCKER_VERSION, POETRY_CACHE_VOLUME_NAME, PYPROJECT_TOML_FILE_PATH
from pipelines.dagger.actions.system import docker
from pipelines.helpers.github import update_commit_status_check
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.steps import PoeTaskResult, StepStatus

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path
    from typing import Dict, List

    from pipelines.airbyte_ci.test.models import AirbyteCiPackageConfiguration

# The following directories are always mounted because a lot of tests rely on them
DIRECTORIES_TO_ALWAYS_MOUNT = [
    ".git",  # This is needed as some package tests rely on being in a git repo
    ".github",
    "docs",
    "airbyte-integrations",
    "airbyte-ci",
    "airbyte-cdk",
    PYPROJECT_TOML_FILE_PATH,
    "LICENSE_SHORT",
    "poetry.lock",
    "spotless-maven-pom.xml",
    "tools/gradle/codestyle/java-google-style.xml",
]

DEFAULT_EXCLUDE = ["**/__pycache__", "**/.pytest_cache", "**/.venv", "**.log", "**/.gradle"]

DEFAULT_CONTAINER_IMAGE = "python:{version}"

VERSION_CONTAINER_IMAGES = {
    "3.10": DEFAULT_CONTAINER_IMAGE.format(version="3.10.12"),
    "3.11": DEFAULT_CONTAINER_IMAGE.format(version="3.11.5"),
}


async def get_filtered_airbyte_repo_dir(dagger_client: dagger.Client, poetry_package_path: Path) -> dagger.Directory:
    """Get a filtered airbyte repo directory with the directories to always mount and the poetry package path.

    Args:
        dagger_client (dagger.Client): Dagger client.
        poetry_package_path (Path): Path to the poetry package in the airbyte repo.

    Returns:
        dagger.Directory: The filtered airbyte repo directory.
    """
    directories_to_mount = list(set([str(poetry_package_path), *DIRECTORIES_TO_ALWAYS_MOUNT]))
    return dagger_client.host().directory(
        ".",
        exclude=DEFAULT_EXCLUDE,
        include=directories_to_mount,
    )


async def get_poetry_package_dir(airbyte_repo_dir: dagger.Directory, poetry_package_path: Path) -> dagger.Directory:
    """Get the poetry package directory from the airbyte repo directory.

    Args:
        airbyte_repo_dir (dagger.Directory): The airbyte repo directory.
        poetry_package_path (Path): Path to the poetry package in the airbyte repo.

    Raises:
        FileNotFoundError: If the pyproject.toml file is not found in the poetry package directory.
        FileNotFoundError: If the poetry package directory is not found in the airbyte repo directory.

    Returns:
        dagger.Directory: The poetry package directory.
    """
    try:
        package_directory = await airbyte_repo_dir.directory(str(poetry_package_path))
        if PYPROJECT_TOML_FILE_PATH not in await package_directory.entries():
            raise FileNotFoundError(f"Could not find pyproject.toml in {poetry_package_path}, are you sure this is a poetry package?")
    except dagger.DaggerError:
        raise FileNotFoundError(f"Could not find {poetry_package_path} in the repository, are you sure this path is correct?")
    return package_directory


async def get_airbyte_ci_package_config(poetry_package_dir: dagger.Directory) -> AirbyteCiPackageConfiguration:
    """Get the airbyte ci package configuration from the pyproject.toml file in the poetry package directory.

    Args:
        poetry_package_dir (dagger.Directory): The poetry package directory.

    Returns:
        AirbyteCiPackageConfiguration: The airbyte ci package configuration.
    """
    raw_pyproject_toml = await poetry_package_dir.file(PYPROJECT_TOML_FILE_PATH).contents()
    pyproject_toml = toml.loads(raw_pyproject_toml)
    return deserialize_airbyte_ci_config(pyproject_toml)


def get_poetry_base_container(dagger_client: dagger.Client, python_version: str) -> dagger.Container:
    """Get a base container with system dependencies to run poe tasks of poetry package:
    - git: required for packages using GitPython
    - poetry
    - poethepoet
    - docker: required for packages using docker in their tests

    Args:
        dagger_client (dagger.Client): The dagger client.

    Returns:
        dagger.Container: The base container.
    """
    poetry_cache_volume: dagger.CacheVolume = dagger_client.cache_volume(POETRY_CACHE_VOLUME_NAME)
    poetry_cache_path = "/root/.cache/poetry"
    container_image = VERSION_CONTAINER_IMAGES.get(python_version, DEFAULT_CONTAINER_IMAGE.format(version=python_version))
    return (
        dagger_client.container()
        .from_(container_image)
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
    pipeline_context_params: Dict,
    python_version: str,
) -> dagger.Container:
    """Prepare a container to run poe tasks for a poetry package.

    Args:
        dagger_client (dagger.Client): The dagger client.
        airbyte_repo_dir (dagger.Directory): The airbyte repo directory.
        airbyte_ci_package_config (AirbyteCiPackageConfiguration): The airbyte ci package configuration.
        poetry_package_path (Path): The path to the poetry package in the airbyte repo.
        pipeline_context_params (Dict): The pipeline context parameters.

    Returns:
        dagger.Container: The container to run poe tasks for the poetry package.
    """

    # BE CAREFUL ABOUT THE ORDER OF THESE INSTRUCTIONS
    # PLEASE REMIND THAT DAGGER OPERATION ARE CACHED LIKE IN DOCKERFILE:
    # ANY CHANGE IN THE INPUTS OF AN OPERATION WILL INVALIDATE THE DOWNSTREAM OPERATIONS CACHE

    # Start from the base container
    container = get_poetry_base_container(dagger_client, python_version)

    # Set the CI environment variable
    is_ci = pipeline_context_params["is_ci"]
    if is_ci:
        container = container.with_env_variable("CI", "true")

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

    # Set the required environment variables according to the package configuration
    for required_env_var in airbyte_ci_package_config.required_environment_variables:
        # We consider any environment variable as a secret for safety reasons
        secret_env_var = dagger_client.set_secret(required_env_var, os.environ[required_env_var])
        container = container.with_secret_variable(required_env_var, secret_env_var)

    # Mount the airbyte repo directory
    container = container.with_mounted_directory("/airbyte", airbyte_repo_dir)

    # Set working directory to the poetry package directory
    container = container.with_workdir(f"/airbyte/{poetry_package_path}")

    # If a package from `airbyte-platform-internal` is required, modify the entry in pyproject.toml to use https instead of ssh,
    # when run in Github Actions
    # This is currently required for getting the connection-retriever package, for regression tests.
    if is_ci:
        container = (
            container.with_exec(
                [
                    "sed",
                    "-i",
                    "-E",
                    r"s,git@github\.com:airbytehq/airbyte-platform-internal,https://github.com/airbytehq/airbyte-platform-internal.git,",
                    "pyproject.toml",
                ],
                use_entrypoint=True,
            )
            .with_exec(
                [
                    "poetry",
                    "source",
                    "add",
                    "--priority=supplemental",
                    "airbyte-platform-internal-source",
                    "https://github.com/airbytehq/airbyte-platform-internal.git",
                ],
                use_entrypoint=True,
            )
            .with_secret_variable(
                "CI_GITHUB_ACCESS_TOKEN",
                dagger_client.set_secret("CI_GITHUB_ACCESS_TOKEN", pipeline_context_params["ci_github_access_token"].value),
            )
            .with_exec(
                [
                    "/bin/sh",
                    "-c",
                    "poetry config http-basic.airbyte-platform-internal-source octavia-squidington-iii $CI_GITHUB_ACCESS_TOKEN",
                ],
                use_entrypoint=True,
            )
            .with_exec(["poetry", "lock"], use_entrypoint=True)
        )

    # Install the poetry package
    container = container.with_exec(
        ["poetry", "install"]
        + [f"--with={group}" for group in airbyte_ci_package_config.optional_poetry_groups]
        + [f"--extras={extra}" for extra in airbyte_ci_package_config.poetry_extras]
    )
    return container


async def run_poe_task(container: dagger.Container, poe_task: str) -> PoeTaskResult:
    """Run the poe task in the container and return a PoeTaskResult.

    Args:
        container (dagger.Container): The container to run the poe task in.
        poe_task (str): The poe task to run.

    Returns:
        PoeTaskResult: The result of the command execution.
    """
    try:
        executed_container = await container.with_exec(["poe", poe_task], use_entrypoint=True)
        return PoeTaskResult(
            task_name=poe_task,
            status=StepStatus.SUCCESS,
            stdout=await executed_container.stdout(),
            stderr=await executed_container.stderr(),
        )
    except dagger.ExecError as e:
        return PoeTaskResult(task_name=poe_task, status=StepStatus.FAILURE, exc_info=e)


async def run_and_log_poe_task_results(
    pipeline_context_params: Dict, package_name: str, container: dagger.Container, poe_task: str, logger: Logger
) -> PoeTaskResult:
    """Run the poe task in the container and log the result.

    Args:
        pipeline_context_params (Dict): The pipeline context parameters.
        package_name (str): The name of the package to run the poe task for.
        container (dagger.Container): The container to run the poe task in.
        poe_task (str): The poe task to run.
        logger (Logger): The logger to log the result.

    Returns:
        PoeTaskResult: The result of the command execution.
    """

    commit_status_check_params = {
        "sha": pipeline_context_params["git_revision"],
        "description": f"{poe_task} execution for {package_name}",
        "context": f"{package_name} - {poe_task}",
        "target_url": f"{pipeline_context_params['gha_workflow_run_url']}",
        "should_send": pipeline_context_params["is_ci"],
        "logger": logger,
    }

    logger.info(f"Running poe task: {poe_task}")
    # Send pending status check
    update_commit_status_check(**{**commit_status_check_params, "state": "pending"})
    result = await run_poe_task(container, poe_task)
    result.log(logger)
    # Send the final status check
    update_commit_status_check(**{**commit_status_check_params, "state": result.status.get_github_state()})

    return result


async def run_poe_tasks_for_package(
    dagger_client: dagger.Client, poetry_package_path: Path, pipeline_context_params: Dict
) -> List[PoeTaskResult]:
    """Concurrently Run the poe tasks declared in pyproject.toml for a poetry package.

    Args:
        dagger_client (dagger.Client): The dagger client.
        poetry_package_path (Path): The path to the poetry package in the airbyte repo.
        pipeline_context_params (Dict): The pipeline context parameters.
    Returns:
        List[PoeTaskResult]: The results of the poe tasks.
    """
    dagger_client = dagger_client
    airbyte_repo_dir = await get_filtered_airbyte_repo_dir(dagger_client, poetry_package_path)
    package_dir = await get_poetry_package_dir(airbyte_repo_dir, poetry_package_path)
    package_config = await get_airbyte_ci_package_config(package_dir)

    logger = logging.getLogger(str(poetry_package_path))

    if not package_config.poe_tasks:
        logger.warning("No poe tasks to run.")
        return []

    logger.info(f"Python versions: {package_config.python_versions}")

    poe_task_results: List[asyncer.SoonValue] = []
    return_results = []

    for python_version in package_config.python_versions:
        container = prepare_container_for_poe_tasks(
            dagger_client, airbyte_repo_dir, package_config, poetry_package_path, pipeline_context_params, python_version
        )

        async with asyncer.create_task_group() as poe_tasks_task_group:
            for task in package_config.poe_tasks:
                poe_task_results.append(
                    poe_tasks_task_group.soonify(run_and_log_poe_task_results)(
                        pipeline_context_params, str(poetry_package_path), container, task, logger.getChild(f"@{python_version}")
                    )
                )

        return_results.extend([result.value for result in poe_task_results])

    return return_results
