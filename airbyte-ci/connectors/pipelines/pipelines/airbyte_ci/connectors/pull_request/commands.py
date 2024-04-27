#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import asyncclick as click
from pipelines.helpers.connectors.command import run_connector_pipeline
from pipelines.airbyte_ci.connectors.pull_request.pipeline import run_connector_pull_request
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.git import get_modified_files
from pipelines.helpers.utils import transform_strs_to_paths


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
    modified_files = transform_strs_to_paths(
        await get_modified_files(
            ctx.obj["git_branch"],
            ctx.obj["git_revision"],
            ctx.obj["diffed_branch"],
            ctx.obj["is_local"],
            ctx.obj["ci_context"],
            ctx.obj["git_repo_url"],
        )
    )
    return await run_connector_pipeline(ctx, "Create pull request", run_connector_pull_request, report, set(modified_files))
