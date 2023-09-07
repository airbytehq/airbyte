#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from connector_ops.utils import Connector
from pipelines.actions import environments
from pipelines.contexts import PipelineContext

pytestmark = [
    pytest.mark.anyio,
]


@pytest.fixture
def python_connector() -> Connector:
    return Connector("source-openweather")


@pytest.fixture
def context(dagger_client):
    context = PipelineContext(
        pipeline_name="test",
        is_local=True,
        git_branch="test",
        git_revision="test",
    )
    context.dagger_client = dagger_client
    return context


async def test_with_installed_python_package(context, python_connector):
    python_environment = context.dagger_client.container().from_("python:3.10")
    installed_connector_package = await environments.with_installed_python_package(
        context,
        python_environment,
        str(python_connector.code_directory),
    )
    await installed_connector_package.with_exec(["python", "main.py", "spec"])
