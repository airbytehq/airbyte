#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List

from ci_connector_ops.pipelines.bases import StepResult
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.tests import java_connectors, python_connectors
from ci_connector_ops.utils import ConnectorLanguage

LANGUAGE_MAPPING = {
    "run_all_tests": {
        ConnectorLanguage.PYTHON: python_connectors.run_all_tests,
        ConnectorLanguage.LOW_CODE: python_connectors.run_all_tests,
        ConnectorLanguage.JAVA: java_connectors.run_all_tests,
    },
    "run_code_format_checks": {
        ConnectorLanguage.PYTHON: python_connectors.run_code_format_checks,
        ConnectorLanguage.LOW_CODE: python_connectors.run_code_format_checks,
        # ConnectorLanguage.JAVA: java_connectors.run_code_format_checks
    },
}


async def run_code_format_checks(context: ConnectorTestContext) -> List[StepResult]:
    if _run_code_format_checks := LANGUAGE_MAPPING["run_code_format_checks"].get(context.connector.language):
        return await _run_code_format_checks(context)
    else:
        context.logger.warning(f"No code format checks defined for connector language {context.connector.language}!")
        return []


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    if _run_all_tests := LANGUAGE_MAPPING["run_all_tests"].get(context.connector.language):
        return await _run_all_tests(context)
    else:
        context.logger.warning(f"No tests defined for connector language {context.connector.language}!")
        return []
