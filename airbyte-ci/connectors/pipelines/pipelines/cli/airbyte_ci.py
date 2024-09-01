#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module is the CLI entrypoint to the airbyte-ci commands."""

from __future__ import annotations

# HACK! IMPORTANT! This import and function call must be the first import in this file
# This is needed to ensure that the working directory is the root of the airbyte repo
# ruff: noqa: E402
from pipelines.cli.ensure_repo_root import set_working_directory_to_root

set_working_directory_to_root()

import logging
import multiprocessing
import os
import sys
from typing import Optional

import asyncclick as click
import docker  # type: ignore
from github import PullRequest
from pipelines import main_logger
from pipelines.cli.auto_update import __installed_version__, check_for_upgrade, pre_confirm_auto_update_flag
from pipelines.cli.click_decorators import (
    CI_REQUIREMENTS_OPTION_NAME,
    click_append_to_context_object,
    click_ci_requirements_option,
    click_ignore_unused_kwargs,
    click_merge_args_into_context_obj,
)
from pipelines.cli.confirm_prompt import pre_confirm_all_flag
from pipelines.cli.lazy_group import LazyGroup
from pipelines.cli.secrets import wrap_gcp_credentials_in_secret, wrap_in_secret
from pipelines.cli.telemetry import click_track_command
from pipelines.consts import DAGGER_WRAP_ENV_VAR_NAME, LOCAL_BUILD_PLATFORM, CIContext
from pipelines.dagger.actions.connector.hooks import get_dagger_sdk_version
from pipelines.helpers import github
from pipelines.helpers.git import get_current_git_branch, get_current_git_revision
from pipelines.helpers.github import AIRBYTE_GITHUB_REPO_URL, AIRBYTE_GITHUB_REPO_URL_PREFIX
from pipelines.helpers.utils import get_current_epoch_time
from pipelines.models.secrets import InMemorySecretStore


def log_context_info(ctx: click.Context) -> None:
    main_logger.info(f"Running airbyte-ci version {__installed_version__}")
    main_logger.info(f"Running dagger version {get_dagger_sdk_version()}")
    main_logger.info("Running airbyte-ci in CI mode.")
    main_logger.info(f"CI Context: {ctx.obj['ci_context']}")
    main_logger.info(f"CI Report Bucket Name: {ctx.obj['ci_report_bucket_name']}")
    main_logger.info(f"Git Repo URL: {ctx.obj['git_repo_url']}")
    main_logger.info(f"Git Branch: {ctx.obj['git_branch']}")
    main_logger.info(f"Git Revision: {ctx.obj['git_revision']}")
    main_logger.info(f"GitHub Workflow Run ID: {ctx.obj['gha_workflow_run_id']}")
    main_logger.info(f"GitHub Workflow Run URL: {ctx.obj['gha_workflow_run_url']}")
    main_logger.info(f"Pull Request Number: {ctx.obj['pull_request_number']}")
    main_logger.info(f"Pipeline Start Timestamp: {ctx.obj['pipeline_start_timestamp']}")
    main_logger.info(f"Local build platform: {LOCAL_BUILD_PLATFORM}")


def _get_gha_workflow_run_url(ctx: click.Context) -> Optional[str]:
    gha_workflow_run_id = ctx.obj["gha_workflow_run_id"]
    if not gha_workflow_run_id:
        return None

    return f"{AIRBYTE_GITHUB_REPO_URL_PREFIX}/actions/runs/{gha_workflow_run_id}"


def _get_pull_request(ctx: click.Context) -> Optional[PullRequest.PullRequest]:
    pull_request_number = ctx.obj["pull_request_number"]
    ci_github_access_token = ctx.obj["ci_github_access_token"]

    can_get_pull_request = pull_request_number and ci_github_access_token
    if not can_get_pull_request:
        return None
    return github.get_pull_request(pull_request_number, ci_github_access_token)


def check_local_docker_configuration() -> None:
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
    if CI_REQUIREMENTS_OPTION_NAME in sys.argv:
        return False

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


