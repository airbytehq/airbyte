#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module is the CLI entrypoint to the airbyte-ci commands."""

import importlib
import logging
import multiprocessing
import os
import sys
from typing import List, Optional

import asyncclick as click
import dagger
import docker
import git
from github import PullRequest
from pipelines import main_logger
from pipelines.cli.click_decorators import click_append_to_context_object, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.cli.telemetry import click_track_command
from pipelines.consts import DAGGER_WRAP_ENV_VAR_NAME, LOCAL_PIPELINE_PACKAGE_PATH, CIContext
from pipelines.helpers import github
from pipelines.helpers.git import get_airbyte_repo_dir, get_target_repo_state
from pipelines.helpers.utils import get_current_epoch_time
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context

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


def get_repo_dir_from_local_path(dagger_client, target_repo, airbyte_ci_ignore) -> dagger.Directory:
    return dagger_client.host().directory(target_repo, exclude=airbyte_ci_ignore)


def get_repo_dir_from_remote_url(dagger_client, target_url: str, branch: Optional[str] = None, commit: Optional[str] = None) -> git.Repo:
    """Get the git repo from the target directory."""
    if branch is None and commit is None:
        raise click.UsageError("Either branch or commit must be set.")
    if commit:
        git_ref = dagger_client.git(target_url).commit(commit)
    else:
        git_ref = dagger_client.git(target_url).branch(branch)
    return git_ref.tree()


def get_repo_dir(
    dagger_client, local_repo, target_repo, airbyte_ci_ignore: List[str], branch: Optional[str] = None, commit: Optional[str] = None
) -> git.Repo:
    if local_repo:
        return get_repo_dir_from_local_path(dagger_client, target_repo, airbyte_ci_ignore)
    else:
        return get_repo_dir_from_remote_url(dagger_client, target_repo, branch, commit)


def set_working_directory_to_repo(repo: git.Repo) -> None:
    """Set the working directory to the root of the repo found in the target directory."""
    working_dir = repo.working_tree_dir
    logging.info(f"Setting working directory to the root of the repo {working_dir}")
    os.chdir(working_dir)


def log_git_info(ctx: click.Context):
    main_logger.info("Running airbyte-ci in CI mode.")
    main_logger.info(f"CI Context: {ctx.obj['ci_context']}")
    main_logger.info(f"CI Report Bucket Name: {ctx.obj['ci_report_bucket_name']}")
    main_logger.info(f"Git head sha: {ctx.obj['target_repo_state'].head_sha}")
    main_logger.info(f"Diffed git ref: {ctx.obj['target_repo_state'].diffed_git_ref}")
    main_logger.info(f"Is airbyte-repo: {ctx.obj['target_repo_state'].is_airbyte_repo}")
    main_logger.info(f"GitHub Workflow Run ID: {ctx.obj['gha_workflow_run_id']}")
    main_logger.info(f"GitHub Workflow Run URL: {ctx.obj['gha_workflow_run_url']}")
    main_logger.info(f"Pull Request Number: {ctx.obj['pull_request_number']}")
    main_logger.info(f"Pipeline Start Timestamp: {ctx.obj['pipeline_start_timestamp']}")
    main_logger.info(f"Modified Files: {ctx.obj['target_repo_state'].modified_files}")


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
@click.option("--git-branch", envvar="CI_GIT_BRANCH")
@click.option("--git-revision", envvar="CI_GIT_REVISION")
@click.option(
    "--diffed-git-ref",
    help="Git reference to which the git diff will happen to detect new or modified connectors",
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
@click.option("--target-repo", default=".")
@click_track_command
@click_merge_args_into_context_obj
@click_append_to_context_object("is_ci", lambda ctx: not ctx.obj["is_local"])
@click_append_to_context_object("gha_workflow_run_url", _get_gha_workflow_run_url)
@click_append_to_context_object("pull_request", _get_pull_request)
@click.pass_context
@click_ignore_unused_kwargs
@pass_pipeline_context
async def airbyte_ci(ctx: click.Context, pipeline_context: ClickPipelineContext):  # noqa D103
    dagger_client = await pipeline_context.get_dagger_client()
    ctx.obj["airbyte_repo_dir"] = await get_airbyte_repo_dir(dagger_client)
    ctx.obj["target_repo_state"] = await get_target_repo_state(dagger_client, ctx)
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

    # TODO figure how to check up to date when running outside of airbyte repo
    # check_up_to_date(throw_as_error=ctx.obj["is_local"])

    if not ctx.obj["is_local"]:
        log_git_info(ctx)


if __name__ == "__main__":
    airbyte_ci()
