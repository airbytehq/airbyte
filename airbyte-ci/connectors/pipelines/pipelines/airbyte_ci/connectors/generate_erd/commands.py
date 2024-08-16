#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List

import asyncclick as click

from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.generate_erd.pipeline import run_connector_generate_erd_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.connectors.command import run_connector_pipeline


@click.command(
    cls=DaggerPipelineCommand,
    short_help="Generate ERD",
)
@click.option(
    "--report",
    is_flag=True,
    type=bool,
    default=False,
    help="Auto open report browser.",
)
@click.option(
    "--skip-step",
    "-x",
    "skip_steps",
    multiple=True,
    type=click.Choice([step_id.value for step_id in CONNECTOR_TEST_STEP_ID]),
    help="Skip a step by name. Can be used multiple times to skip multiple steps.",
)
@click.pass_context
async def generate_erd(ctx: click.Context, report: bool, skip_steps: List[str]) -> bool:
    return await run_connector_pipeline(
        ctx,
        "Generate ERD schema",
        report,
        run_connector_generate_erd_pipeline,
        skip_steps,
    )
