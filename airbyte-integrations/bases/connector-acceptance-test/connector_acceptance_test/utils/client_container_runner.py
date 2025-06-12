#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
import uuid
from glob import glob
from pathlib import Path
from typing import List

import dagger

from connector_acceptance_test.utils import SecretDict


IN_CONTAINER_CONNECTOR_PATH = Path("/connector")
IN_CONTAINER_CONFIG_PATH = Path("/tmp/config.json")
IN_CONTAINER_OUTPUT_PATH = Path("/tmp/output.txt")


async def _build_container(dagger_client: dagger.Client, dockerfile_path: Path) -> dagger.Container:
    workspace = (
        dagger_client.container()
        .with_mounted_directory("/tmp/setup_teardown_context", dagger_client.host().directory(os.path.dirname(dockerfile_path)))
        .directory("/tmp/setup_teardown_context")
    )
    return await dagger_client.container().build(context=workspace, dockerfile=dockerfile_path.name)


async def _build_client_container(dagger_client: dagger.Client, connector_path: Path, dockerfile_path: Path) -> dagger.Container:
    container = await _build_container(dagger_client, dockerfile_path)
    return container.with_mounted_directory(
        str(IN_CONTAINER_CONNECTOR_PATH), dagger_client.host().directory(str(connector_path), exclude=get_default_excluded_files())
    )


def get_default_excluded_files() -> List[str]:
    return (
        [".git"]
        + glob("**/build", recursive=True)
        + glob("**/.venv", recursive=True)
        + glob("**/__pycache__", recursive=True)
        + glob("**/*.egg-info", recursive=True)
        + glob("**/.vscode", recursive=True)
        + glob("**/.pytest_cache", recursive=True)
        + glob("**/.eggs", recursive=True)
        + glob("**/.mypy_cache", recursive=True)
        + glob("**/.DS_Store", recursive=True)
        + glob("**/.gradle", recursive=True)
    )


async def _run_with_config(container: dagger.Container, command: List[str], config: SecretDict) -> dagger.Container:
    container = container.with_new_file(str(IN_CONTAINER_CONFIG_PATH), contents=json.dumps(dict(config)))
    return await _run(container, command)


async def _run(container: dagger.Container, command: List[str]) -> dagger.Container:
    return await container.with_env_variable("CACHEBUSTER", str(uuid.uuid4())).with_exec(command)


async def get_client_container(dagger_client: dagger.Client, connector_path: Path, dockerfile_path: Path):
    return await _build_client_container(dagger_client, connector_path, dockerfile_path)


async def do_setup(container: dagger.Container, command: List[str], connector_config: SecretDict, connector_path: Path):
    container = await _run_with_config(container, command, connector_config)
    await container.directory(str(IN_CONTAINER_CONNECTOR_PATH / "integration_tests")).export(str(connector_path / "integration_tests"))
    return container


async def do_teardown(container: dagger.Container, command: List[str]):
    return await _run(container, command)
