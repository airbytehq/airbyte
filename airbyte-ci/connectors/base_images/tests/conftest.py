#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import platform
import sys

import dagger
import pytest


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def dagger_client():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        yield client


@pytest.fixture(scope="session")
def current_platform():
    return dagger.Platform(f"linux/{platform.machine()}")
