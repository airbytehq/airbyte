#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups functions made to run checks (static code analysis) for a specific connector given a test context."""

from typing import List

import asyncer
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.models import Step, StepResult
from ci_connector_ops.pipelines.utils import get_step_result

RUN_BLACK_CMD = ["python", "-m", "black", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check", "."]
RUN_ISORT_CMD = ["python", "-m", "isort", f"--settings-file=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check-only", "--diff", "."]
RUN_FLAKE_CMD = ["python", "-m", "pflake8", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "."]


async def run_qa_checks(context: ConnectorTestContext, step=Step.QA_CHECKS) -> StepResult:
    """Runs our QA checks on a connector.
    The QA checks are defined in this module:
    https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/qa_checks.py

    Args:
        context (ConnectorTestContext): The current test context, providing a connector object, a dagger client and a repository directory.
    Returns:
        StepResult: Failure or success of the QA checks with stdout and stdout.
    """
    ci_connector_ops = await environments.with_ci_connector_ops(context)
    ci_connector_ops = step.get_dagger_pipeline(ci_connector_ops)
    filtered_repo = context.get_repo_dir(
        include=[
            str(context.connector.code_directory),
            str(context.connector.documentation_file_path),
            str(context.connector.icon_path),
            "airbyte-config/init/src/main/resources/seed/source_definitions.yaml",
            "airbyte-config/init/src/main/resources/seed/destination_definitions.yaml",
        ],
    )
    qa_checks = (
        ci_connector_ops.with_mounted_directory("/airbyte", filtered_repo)
        .with_workdir("/airbyte")
        .with_exec(["run-qa-checks", f"connectors/{context.connector.technical_name}"])
    )
    return await get_step_result(qa_checks, step)


async def run_code_format_checks(context: ConnectorTestContext, step=Step.CODE_FORMAT_CHECKS) -> StepResult:
    """Run a code format check on the container source code.
    We call black, isort and flake commands:
    - Black formats the code: fails if the code is not formatted.
    - Isort checks the import orders: fails if the import are not properly ordered.
    - Flake enforces style-guides: fails if the style-guide is not followed.
    Args:
        context (ConnectorTestContext): The current test context, providing a connector object, a dagger client and a repository directory.
        step (Step): The step in which the code format checks are run. Defaults to Step.CODE_FORMAT_CHECKS
    Returns:
        StepResult: Failure or success of the code format checks with stdout and stdout.
    """

    connector_under_test = environments.with_airbyte_connector(context)
    connector_under_test = step.get_dagger_pipeline(connector_under_test)
    formatter = (
        connector_under_test.with_exec(["echo", "Running black"])
        .with_exec(RUN_BLACK_CMD)
        .with_exec(["echo", "Running Isort"])
        .with_exec(RUN_ISORT_CMD)
        .with_exec(["echo", "Running Flake"])
        .with_exec(RUN_FLAKE_CMD)
    )
    return await get_step_result(formatter, step)


ALL_CHECKS = [run_code_format_checks, run_qa_checks]


async def run_checks(context: ConnectorTestContext) -> List[StepResult]:
    """Concurrently run all the checks coroutines defined in ALL_CHECKS.

    Args:
        context (ConnectorTestContext): The current test context, providing a connector object, a dagger client and a repository directory.

    Returns:
        List[StepResult]: List of checks results.
    """
    soon_results = []
    async with asyncer.create_task_group() as task_group:
        for check in ALL_CHECKS:
            soon_results.append(task_group.soonify(check)(context))
    return [soon_result.value for soon_result in soon_results]
