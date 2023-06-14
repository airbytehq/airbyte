#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch formatting steps according to the connector language."""

from __future__ import annotations

import anyio
from ci_connector_ops.pipelines.bases import ConnectorReport, StepResult
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.format import java_connectors, python_connectors
from ci_connector_ops.utils import ConnectorLanguage


class NoFormatStepForLanguageError(Exception):
    pass


LANGUAGE_FORMAT_CONNECTOR_MAPPING = {
    ConnectorLanguage.PYTHON: python_connectors.run_connector_format,
    ConnectorLanguage.LOW_CODE: python_connectors.run_connector_format,
    ConnectorLanguage.JAVA: java_connectors.run_connector_format,
}


async def run_connector_format(context: ConnectorContext) -> StepResult:
    """Run a format pipeline for a single connector."""
    if context.connector.language not in LANGUAGE_FORMAT_CONNECTOR_MAPPING:
        raise NoFormatStepForLanguageError(f"No format step for connector language {context.connector.language}.")
    return await LANGUAGE_FORMAT_CONNECTOR_MAPPING[context.connector.language](context)


async def run_connector_format_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """Run a format pipeline for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        ConnectorReport: The reports holding formats results.
    """
    step_results = []
    async with semaphore:
        async with context:
            step_results += await run_connector_format(context)
            context.report = ConnectorReport(context, step_results, name="FORMAT RESULTS")
        return context.report
