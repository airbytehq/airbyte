#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module is the CLI entrypoint to the airbyte-ci commands."""

import click
from ci_connector_ops.pipelines import github
from ci_connector_ops.pipelines.bases import CIContext
from ci_connector_ops.pipelines.utils import (
    get_current_epoch_time,
    get_current_git_branch,
    get_current_git_revision,
    get_modified_files_in_branch,
    get_modified_files_in_commit,
)

from .groups.connectors import connectors
from .groups.metadata import metadata


@click.group(help="Airbyte CI top-level command group.")
@click.option("--is-local/--is-ci", default=True)
@click.option("--git-branch", default=get_current_git_branch, envvar="CI_GIT_BRANCH")
@click.option("--git-revision", default=get_current_git_revision, envvar="CI_GIT_REVISION")
@click.option(
    "--diffed-branch",
    help="Branch to which the git diff will happen to detect new or modified connectors",
    default="origin/master",
    type=str,
)
@click.option("--gha-workflow-run-id", help="[CI Only] The run id of the GitHub action workflow", default=None, type=str)
@click.option("--ci-context", default=CIContext.MANUAL, envvar="CI_CONTEXT", type=click.Choice(CIContext))
@click.option("--pipeline-start-timestamp", default=get_current_epoch_time, envvar="CI_PIPELINE_START_TIMESTAMP", type=int)
@click.option("--pull-request-number", envvar="PULL_REQUEST_NUMBER", type=int)
@click.option("--ci-github-access-token", envvar="CI_GITHUB_ACCESS_TOKEN", type=str)
@click.pass_context
def airbyte_ci(
    ctx: click.Context,
    is_local: bool,
    git_branch: str,
    git_revision: str,
    diffed_branch: str,
    gha_workflow_run_id: str,
    ci_context: str,
    pipeline_start_timestamp: int,
    pull_request_number: int,
    ci_github_access_token: str,
):  # noqa D103
    ctx.ensure_object(dict)
    ctx.obj["is_local"] = is_local
    ctx.obj["is_ci"] = not is_local
    ctx.obj["git_branch"] = git_branch
    ctx.obj["git_revision"] = git_revision
    ctx.obj["gha_workflow_run_id"] = gha_workflow_run_id
    ctx.obj["gha_workflow_run_url"] = (
        f"https://github.com/airbytehq/airbyte/actions/runs/{gha_workflow_run_id}" if gha_workflow_run_id else None
    )
    ctx.obj["ci_context"] = ci_context
    ctx.obj["pipeline_start_timestamp"] = pipeline_start_timestamp
    ctx.obj["modified_files_in_branch"] = get_modified_files_in_branch(git_branch, git_revision, diffed_branch, is_local)
    ctx.obj["modified_files_in_commit"] = get_modified_files_in_commit(git_branch, git_revision, is_local)
    ctx.obj["modified_files"] = ctx.obj["modified_files_in_commit"] if git_branch == "master" else ctx.obj["modified_files_in_branch"]

    if pull_request_number and ci_github_access_token:
        ctx.obj["pull_request"] = github.get_pull_request(pull_request_number, ci_github_access_token)
    else:
        ctx.obj["pull_request"] = None
    if not is_local:
        click.echo("Running airbyte-ci in CI mode.")
        click.echo(f"CI Context: {ci_context}")
        click.echo(f"Git Branch: {git_branch}")
        click.echo(f"Git Revision: {git_revision}")
        click.echo(f"GitHub Workflow Run ID: {gha_workflow_run_id}")
        click.echo(f"GitHub Workflow Run URL: {ctx.obj['gha_workflow_run_url']}")
        click.echo(f"Pull Request Number: {pull_request_number}")
        click.echo(f"Pipeline Start Timestamp: {pipeline_start_timestamp}")


airbyte_ci.add_command(connectors)
airbyte_ci.add_command(metadata)

if __name__ == "__main__":
    airbyte_ci()
