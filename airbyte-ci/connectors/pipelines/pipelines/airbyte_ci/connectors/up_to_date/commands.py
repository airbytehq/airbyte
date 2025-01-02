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
    short_help="Get the selected connectors up to date.",
)
@click.option(
    "--dep",
    type=str,
    multiple=True,
    default=[],
    help="Give a specific set of `poetry add` dependencies to update. For example: --dep airbyte-cdk==0.80.0 --dep pytest@^6.2",
)
@click.option(
    "--create-prs",
    is_flag=True,
    type=bool,
    default=False,
    help="Create pull requests for updated connectors",
)
@click.option(
    "--auto-merge",
    is_flag=True,
    type=bool,
    default=False,
    help="Set the auto-merge label on the create pull requests",
)
@click.option(
    "--no-bump",
    is_flag=True,
    type=bool,
    default=False,
    help="Don't bump or changelog",
)
@click.option(
    "--open-reports",
    is_flag=True,
    type=bool,
    default=False,
    help="Auto open reports in browser",
)
@click.pass_context
async def up_to_date(
    ctx: click.Context,
    dep: List[str],
    create_prs: bool,
    auto_merge: bool,
    no_bump: bool,
    open_reports: bool,
) -> bool:
    if create_prs and not ctx.obj["ci_github_access_token"]:
        raise click.ClickException(
            "GitHub access token is required to create or simulate a pull request. Set the CI_GITHUB_ACCESS_TOKEN environment variable."
        )

    return await run_connector_pipeline(
        ctx,
        "Get Python connector up to date",
        open_reports,
        run_connector_up_to_date_pipeline,
        create_prs,
        auto_merge,
        dep,
        not no_bump,
    )
