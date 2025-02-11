#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import asyncclick as click

from pipelines.airbyte_ci.connectors.pull_request.pipeline import run_connector_pull_request_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.connectors.command import run_connector_pipeline


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
    "--changelog",
    help="Add message to the changelog for this version.",
    type=bool,
    is_flag=True,
    required=False,
    default=False,
)
@click.option(
    "--bump",
    help="Bump the metadata.yaml version. Can be `major`, `minor`, or `patch`.",
    type=click.Choice(["patch", "minor", "major"]),
    required=False,
    default=None,
)
@click.pass_context
async def pull_request(
    ctx: click.Context, message: str, branch_id: str, report: bool, title: str, body: str, changelog: bool, bump: str | None
) -> bool:
    if not ctx.obj["ci_github_access_token"]:
        raise click.ClickException(
            "GitHub access token is required to create or simulate a pull request. Set the CI_GITHUB_ACCESS_TOKEN environment variable."
        )
    return await run_connector_pipeline(
        ctx,
        "Create pull request",
        report,
        run_connector_pull_request_pipeline,
        message,
        branch_id,
        title,
        body,
    )
