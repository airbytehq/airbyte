#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch tests steps according to the connector under test language."""

import itertools
from typing import List

import anyio
import asyncer
from connector_ops.utils import METADATA_FILE_NAME, ConnectorLanguage
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.airbyte_ci.connectors.test.steps import java_connectors, python_connectors
from pipelines.airbyte_ci.connectors.test.steps.common import QaChecks, VersionFollowsSemverCheck, VersionIncrementCheck
from pipelines.airbyte_ci.metadata.pipeline import MetadataValidation
from pipelines.helpers.steps import Runnable, new_run_steps
from pipelines.models.steps import StepResult

LANGUAGE_MAPPING = {
    "run_all_tests": {
        ConnectorLanguage.PYTHON: python_connectors.run_all_tests,
        ConnectorLanguage.LOW_CODE: python_connectors.run_all_tests,
        ConnectorLanguage.JAVA: java_connectors.run_all_tests,
    },
    "get_test_steps": {
        ConnectorLanguage.PYTHON: python_connectors.get_test_steps,
        ConnectorLanguage.LOW_CODE: python_connectors.get_test_steps,
        ConnectorLanguage.JAVA: java_connectors.get_test_steps,
    },
}


def get_test_steps(context: ConnectorContext) -> List[Runnable]:
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


async def new_run_connector_test_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore):
    """
    Compute the steps to run for a connector test pipeline.
    """

    steps = get_test_steps(context)

    if not context.code_tests_only:
        steps += [
            Runnable(id="metadata_validation", step=MetadataValidation(context)),
            Runnable(id="version_follow_check", step=VersionFollowsSemverCheck(context)),
            Runnable(id="version_inc_check", step=VersionIncrementCheck(context)),
            Runnable(id="qa_checks", step=QaChecks(context)),
        ]

    async with semaphore:
        async with context:
            results = await new_run_steps(steps)
            context.report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")

        return context.report
