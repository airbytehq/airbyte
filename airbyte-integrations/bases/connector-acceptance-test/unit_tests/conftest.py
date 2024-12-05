#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import sys
from contextlib import contextmanager

import dagger
import pytest


@pytest.fixture
def mssql_spec_schema():
    with open("unit_tests/data/mssql_spec.json") as f:
        return json.load(f).get("connectionSpecification")


@pytest.fixture
def postgres_source_spec_schema():
    with open("unit_tests/data/postgres_spec.json") as f:
        return json.load(f).get("connectionSpecification")


@contextmanager
def does_not_raise():
    yield


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def dagger_client():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        yield client


@pytest.fixture(scope="module")
async def source_faker_container(dagger_client):
    return await dagger_client.container().from_("airbyte/source-faker:latest")
