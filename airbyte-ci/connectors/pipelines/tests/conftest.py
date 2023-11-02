#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import platform
import sys
from pathlib import Path
from typing import List

import dagger
import git
import pytest
import requests
from connector_ops.utils import Connector
from pipelines.helpers import utils
from tests.utils import ALL_CONNECTORS


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
def dagger_connection():
    return dagger.Connection(dagger.Config(log_output=sys.stderr))


@pytest.fixture(scope="module")
async def dagger_client(dagger_connection):
    async with dagger_connection as client:
        yield client


@pytest.fixture(scope="session")
def oss_registry():
    response = requests.get("https://connectors.airbyte.com/files/registries/v0/oss_registry.json")
    response.raise_for_status()
    return response.json()


@pytest.fixture(scope="session")
def airbyte_repo_path() -> Path:
    return Path(git.Repo(search_parent_directories=True).working_tree_dir)


@pytest.fixture
def new_connector(airbyte_repo_path: Path, mocker) -> Connector:
    new_connector_code_directory = airbyte_repo_path / "airbyte-integrations/connectors/source-new-connector"
    Path(new_connector_code_directory).mkdir()

    new_connector_code_directory.joinpath("metadata.yaml").touch()
    mocker.patch.object(
        utils,
        "ALL_CONNECTOR_DEPENDENCIES",
        [(connector, connector.get_local_dependency_paths()) for connector in utils.get_all_connectors_in_repo()],
    )
    yield Connector("source-new-connector")
    new_connector_code_directory.joinpath("metadata.yaml").unlink()
    new_connector_code_directory.rmdir()


@pytest.fixture(autouse=True, scope="session")
def from_airbyte_root(airbyte_repo_path):
    """
    Change the working directory to the root of the Airbyte repo.
    This will make all the tests current working directory to be the root of the Airbyte repo as we've set autouse=True.
    """
    original_dir = Path.cwd()
    os.chdir(airbyte_repo_path)
    yield airbyte_repo_path
    os.chdir(original_dir)


@pytest.fixture(scope="session")
def all_connectors() -> List[Connector]:
    return sorted(ALL_CONNECTORS, key=lambda connector: connector.technical_name)


@pytest.fixture(scope="session")
def current_platform():
    return dagger.Platform(f"linux/{platform.machine()}")
