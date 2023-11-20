#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module is the CLI entrypoint to the airbyte-ci commands."""

import importlib
import logging
import multiprocessing
import os
import sys
from pathlib import Path
from typing import List, Optional

import asyncclick as click
import docker
import git
from github import PullRequest
from pipelines import main_logger
from pipelines.cli.click_decorators import click_append_to_context_object, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.cli.telemetry import click_track_command
from pipelines.consts import DAGGER_WRAP_ENV_VAR_NAME, LOCAL_PIPELINE_PACKAGE_PATH, CIContext
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


def display_welcome_message() -> None:
    print(
        """
        ╔─────────────────────────────────────────────────────────────────────────────────────────────────╗
        │                                                                                                 │
        │                                                                                                 │
        │    /$$$$$$  /$$$$$$ /$$$$$$$  /$$$$$$$  /$$     /$$ /$$$$$$$$ /$$$$$$$$       /$$$$$$  /$$$$$$  │
        │   /$$__  $$|_  $$_/| $$__  $$| $$__  $$|  $$   /$$/|__  $$__/| $$_____/      /$$__  $$|_  $$_/  │
        │  | $$  \ $$  | $$  | $$  \ $$| $$  \ $$ \  $$ /$$/    | $$   | $$           | $$  \__/  | $$    │
        │  | $$$$$$$$  | $$  | $$$$$$$/| $$$$$$$   \  $$$$/     | $$   | $$$$$ /$$$$$$| $$        | $$    │
        │  | $$__  $$  | $$  | $$__  $$| $$__  $$   \  $$/      | $$   | $$__/|______/| $$        | $$    │
        │  | $$  | $$  | $$  | $$  \ $$| $$  \ $$    | $$       | $$   | $$           | $$    $$  | $$    │
        │  | $$  | $$ /$$$$$$| $$  | $$| $$$$$$$/    | $$       | $$   | $$$$$$$$     |  $$$$$$/ /$$$$$$  │
        │  |__/  |__/|______/|__/  |__/|_______/     |__/       |__/   |________/      \______/ |______/  │
        │                                                                                                 │
        │                                                                                                 │
        ╚─────────────────────────────────────────────────────────────────────────────────────────────────╝
        """  # noqa: W605
    )


def check_up_to_date(throw_as_error=False) -> bool:
    """Check if the installed version of pipelines is up to date."""
    latest_version = get_latest_version()
    if latest_version != __installed_version__:
        upgrade_error_message = f"""
        🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

        airbyte-ci is not up to date. Installed version: {__installed_version__}. Latest version: {latest_version}
        Please run `pipx reinstall pipelines` to upgrade to the latest version.

        🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
        """

        if throw_as_error:
            raise Exception(upgrade_error_message)
        else:
            logging.warning(upgrade_error_message)
            return False

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


