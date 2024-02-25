# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""This module groups factory like functions to dispatch tests steps according to the connector under test language."""

from __future__ import annotations

from typing import TYPE_CHECKING

import anyio
from connector_ops.utils import ConnectorLanguage  # type: ignore
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.regression_test.steps.regression_cats import get_test_steps
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.helpers.execution.run_steps import StepToRun, run_steps

if TYPE_CHECKING:

    from pipelines.helpers.execution.run_steps import STEP_TREE


async def run_connector_regression_test_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """
    Compute the steps to run for a connector test pipeline.
    """
    steps_to_run: STEP_TREE = get_test_steps(context)

    async with semaphore:
        async with context:
            result_dict = await run_steps(
                runnables=steps_to_run,
                options=context.run_step_options,
            )

            results = list(result_dict.values())
            report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")
            context.report = report

    return report
