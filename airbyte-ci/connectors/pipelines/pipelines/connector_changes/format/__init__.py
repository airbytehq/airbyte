#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch formatting steps according to the connector language."""

from __future__ import annotations

from connector_ops.utils import ConnectorLanguage
from pipelines.bases import ConnectorReport
from pipelines.connector_changes.format import python_connectors
from pipelines.contexts import ConnectorContext


class NoFormatStepForLanguageError(Exception):
    pass


FORMATTING_STEP_TO_CONNECTOR_LANGUAGE_MAPPING = {
    ConnectorLanguage.PYTHON: python_connectors.FormatConnectorCode,
    ConnectorLanguage.LOW_CODE: python_connectors.FormatConnectorCode,
    # ConnectorLanguage.JAVA: java_connectors.FormatConnectorCode,
}


async def run_connector_format_pipeline(
    context: ConnectorContext, semaphore, commit_and_push: bool, export_changes_to_host: bool
) -> ConnectorReport:
    """Run a format pipeline for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        ConnectorReport: The reports holding formats results.
    """
    steps_results = []
    async with context:
        FormatConnectorCode = FORMATTING_STEP_TO_CONNECTOR_LANGUAGE_MAPPING.get(context.connector.language)
        if not FormatConnectorCode:
            raise NoFormatStepForLanguageError(
                f"No formatting step found for connector {context.connector.technical_name} with language {context.connector.language}"
            )
        format_connector_code_result = await FormatConnectorCode(
            context, export_changes_to_host, commit=commit_and_push, push=commit_and_push
        ).run()
        steps_results.append(format_connector_code_result)
        context.report = ConnectorReport(context, steps_results, name="FORMAT RESULTS")
    return context.report
