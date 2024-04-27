#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import asyncclick as click
from pipelines.airbyte_ci.connectors.helpers.command import run_connector_pipeline
from pipelines.airbyte_ci.connectors.pull_request.pipeline import run_connector_pull_request
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand


@click.command(
    cls=DaggerPipelineCommand,
    short_help="Create a pull request for changed files in the connector repository.",
)
@click.option(
    "--report",
    is_flag=True,
    type=bool,
    default=False,
    help="Auto open report browser.",
)
@click.pass_context
async def pull_request(ctx: click.Context, report: bool) -> bool:
    return await run_connector_pipeline(ctx, "Create pull request", run_connector_pull_request, enable_report_auto_open=report)
