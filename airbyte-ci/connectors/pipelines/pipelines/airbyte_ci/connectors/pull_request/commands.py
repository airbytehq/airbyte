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
    "-m",
    "--message",
    help="Commit message and pull request title and changelog (if enabled).",
    type=str,
    required=True,
)
@click.option(
    "-b",
    "--branch_id",
    help="update a branch named <branch_id>/<connector-name> instead generating one from the message.",
    type=str,
    required=True,
)
@click.option(
    "--report",
    is_flag=True,
    type=bool,
    default=False,
    help="Auto open report browser.",
)
@click.option(
    "--title",
    help="Title of the PR to be created or edited (optional - defaults to message or no change).",
    type=str,
    required=False,
)
@click.option(
    "--body",
    help="Body of the PR to be created or edited (optional - defaults to empty or not change).",
    type=str,
    required=False,
)
@click.option(
    "--dry-run",
    help="Don't actually make the pull requests. Just print the files that would be changed.",
    type=bool,
    is_flag=True,
    required=False,
    default=False,
)
@click.pass_context
async def pull_request(ctx: click.Context, message: str, branch_id: str, report: bool, title: str, body: str, dry_run: bool) -> bool:
    if not ctx.obj["ci_github_access_token"]:
        raise click.ClickException(
            "GitHub access token is required to create a pull request. Set the CI_GITHUB_ACCESS_TOKEN environment variable."
        )

    full_path_modified_files = transform_strs_to_paths(
        await get_modified_files(
            ctx.obj["git_branch"],
            ctx.obj["git_revision"],
            ctx.obj["diffed_branch"],
            ctx.obj["is_local"],
            ctx.obj["ci_context"],
            ctx.obj["git_repo_url"],
        )
    )
    return await run_connector_pipeline(
        ctx,
        "Create pull request",
        report,
        run_connector_pull_request,
        message,
        branch_id,
        title,
        body,
        dry_run,
        set(full_path_modified_files),
    )
