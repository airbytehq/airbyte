#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module is the CLI entrypoint to the airbyte-ci commands."""

import importlib
import logging
import os
from pathlib import Path
from typing import List

import click
import git
from github import PullRequest
from pipelines import main_logger
from pipelines.cli.lazy_group import LazyGroup
from pipelines.cli.telemetry import track_command
from pipelines.consts import LOCAL_PIPELINE_PACKAGE_PATH, CIContext
from pipelines.helpers import github
from pipelines.helpers.git import (
    get_current_git_branch,
    get_current_git_revision,
    get_modified_files_in_branch,
    get_modified_files_in_commit,
    get_modified_files_in_pull_request,
)
from pipelines.helpers.utils import get_current_epoch_time, transform_strs_to_paths

# HELPERS

__installed_version__ = importlib.metadata.version("pipelines")


def check_up_to_date() -> bool:
    """Check if the installed version of pipelines is up to date."""
    latest_version = get_latest_version()
    if latest_version != __installed_version__:
        upgrade_error_message = f"""
        🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

        airbyte-ci is not up to date. Installed version: {__installed_version__}. Latest version: {latest_version}
        Please run `pipx reinstall pipelines` to upgrade to the latest version.

        🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
        """
        raise Exception(upgrade_error_message)

    main_logger.info(f"pipelines is up to date. Installed version: {__installed_version__}. Latest version: {latest_version}")
    return True


def get_latest_version() -> str:
    """
    Get the version of the latest release, which is just in the pyproject.toml file of the pipelines package
    as this is an internal tool, we don't need to check for the latest version on PyPI
    """
    path_to_pyproject_toml = LOCAL_PIPELINE_PACKAGE_PATH + "pyproject.toml"
    with open(path_to_pyproject_toml, "r") as f:
        for line in f.readlines():
            if "version" in line:
                return line.split("=")[1].strip().replace('"', "")
    raise Exception("Could not find version in pyproject.toml. Please ensure you are running from the root of the airbyte repo.")


def _validate_airbyte_repo(repo: git.Repo) -> bool:
    """Check if any of the remotes are the airbyte repo."""
    expected_repo_name = "airbytehq/airbyte"
    for remote in repo.remotes:
        if expected_repo_name in remote.url:
            return True

    warning_message = f"""
    ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️

    It looks like you are not running this command from the airbyte repo ({expected_repo_name}).

    If this command is run from outside the airbyte repo, it will not work properly.

    Please run this command your local airbyte project.

    ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
    """

    logging.warning(warning_message)

    return False


def get_airbyte_repo() -> git.Repo:
    """Get the airbyte repo."""
    repo = git.Repo(search_parent_directories=True)
    _validate_airbyte_repo(repo)
    return repo


def get_airbyte_repo_path_with_fallback() -> Path:
    """Get the path to the airbyte repo."""
    try:
        return get_airbyte_repo().working_tree_dir
    except git.exc.InvalidGitRepositoryError:
        logging.warning("Could not find the airbyte repo, falling back to the current working directory.")
        path = Path.cwd()
        logging.warning(f"Using {path} as the airbyte repo path.")
        return path


def set_working_directory_to_root() -> None:
    """Set the working directory to the root of the airbyte repo."""
    working_dir = get_airbyte_repo_path_with_fallback()
    logging.info(f"Setting working directory to {working_dir}")
    os.chdir(working_dir)


def get_modified_files(
    git_branch: str, git_revision: str, diffed_branch: str, is_local: bool, ci_context: CIContext, pull_request: PullRequest
) -> List[str]:
    """Get the list of modified files in the current git branch.
    If the current branch is master, it will return the list of modified files in the head commit.
    The head commit on master should be the merge commit of the latest merged pull request as we squash commits on merge.
    Pipelines like "publish on merge" are triggered on each new commit on master.

    If the CI context is a pull request, it will return the list of modified files in the pull request, without using git diff.
    If the current branch is not master, it will return the list of modified files in the current branch.
    This latest case is the one we encounter when running the pipeline locally, on a local branch, or manually on GHA with a workflow dispatch event.
    """
    if ci_context is CIContext.MASTER or ci_context is CIContext.NIGHTLY_BUILDS:
        return get_modified_files_in_commit(git_branch, git_revision, is_local)
    if ci_context is CIContext.PULL_REQUEST and pull_request is not None:
        return get_modified_files_in_pull_request(pull_request)
    if ci_context is CIContext.MANUAL:
        if git_branch == "master":
            return get_modified_files_in_commit(git_branch, git_revision, is_local)
        else:
            return get_modified_files_in_branch(git_branch, git_revision, diffed_branch, is_local)
    return get_modified_files_in_branch(git_branch, git_revision, diffed_branch, is_local)


