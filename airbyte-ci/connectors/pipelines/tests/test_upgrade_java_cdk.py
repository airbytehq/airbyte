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
    return Connector("source-postgres")


def get_sample_build_gradle(airbyte_cdk_version: str, useLocalCdk: str):
    return f"""import org.jsonschema2pojo.SourceType

plugins {{
    id 'application'
    id 'airbyte-java-connector'
    id "org.jsonschema2pojo" version "1.2.1"
}}

java {{
    compileJava {{
        options.compilerArgs += "-Xlint:-try,-rawtypes,-unchecked"
    }}
}}

airbyteJavaConnector {{
    cdkVersionRequired = '{airbyte_cdk_version}'
    features = ['db-sources']
    useLocalCdk = {useLocalCdk}
}}


application {{
    mainClass = 'io.airbyte.integrations.source.postgres.PostgresSource'
    applicationDefaultJvmArgs = ['-XX:+ExitOnOutOfMemoryError', '-XX:MaxRAMPercentage=75.0']
}}
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
    "build_gradle_content, expected_build_gradle_content",
    [
        (get_sample_build_gradle("1.2.3", "false"), get_sample_build_gradle("6.6.6", "false")),
        (get_sample_build_gradle("1.2.3", "true"), get_sample_build_gradle("6.6.6", "false")),
        (get_sample_build_gradle("6.6.6", "false"), get_sample_build_gradle("6.6.6", "false")),
        (get_sample_build_gradle("6.6.6", "true"), get_sample_build_gradle("6.6.6", "false")),
        (get_sample_build_gradle("7.0.0", "false"), get_sample_build_gradle("6.6.6", "false")),
        (get_sample_build_gradle("7.0.0", "true"), get_sample_build_gradle("6.6.6", "false")),
    ],
)
async def test_run_connector_cdk_upgrade_pipeline(
    connector_context: ConnectorContext, build_gradle_content: str, expected_build_gradle_content: str
):
    full_og_connector_dir = await connector_context.get_connector_dir()
    updated_connector_dir = full_og_connector_dir.with_new_file("build.gradle", build_gradle_content)

    # For this test, replace the actual connector dir with an updated version that sets the build.gradle contents
    connector_context.get_connector_dir = AsyncMock(return_value=updated_connector_dir)

    # Mock the diff method to record the resulting directory and return a mock to not actually export the diff to the repo
    updated_connector_dir.diff = MagicMock(return_value=AsyncMock())
    step = upgrade_cdk_pipeline.SetCDKVersion(connector_context, "6.6.6")
    step_result = await step.run()
    assert step_result.status == StepStatus.SUCCESS

    # Check that the resulting directory that got passed to the mocked diff method looks as expected
    resulting_directory: Directory = await full_og_connector_dir.diff(updated_connector_dir.diff.call_args[0][0])
    files = await resulting_directory.entries()
    # validate only build.gradle is changed
    assert files == ["build.gradle"]
    build_gradle = resulting_directory.file("build.gradle")
    actual_build_gradle_content = await build_gradle.contents()
    assert actual_build_gradle_content == expected_build_gradle_content

    # Assert that the diff was exported to the repo
    assert updated_connector_dir.diff.return_value.export.call_count == 1


async def test_skip_connector_cdk_upgrade_pipeline_on_missing_build_gradle(connector_context: ConnectorContext):
    full_og_connector_dir = await connector_context.get_connector_dir()
    updated_connector_dir = full_og_connector_dir.without_file("build.gradle")

    connector_context.get_connector_dir = AsyncMock(return_value=updated_connector_dir)

    step = upgrade_cdk_pipeline.SetCDKVersion(connector_context, "6.6.6")
    step_result = await step.run()
    assert step_result.status == StepStatus.FAILURE


async def test_fail_connector_cdk_upgrade_pipeline_on_missing_airbyte_cdk(connector_context: ConnectorContext):
    full_og_connector_dir = await connector_context.get_connector_dir()
    updated_connector_dir = full_og_connector_dir.with_new_file("build.gradle", get_sample_build_gradle("abc", "false"))

    connector_context.get_connector_dir = AsyncMock(return_value=updated_connector_dir)

    step = upgrade_cdk_pipeline.SetCDKVersion(connector_context, "6.6.6")
    step_result = await step.run()
    assert step_result.status == StepStatus.FAILURE