def check_dagger_wrap() -> bool:
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
        "poetry": "pipelines.airbyte_ci.poetry.commands.poetry",
        "format": "pipelines.airbyte_ci.format.commands.format_code",
        "metadata": "pipelines.airbyte_ci.metadata.commands.metadata",
        "test": "pipelines.airbyte_ci.test.commands.test",
        "update": "pipelines.airbyte_ci.update.commands.update",
    },
)
@click.version_option(__installed_version__)
@pre_confirm_all_flag
@pre_confirm_auto_update_flag
@click.option("--enable-dagger-run/--disable-dagger-run", default=is_dagger_run_enabled_by_default)
@click.option("--enable-update-check/--disable-update-check", default=True)
@click.option("--enable-auto-update/--disable-auto-update", default=True)
@click.option("--is-local/--is-ci", default=True)
@click.option("--git-repo-url", default=AIRBYTE_GITHUB_REPO_URL, envvar="CI_GIT_REPO_URL")
@click.option("--git-branch", default=get_current_git_branch, envvar="CI_GIT_BRANCH")
@click.option("--git-revision", default=get_current_git_revision, envvar="CI_GIT_REVISION")
@click.option(
    "--diffed-branch",
    help="Branch to which the git diff will happen to detect new or modified connectors",
    default="master",
    type=str,
)
@click.option("--gha-workflow-run-id", help="[CI Only] The run id of the GitHub action workflow", default=None, type=str)
@click.option("--ci-context", default=CIContext.MANUAL, envvar="CI_CONTEXT", type=click.Choice([c for c in CIContext]))
@click.option("--pipeline-start-timestamp", default=get_current_epoch_time, envvar="CI_PIPELINE_START_TIMESTAMP", type=int)
@click.option("--pull-request-number", envvar="PULL_REQUEST_NUMBER", type=int)
@click.option("--ci-git-user", default="octavia-squidington-iii", envvar="CI_GIT_USER", type=str)
@click.option("--ci-github-access-token", envvar="CI_GITHUB_ACCESS_TOKEN", type=str, callback=wrap_in_secret)
@click.option("--ci-report-bucket-name", envvar="CI_REPORT_BUCKET_NAME", type=str)
@click.option("--ci-artifact-bucket-name", envvar="CI_ARTIFACT_BUCKET_NAME", type=str)
@click.option(
    "--ci-gcp-credentials",
    help="The service account to use during CI.",
    type=click.STRING,
    required=False,  # Not required for pre-release or local pipelines
    envvar="GCP_GSM_CREDENTIALS",
    callback=wrap_gcp_credentials_in_secret,
)
@click.option("--ci-job-key", envvar="CI_JOB_KEY", type=str)
@click.option("--s3-build-cache-access-key-id", envvar="S3_BUILD_CACHE_ACCESS_KEY_ID", type=str, callback=wrap_in_secret)
@click.option("--s3-build-cache-secret-key", envvar="S3_BUILD_CACHE_SECRET_KEY", type=str, callback=wrap_in_secret)
@click.option("--show-dagger-logs/--hide-dagger-logs", default=False, type=bool)
@click_ci_requirements_option()
@click_track_command
@click_merge_args_into_context_obj
@click_append_to_context_object("is_ci", lambda ctx: not ctx.obj["is_local"])
@click_append_to_context_object("gha_workflow_run_url", _get_gha_workflow_run_url)
@click_append_to_context_object("pull_request", _get_pull_request)
@click.pass_context
@click_ignore_unused_kwargs
async def airbyte_ci(ctx: click.Context) -> None:  # noqa D103
    # Check that the command being run is not upgrade
    is_update_command = ctx.invoked_subcommand == "update"
    if ctx.obj["enable_update_check"] and ctx.obj["is_local"] and not is_update_command:
        check_for_upgrade(
            require_update=ctx.obj["is_local"],
            enable_auto_update=ctx.obj["is_local"] and ctx.obj["enable_auto_update"],
        )

    if ctx.obj["enable_dagger_run"] and not is_current_process_wrapped_by_dagger_run():
        main_logger.debug("Re-Running airbyte-ci with dagger run.")
        from pipelines.cli.dagger_run import call_current_command_with_dagger_run

        call_current_command_with_dagger_run()
        return

    if ctx.obj["is_local"]:
        # This check is meaningful only when running locally
        # In our CI the docker host used by the Dagger Engine is different from the one used by the runner.
        check_local_docker_configuration()

    if not ctx.obj["is_local"]:
        log_context_info(ctx)

    if not ctx.obj.get("secret_stores", {}).get("in_memory"):
        ctx.obj["secret_stores"] = {"in_memory": InMemorySecretStore()}


if __name__ == "__main__":
    airbyte_ci()