# COMMANDS


@click.group(
    cls=LazyGroup,
    help="Airbyte CI top-level command group.",
    lazy_subcommands={
        "connectors": "pipelines.airbyte_ci.connectors.commands.connectors",
        "metadata": "pipelines.airbyte_ci.metadata.commands.metadata",
        "test": "pipelines.airbyte_ci.test.commands.test",
    },
)
@click.version_option(__installed_version__)
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
@click.option("--ci-git-user", default="octavia-squidington-iii", envvar="CI_GIT_USER", type=str)
@click.option("--ci-github-access-token", envvar="CI_GITHUB_ACCESS_TOKEN", type=str)
@click.option("--ci-report-bucket-name", envvar="CI_REPORT_BUCKET_NAME", type=str)
@click.option(
    "--ci-gcs-credentials",
    help="The service account to use during CI.",
    type=click.STRING,
    required=False,  # Not required for pre-release or local pipelines
    envvar="GCP_GSM_CREDENTIALS",
)
@click.option("--ci-job-key", envvar="CI_JOB_KEY", type=str)
@click.option("--show-dagger-logs/--hide-dagger-logs", default=False, type=bool)
@click.pass_context
@track_command
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
    ci_git_user: str,
    ci_github_access_token: str,
    ci_report_bucket_name: str,
    ci_gcs_credentials: str,
    ci_job_key: str,
    show_dagger_logs: bool,
):  # noqa D103
    ctx.ensure_object(dict)
    check_up_to_date()
    ctx.obj["is_local"] = is_local
    ctx.obj["is_ci"] = not is_local
    ctx.obj["git_branch"] = git_branch
    ctx.obj["git_revision"] = git_revision
    ctx.obj["gha_workflow_run_id"] = gha_workflow_run_id
    ctx.obj["gha_workflow_run_url"] = (
        f"https://github.com/airbytehq/airbyte/actions/runs/{gha_workflow_run_id}" if gha_workflow_run_id else None
    )
    ctx.obj["ci_context"] = ci_context
    ctx.obj["ci_report_bucket_name"] = ci_report_bucket_name
    ctx.obj["ci_gcs_credentials"] = ci_gcs_credentials
    ctx.obj["ci_git_user"] = ci_git_user
    ctx.obj["ci_github_access_token"] = ci_github_access_token
    ctx.obj["ci_job_key"] = ci_job_key
    ctx.obj["pipeline_start_timestamp"] = pipeline_start_timestamp
    ctx.obj["show_dagger_logs"] = show_dagger_logs

    if pull_request_number and ci_github_access_token:
        ctx.obj["pull_request"] = github.get_pull_request(pull_request_number, ci_github_access_token)
    else:
        ctx.obj["pull_request"] = None

    ctx.obj["modified_files"] = transform_strs_to_paths(
        get_modified_files(git_branch, git_revision, diffed_branch, is_local, ci_context, ctx.obj["pull_request"])
    )

    if not is_local:
        main_logger.info("Running airbyte-ci in CI mode.")
        main_logger.info(f"CI Context: {ci_context}")
        main_logger.info(f"CI Report Bucket Name: {ci_report_bucket_name}")
        main_logger.info(f"Git Branch: {git_branch}")
        main_logger.info(f"Git Revision: {git_revision}")
        main_logger.info(f"GitHub Workflow Run ID: {gha_workflow_run_id}")
        main_logger.info(f"GitHub Workflow Run URL: {ctx.obj['gha_workflow_run_url']}")
        main_logger.info(f"Pull Request Number: {pull_request_number}")
        main_logger.info(f"Pipeline Start Timestamp: {pipeline_start_timestamp}")
        main_logger.info(f"Modified Files: {ctx.obj['modified_files']}")


set_working_directory_to_root()

if __name__ == "__main__":
    airbyte_ci()
