#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch tests steps according to the connector under test language."""

import itertools
from typing import List

import anyio
import asyncer
from ci_connector_ops.pipelines.bases import ConnectorReport, StepResult
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.pipelines.metadata import MetadataValidation
from ci_connector_ops.pipelines.tests import java_connectors, python_connectors
from ci_connector_ops.pipelines.tests.common import QaChecks, VersionFollowsSemverCheck, VersionIncrementCheck
from ci_connector_ops.utils import METADATA_FILE_NAME, ConnectorLanguage

LANGUAGE_MAPPING = {
    "run_all_tests": {
        ConnectorLanguage.PYTHON: python_connectors.run_all_tests,
        ConnectorLanguage.LOW_CODE: python_connectors.run_all_tests,
        ConnectorLanguage.JAVA: java_connectors.run_all_tests,
    },
    "run_code_format_checks": {
        # TODO: re-enable when we have a code formatter
        # ConnectorLanguage.PYTHON: python_connectors.run_code_format_checks,
        # ConnectorLanguage.LOW_CODE: python_connectors.run_code_format_checks,
        # ConnectorLanguage.JAVA: java_connectors.run_code_format_checks
    },
}


async def run_metadata_validation(context: ConnectorContext) -> List[StepResult]:
    """Run the metadata validation on a connector.
    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The results of the metadata validation steps.
    """
    context.logger.info("Run metadata validation.")
    return [await MetadataValidation(context, context.connector.code_directory / METADATA_FILE_NAME).run()]


async def run_version_checks(context: ConnectorContext) -> List[StepResult]:
    """Run the version checks on a connector.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The results of the version checks steps.
    """
    context.logger.info("Run version checks.")
    return [await VersionFollowsSemverCheck(context).run(), await VersionIncrementCheck(context).run()]


async def run_qa_checks(context: ConnectorContext) -> List[StepResult]:
    """Run the QA checks on a connector.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The results of the QA checks steps.
    """
    context.logger.info("Run QA checks.")
    return [await QaChecks(context).run()]


async def run_code_format_checks(context: ConnectorContext) -> List[StepResult]:
    """Run the code format checks according to the connector language.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The results of the code format checks steps.
    """
    if _run_code_format_checks := LANGUAGE_MAPPING["run_code_format_checks"].get(context.connector.language):
        context.logger.info("Run code format checks.")
        return await _run_code_format_checks(context)
    else:
        context.logger.warning(f"No code format checks defined for connector language {context.connector.language}!")
        return []


async def run_all_tests(context: ConnectorContext) -> List[StepResult]:
    """Run all the tests steps according to the connector language.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The results of the tests steps.
    """
    if _run_all_tests := LANGUAGE_MAPPING["run_all_tests"].get(context.connector.language):
        return await _run_all_tests(context)
    else:
        context.logger.warning(f"No tests defined for connector language {context.connector.language}!")
        return []


async def run_connector_test_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """Run a test pipeline for a single connector.

    A visual DAG can be found on the README.md file of the pipelines modules.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        ConnectorReport: The test reports holding tests results.
    """
    async with semaphore:
        async with context:
            async with asyncer.create_task_group() as task_group:
                tasks = [
                    task_group.soonify(run_metadata_validation)(context),
                    task_group.soonify(run_version_checks)(context),
                    task_group.soonify(run_qa_checks)(context),
                    task_group.soonify(run_code_format_checks)(context),
                    task_group.soonify(run_all_tests)(context),
                ]
            results = list(itertools.chain(*(task.value for task in tasks)))
            context.report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")

        return context.report
