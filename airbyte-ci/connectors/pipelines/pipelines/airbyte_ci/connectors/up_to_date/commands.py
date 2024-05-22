#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List

import asyncclick as click
from pipelines.airbyte_ci.connectors.up_to_date.pipeline import run_connector_up_to_date_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.connectors.command import run_connector_pipeline


@click.command(
    cls=DaggerPipelineCommand,
    short_help="Get the selected Python connectors up to date.",
)
@click.option(
    "--dev",
    type=bool,
    default=False,
    is_flag=True,
    help="Force update when there are only dev changes.",
)
@click.option(
    "--dep",
    type=str,
    multiple=True,
    default=[],
    help="Give a specific set of `poetry add` dependencies to update. For example: --dep airbyte-cdk==0.80.0 --dep pytest@^6.2",
)
@click.option(
    "--report",
    is_flag=True,
    type=bool,
    default=False,
    help="Auto open report browser.",
)
@click.option(
    "--pull",
    is_flag=True,
    type=bool,
    default=False,
    help="Create a pull request.",
)
@click.option(
    "--no-bump",
    is_flag=True,
    type=bool,
    default=False,
    help="Don't bump or changelog",
)

# TODO: flag to skip regression tests
@click.pass_context
async def up_to_date(
    ctx: click.Context,
    dev: bool,
    pull: bool,
    dep: List[str],
    report: bool,
    no_bump: bool,
) -> bool:

    if not ctx.obj["ci_github_access_token"]:
        raise click.ClickException(
            "GitHub access token is required to create or simulate a pull request. Set the CI_GITHUB_ACCESS_TOKEN environment variable."
        )

    return await run_connector_pipeline(
        ctx,
        "Get Python connector up to date",
        report,
        run_connector_up_to_date_pipeline,
        dev,
        pull,
        no_bump,
        dep,
    )