async def get_modified_files(
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
        return await get_modified_files_in_commit(git_branch, git_revision, is_local)
    if ci_context is CIContext.PULL_REQUEST and pull_request is not None:
        return get_modified_files_in_pull_request(pull_request)
    if ci_context is CIContext.MANUAL:
        if git_branch == "master":
            return await get_modified_files_in_commit(git_branch, git_revision, is_local)
        else:
            return await get_modified_files_in_branch(git_branch, git_revision, diffed_branch, is_local)
    return await get_modified_files_in_branch(git_branch, git_revision, diffed_branch, is_local)


def log_git_info(ctx: click.Context):
    main_logger.info("Running airbyte-ci in CI mode.")
    main_logger.info(f"CI Context: {ctx.obj['ci_context']}")
    main_logger.info(f"CI Report Bucket Name: {ctx.obj['ci_report_bucket_name']}")
    main_logger.info(f"Git Branch: {ctx.obj['git_branch']}")
    main_logger.info(f"Git Revision: {ctx.obj['git_revision']}")
    main_logger.info(f"GitHub Workflow Run ID: {ctx.obj['gha_workflow_run_id']}")
    main_logger.info(f"GitHub Workflow Run URL: {ctx.obj['gha_workflow_run_url']}")
    main_logger.info(f"Pull Request Number: {ctx.obj['pull_request_number']}")
    main_logger.info(f"Pipeline Start Timestamp: {ctx.obj['pipeline_start_timestamp']}")
    main_logger.info(f"Modified Files: {ctx.obj['modified_files']}")


def _get_gha_workflow_run_url(ctx: click.Context) -> Optional[str]:
    gha_workflow_run_id = ctx.obj["gha_workflow_run_id"]
    if not gha_workflow_run_id:
        return None

    return f"https://github.com/airbytehq/airbyte/actions/runs/{gha_workflow_run_id}"


def _get_pull_request(ctx: click.Context) -> PullRequest or None:
    pull_request_number = ctx.obj["pull_request_number"]
    ci_github_access_token = ctx.obj["ci_github_access_token"]

    can_get_pull_request = pull_request_number and ci_github_access_token
    if not can_get_pull_request:
        return None

    return github.get_pull_request(pull_request_number, ci_github_access_token)


def check_local_docker_configuration():
    try:
        docker_client = docker.from_env()
    except Exception as e:
        raise click.UsageError(f"Could not connect to docker daemon: {e}")
    daemon_info = docker_client.info()
    docker_cpus_count = daemon_info["NCPU"]
    local_cpus_count = multiprocessing.cpu_count()
    if docker_cpus_count < local_cpus_count:
        logging.warning(
            f"Your docker daemon is configured with less CPUs than your local machine ({docker_cpus_count} vs. {local_cpus_count}). This may slow down the airbyte-ci execution. Please consider increasing the number of CPUs allocated to your docker daemon in the Resource Allocation settings of Docker."
        )


def is_dagger_run_enabled_by_default() -> bool:
    dagger_run_by_default = [
        ["connectors", "test"],
        ["connectors", "build"],
        ["test"],
        ["metadata_service"],
    ]

    for command_tokens in dagger_run_by_default:
        if all(token in sys.argv for token in command_tokens):
            return True

    return False


def check_dagger_wrap():
    """
    Check if the command is already wrapped by dagger run.
    This is useful to avoid infinite recursion when calling dagger run from dagger run.
    """
    return os.getenv(DAGGER_WRAP_ENV_VAR_NAME) == "true"


def is_current_process_wrapped_by_dagger_run() -> bool:
    """
    Check if the current process is wrapped by dagger run.
    """
    called_with_dagger_run = check_dagger_wrap()
    main_logger.info(f"Called with dagger run: {called_with_dagger_run}")
    return called_with_dagger_run


async def get_modified_files_str(ctx: click.Context):
    modified_files = await get_modified_files(
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj["diffed_branch"],
        ctx.obj["is_local"],
        ctx.obj["ci_context"],
        ctx.obj["pull_request"],
    )
    return transform_strs_to_paths(modified_files)


# COMMANDS


@click.group(
    cls=LazyGroup,
    help="Airbyte CI top-level command group.",
    lazy_subcommands={
        "connectors": "pipelines.airbyte_ci.connectors.commands.connectors",
        "format": "pipelines.airbyte_ci.format.commands.format_code",
        "metadata": "pipelines.airbyte_ci.metadata.commands.metadata",
        "test": "pipelines.airbyte_ci.test.commands.test",
    },
)
@click.version_option(__installed_version__)
@click.option("--enable-dagger-run/--disable-dagger-run", default=is_dagger_run_enabled_by_default)
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
@click.option("--ci-artifact-bucket-name", envvar="CI_ARTIFACT_BUCKET_NAME", type=str)
@click.option(
    "--ci-gcs-credentials",
    help="The service account to use during CI.",
    type=click.STRING,
    required=False,  # Not required for pre-release or local pipelines
    envvar="GCP_GSM_CREDENTIALS",
)
@click.option("--ci-job-key", envvar="CI_JOB_KEY", type=str)
@click.option("--s3-build-cache-access-key-id", envvar="S3_BUILD_CACHE_ACCESS_KEY_ID", type=str)
@click.option("--s3-build-cache-secret-key", envvar="S3_BUILD_CACHE_SECRET_KEY", type=str)
@click.option("--show-dagger-logs/--hide-dagger-logs", default=False, type=bool)
@click_track_command
@click_merge_args_into_context_obj
@click_append_to_context_object("is_ci", lambda ctx: not ctx.obj["is_local"])
@click_append_to_context_object("gha_workflow_run_url", _get_gha_workflow_run_url)
@click_append_to_context_object("pull_request", _get_pull_request)
@click_append_to_context_object("modified_files", get_modified_files_str)
@click.pass_context
@click_ignore_unused_kwargs
async def airbyte_ci(ctx: click.Context):  # noqa D103
    display_welcome_message()

    if ctx.obj["enable_dagger_run"] and not is_current_process_wrapped_by_dagger_run():
        main_logger.debug("Re-Running airbyte-ci with dagger run.")
        from pipelines.cli.dagger_run import call_current_command_with_dagger_run

        call_current_command_with_dagger_run()
        return

    if ctx.obj["is_local"]:
        # This check is meaningful only when running locally
        # In our CI the docker host used by the Dagger Engine is different from the one used by the runner.
        check_local_docker_configuration()

    check_up_to_date(throw_as_error=ctx.obj["is_local"])

    if not ctx.obj["is_local"]:
        log_git_info(ctx)


set_working_directory_to_root()

if __name__ == "__main__":
    airbyte_ci()
