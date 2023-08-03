#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import sys
from pathlib import Path

import dagger
import git
import pytest
import requests
from connector_ops.utils import Connector
from pipelines import utils


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def dagger_client():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
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
