#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module contains hacks used in connectors pipelines. They're gathered here for tech debt visibility."""

from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING, Callable, List

import asyncclick as click
from connector_ops.utils import ConnectorLanguage  # type: ignore
from pipelines import consts
from pipelines.helpers.github import AIRBYTE_GITHUB_REPO_URL, is_automerge_pull_request, update_commit_status_check

if TYPE_CHECKING:
    from dagger import Container
    from pipelines.airbyte_ci.connectors.context import ConnectorContext


async def cache_latest_cdk(context: ConnectorContext) -> None:
    """
    Download the latest CDK version to update the pip cache.

    Underlying issue:
        Most Python connectors, or normalization, are not pinning the CDK version they use.
        It means that the will get whatever version is in the pip cache.
        But the original goal of not pinning the CDK version is to always get the latest version.

    Hack:
        Call this function before building connector test environment to update the cache with the latest CDK version.

    Github Issue:
        Revisiting and aligning how we build Python connectors and using the same container for test, build and publish will provide better control over the CDK version.
        https://github.com/airbytehq/airbyte/issues/25523
    Args:
        dagger_client (Client): Dagger client.
    """
    # We want the CDK to be re-downloaded on every run per connector to ensure we always get the latest version.
    # But we don't want to invalidate the pip cache on every run because it could lead to a different CDK version installed on different architecture build.
    cachebuster_value = f"{context.connector.technical_name}_{context.pipeline_start_timestamp}"

    await (
        context.dagger_client.container()
        .from_("python:3.9-slim")
        .with_mounted_cache(consts.PIP_CACHE_PATH, context.dagger_client.cache_volume(consts.PIP_CACHE_VOLUME_NAME))
        .with_env_variable("CACHEBUSTER", cachebuster_value)
        .with_exec(["pip", "install", "--force-reinstall", "airbyte-cdk", "-vvv"], use_entrypoint=True)
        .sync()
    )


def never_fail_exec(command: List[str]) -> Callable[[Container], Container]:
    """
    Wrap a command execution with some bash sugar to always exit with a 0 exit code but write the actual exit code to a file.

    Underlying issue:
        When a classic dagger with_exec is returning a >0 exit code an ExecError is raised.
        It's OK for the majority of our container interaction.
        But some execution, like running CAT, are expected to often fail.
        In CAT we don't want ExecError to be raised on container interaction because CAT might write updated secrets that we need to pull from the container after the test run.
        The bash trick below is a hack to always return a 0 exit code but write the actual exit code to a file.
        The file is then read by the pipeline to determine the exit code of the container.

    Args:
        command (List[str]): The command to run in the container.

    Returns:
        Callable: _description_
    """

    def never_fail_exec_inner(container: Container) -> Container:
        return container.with_exec(["sh", "-c", f"{' '.join(command)}; echo $? > /exit_code"])

    return never_fail_exec_inner


def do_regression_test_status_check(ctx: click.Context, status_check_name: str, logger: Logger) -> None:
    """
    Emit a failing status check that requires a manual override, via a /-command.

    Only required for certified connectors.
    """
    commit = ctx.obj["git_revision"]
    run_url = ctx.obj["gha_workflow_run_url"]
    should_send = ctx.obj.get("ci_context") == consts.CIContext.PULL_REQUEST

    if (
        (not is_automerge_pull_request(ctx.obj.get("pull_request")))
        and (ctx.obj["git_repo_url"] == AIRBYTE_GITHUB_REPO_URL)
        and any(
            [
                (connector.language == ConnectorLanguage.PYTHON and connector.support_level == "certified")
                for connector in ctx.obj["selected_connectors_with_modified_files"]
            ]
        )
    ):
        logger.info(f'is_automerge_pull_request={is_automerge_pull_request(ctx.obj.get("pull_request"))}')
        logger.info(f'git_repo_url={ctx.obj["git_repo_url"]}')
        for connector in ctx.obj["selected_connectors_with_modified_files"]:
            logger.info(f"connector = {connector.name}")
            logger.info(f"connector.language={connector.language}")
            logger.info(f"connector.support_level = {connector.support_level}")
        update_commit_status_check(
            commit,
            "failure",
            run_url,
            description="Check if regression tests have been manually approved",
            context=status_check_name,
            is_optional=False,
            should_send=should_send,
            logger=logger,
        )
    else:
        update_commit_status_check(
            commit,
            "success",
            run_url,
            description="[Skipped]",
            context=status_check_name,
            is_optional=True,
            should_send=should_send,
            logger=logger,
        )
