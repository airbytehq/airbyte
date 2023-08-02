#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import sys

import dagger
import pytest
import requests


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
