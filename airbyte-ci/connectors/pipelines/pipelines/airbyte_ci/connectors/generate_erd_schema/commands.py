#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import asyncclick as click
from pipelines.airbyte_ci.connectors.generate_erd_schema.pipeline import run_connector_generate_erd_schema_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.connectors.command import run_connector_pipeline
from pipelines.helpers.connectors.format import verify_formatters


@click.command(
    cls=DaggerPipelineCommand,
    short_help="Generate ERD schema",
)
@click.option(
    "--report",
    is_flag=True,
    type=bool,
    default=False,
    help="Auto open report browser.",
)
@click.pass_context
async def generate_erd_schema(ctx: click.Context, report: bool) -> bool:
    verify_formatters()
    return await run_connector_pipeline(
        ctx,
        "Generate ERD schema",
        report,
        run_connector_generate_erd_schema_pipeline,
    )
