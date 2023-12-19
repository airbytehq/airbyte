#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch tests steps according to the connector under test language."""

from typing import List

import anyio
from connector_ops.utils import ConnectorLanguage
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.airbyte_ci.connectors.test.steps import java_connectors, python_connectors
from pipelines.airbyte_ci.connectors.test.steps.common import QaChecks, VersionFollowsSemverCheck, VersionIncrementCheck
from pipelines.airbyte_ci.metadata.pipeline import MetadataValidation
from pipelines.helpers.run_steps import StepToRun, run_steps

LANGUAGE_MAPPING = {
    "get_test_steps": {
        ConnectorLanguage.PYTHON: python_connectors.get_test_steps,
        ConnectorLanguage.LOW_CODE: python_connectors.get_test_steps,
        ConnectorLanguage.JAVA: java_connectors.get_test_steps,
    },
}


def get_test_steps(context: ConnectorContext) -> List[StepToRun]:
    """Get all the tests steps according to the connector language.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The list of tests steps.
    """
    if _get_test_steps := LANGUAGE_MAPPING["get_test_steps"].get(context.connector.language):
        return _get_test_steps(context)
    else:
        context.logger.warning(f"No tests defined for connector language {context.connector.language}!")
        return []


async def run_connector_test_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore):
    """
    Compute the steps to run for a connector test pipeline.
    """

    steps_to_run = get_test_steps(context)

    if not context.code_tests_only:
        steps_to_run += [
            [
                StepToRun(id=CONNECTOR_TEST_STEP_ID.METADATA_VALIDATION, step=MetadataValidation(context)),
                StepToRun(id=CONNECTOR_TEST_STEP_ID.VERSION_FOLLOW_CHECK, step=VersionFollowsSemverCheck(context)),
                StepToRun(id=CONNECTOR_TEST_STEP_ID.VERSION_INC_CHECK, step=VersionIncrementCheck(context)),
                StepToRun(id=CONNECTOR_TEST_STEP_ID.QA_CHECKS, step=QaChecks(context)),
            ]
        ]

    async with semaphore:
        async with context:
            result_dict = await run_steps(
                runnables=steps_to_run,
                options=context.run_step_options,
            )

            results = result_dict.values()
            context.report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")

        return context.report
