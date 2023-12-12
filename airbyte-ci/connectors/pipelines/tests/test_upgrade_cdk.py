#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import random
from typing import List

import anyio
import pytest
from connector_ops.utils import Connector, ConnectorLanguage
from pipelines.airbyte_ci.connectors.publish import pipeline as publish_pipeline
from pipelines.airbyte_ci.connectors.upgrade_cdk import pipeline as upgrade_cdk_pipeline
from pipelines.models.steps import StepStatus
from pipelines.airbyte_ci.connectors.context import ConnectorContext

pytestmark = [
    pytest.mark.anyio,
]

@pytest.fixture
def connector_with_poetry():
    return Connector("destination-duckdb")

@pytest.fixture
def context_for_connector_with_poetry(connector_with_poetry, dagger_client, current_platform):
    context = ConnectorContext(
        pipeline_name="test unit tests",
        connector=connector_with_poetry,
        git_branch="test",
        git_revision="test",
        report_output_prefix="test",
        is_local=True,
        use_remote_secrets=True,
        targeted_platforms=[current_platform],
    )
    context.dagger_client = dagger_client
    context.connector_secrets = {}
    return context

async def test_run_connector_cdk_upgrade_pipeline(context_for_connector_with_poetry):
    semaphore = anyio.Semaphore(1)
    # og_repo_dir = await context.get_repo_dir()
    # report = await upgrade_cdk_pipeline.run_connector_cdk_upgrade_pipeline(context_for_connector_with_poetry, semaphore, "6.6.6")
    og_repo_dir = await context_for_connector_with_poetry.get_repo_dir()
    step = upgrade_cdk_pipeline.SetCDKVersion(context_for_connector_with_poetry, og_repo_dir, "6.6.6")
    step_result = await step.run()

    # print(report.steps_results[-1])
    print(step_result)
