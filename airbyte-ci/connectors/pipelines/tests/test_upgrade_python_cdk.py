#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import random
from pathlib import Path
from typing import List
from unittest.mock import AsyncMock, MagicMock

import anyio
import asyncclick as click
import pytest
from connector_ops.utils import Connector, ConnectorLanguage
from dagger import Directory
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.publish import pipeline as publish_pipeline
from pipelines.airbyte_ci.connectors.upgrade_cdk import pipeline as upgrade_cdk_pipeline
from pipelines.models.steps import StepStatus

pytestmark = [
    pytest.mark.anyio,
]


@pytest.fixture
def sample_connector():
    return Connector("source-pokeapi")


def get_sample_setup_py(airbyte_cdk_dependency: str):
    return f"""from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "{airbyte_cdk_dependency}",
]

setup(
    name="source_pokeapi",
    description="Source implementation for Pokeapi.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
)
"""


@pytest.fixture
def connector_context(sample_connector, dagger_client, current_platform):
    context = ConnectorContext(
        pipeline_name="test",
        connector=sample_connector,
        git_branch="test",
        git_revision="test",
        diffed_branch="test",
        git_repo_url="test",
        report_output_prefix="test",
        is_local=True,
        targeted_platforms=[current_platform],
    )
    context.dagger_client = dagger_client
    return context


@pytest.mark.parametrize(
    "setup_py_content, expected_setup_py_content",
    [
        (get_sample_setup_py("airbyte-cdk"), get_sample_setup_py("airbyte-cdk>=6.6.6")),
        (get_sample_setup_py("airbyte-cdk[file-based]"), get_sample_setup_py("airbyte-cdk[file-based]>=6.6.6")),
        (get_sample_setup_py("airbyte-cdk==1.2.3"), get_sample_setup_py("airbyte-cdk>=6.6.6")),
        (get_sample_setup_py("airbyte-cdk>=1.2.3"), get_sample_setup_py("airbyte-cdk>=6.6.6")),
        (get_sample_setup_py("airbyte-cdk[file-based]>=1.2.3"), get_sample_setup_py("airbyte-cdk[file-based]>=6.6.6")),
        (get_sample_setup_py("airbyte-cdk==1.2"), get_sample_setup_py("airbyte-cdk>=6.6.6")),
        (get_sample_setup_py("airbyte-cdk>=1.2"), get_sample_setup_py("airbyte-cdk>=6.6.6")),
        (get_sample_setup_py("airbyte-cdk[file-based]>=1.2"), get_sample_setup_py("airbyte-cdk[file-based]>=6.6.6")),
    ],
)
async def test_run_connector_cdk_upgrade_pipeline(
    connector_context: ConnectorContext, setup_py_content: str, expected_setup_py_content: str
):
    full_og_connector_dir = await connector_context.get_connector_dir()
    updated_connector_dir = full_og_connector_dir.with_new_file("setup.py", setup_py_content)

    # For this test, replace the actual connector dir with an updated version that sets the setup.py contents
    connector_context.get_connector_dir = AsyncMock(return_value=updated_connector_dir)

    # Mock the diff method to record the resulting directory and return a mock to not actually export the diff to the repo
    updated_connector_dir.diff = MagicMock(return_value=AsyncMock())
    step = upgrade_cdk_pipeline.SetCDKVersion(connector_context, "6.6.6")
    step_result = await step.run()
    assert step_result.status == StepStatus.SUCCESS

    # Check that the resulting directory that got passed to the mocked diff method looks as expected
    resulting_directory: Directory = await full_og_connector_dir.diff(updated_connector_dir.diff.call_args[0][0])
    files = await resulting_directory.entries()
    # validate only setup.py is changed
    assert files == ["setup.py"]
    setup_py = resulting_directory.file("setup.py")
    actual_setup_py_content = await setup_py.contents()
    assert actual_setup_py_content == expected_setup_py_content

    # Assert that the diff was exported to the repo
    assert updated_connector_dir.diff.return_value.export.call_count == 1


async def test_skip_connector_cdk_upgrade_pipeline_on_missing_setup_py(connector_context: ConnectorContext):
    full_og_connector_dir = await connector_context.get_connector_dir()
    updated_connector_dir = full_og_connector_dir.without_file("setup.py")

    connector_context.get_connector_dir = AsyncMock(return_value=updated_connector_dir)

    step = upgrade_cdk_pipeline.SetCDKVersion(connector_context, "6.6.6")
    step_result = await step.run()
    assert step_result.status == StepStatus.SKIPPED


async def test_fail_connector_cdk_upgrade_pipeline_on_missing_airbyte_cdk(connector_context: ConnectorContext):
    full_og_connector_dir = await connector_context.get_connector_dir()
    updated_connector_dir = full_og_connector_dir.with_new_file("setup.py", get_sample_setup_py("another-lib==1.2.3"))

    connector_context.get_connector_dir = AsyncMock(return_value=updated_connector_dir)

    step = upgrade_cdk_pipeline.SetCDKVersion(connector_context, "6.6.6")
    step_result = await step.run()
    assert step_result.status == StepStatus.FAILURE
