#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch tests steps according to the connector under test language."""

from __future__ import annotations

from typing import TYPE_CHECKING

import anyio
from connector_ops.utils import ConnectorLanguage  # type: ignore

from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.airbyte_ci.connectors.test.context import ConnectorTestContext
from pipelines.airbyte_ci.connectors.test.steps import java_connectors, manifest_only_connectors, python_connectors
from pipelines.airbyte_ci.connectors.test.steps.common import QaChecks, VersionIncrementCheck
from pipelines.helpers.execution.run_steps import StepToRun, run_steps

if TYPE_CHECKING:
    from pipelines.helpers.execution.run_steps import STEP_TREE

LANGUAGE_MAPPING = {
    "get_test_steps": {
        ConnectorLanguage.PYTHON: python_connectors.get_test_steps,
        ConnectorLanguage.LOW_CODE: python_connectors.get_test_steps,
        ConnectorLanguage.MANIFEST_ONLY: manifest_only_connectors.get_test_steps,
        ConnectorLanguage.JAVA: java_connectors.get_test_steps,
    },
}


def get_test_steps(context: ConnectorTestContext) -> STEP_TREE:
    """Get all the tests steps according to the connector language.

    Args:
        context (ConnectorTestContext): The current connector context.

    Returns:
        STEP_TREE: The list of tests steps.
    """
    if _get_test_steps := LANGUAGE_MAPPING["get_test_steps"].get(context.connector.language):
        return _get_test_steps(context)
    else:
        context.logger.warning(f"No tests defined for connector language {context.connector.language}!")
        return []


async def run_connector_test_pipeline(context: ConnectorTestContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """
    Compute the steps to run for a connector test pipeline.
    """
    all_steps_to_run: STEP_TREE = []

    all_steps_to_run += get_test_steps(context)

    if not context.code_tests_only:
        static_analysis_steps_to_run = [
            [
                StepToRun(id=CONNECTOR_TEST_STEP_ID.VERSION_INC_CHECK, step=VersionIncrementCheck(context)),
                StepToRun(id=CONNECTOR_TEST_STEP_ID.QA_CHECKS, step=QaChecks(context)),
            ]
        ]
        all_steps_to_run += static_analysis_steps_to_run

    async with semaphore:
        async with context:
            result_dict = await run_steps(
                runnables=all_steps_to_run,
                options=context.run_step_options,
            )

            results = list(result_dict.values())
            report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")
            context.report = report

        return report
