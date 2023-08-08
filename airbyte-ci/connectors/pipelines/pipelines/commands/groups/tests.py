#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the tests command to test airbyte-ci projects.
"""

import logging
import os
import sys

import anyio
import click
import dagger
from pipelines.utils import AIRBYTE_REPO_URL


@click.command()
@click.argument("airbyte_ci_package_path")
@click.pass_context
def tests(
    ctx: click.Context,
    airbyte_ci_package_path: str,
):
    """Runs the tests for the given airbyte-ci package.

    Args:
        airbyte_ci_package_path (str): Path to the airbyte-ci package to test, relative to airbyte-ci directory
    """
    success = anyio.run(run_test, airbyte_ci_package_path, ctx.obj["git_branch"], ctx.obj["is_local"])
    if not success:
        click.Abort()


async def run_test(airbyte_ci_package_path: str, git_branch: str, is_local: bool) -> bool:
    """Runs the tests for the given airbyte-ci package in a Dagger container.

    Args:
        airbyte_ci_package_path (str): Path to the airbyte-ci package to test, relative to airbyte-ci directory.
        git_branch (str): Name of the git branch to test.
        is_local (bool): Whether the command is run locally or in CI.
    Returns:
        bool: True if the tests passed, False otherwise.
    """
    logger = logging.getLogger(f"{airbyte_ci_package_path}.tests")
    logger.info(f"Running tests for {airbyte_ci_package_path} on branch {git_branch}")
    if is_local:
        logger.warn(
            "For performance reason the code under test will be pulled from the remote repository, not from the local filesystem. Please push your changes to the remote repository before running this command."
        )
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
        airbyte_repo = dagger_client.git(AIRBYTE_REPO_URL, keep_git_dir=True)
        airbyte_dir = airbyte_repo.branch(git_branch).tree()
        try:
            docker_host_socket = dagger_client.host().unix_socket("/var/run/buildkit/buildkitd.sock")
            pytest_container = await (
                dagger_client.container()
                .from_("python:3.10.12")
                .with_exec(["apt-get", "update"])
                .with_exec(["apt-get", "install", "-y", "bash", "git", "curl"])
                .with_env_variable("VERSION", "24.0.2")
                .with_exec(["sh", "-c", "curl -fsSL https://get.docker.com | sh"])
                .with_exec(["pip", "install", "pipx"])
                .with_exec(["pipx", "ensurepath"])
                .with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")
                .with_exec(["pipx", "install", "poetry"])
                .with_mounted_directory(
                    "/airbyte",
                    airbyte_dir,
                )
                .with_workdir(f"/airbyte/airbyte-ci/{airbyte_ci_package_path}")
                .with_exec(["poetry", "install"])
                .with_unix_socket("/var/run/docker.sock", dagger_client.host().unix_socket("/var/run/docker.sock"))
                .with_exec(["poetry", "run", "pytest", "tests"])
            )
            if "_EXPERIMENTAL_DAGGER_RUNNER_HOST" in os.environ:
                logger.info("Using experimental dagger runner host to run CAT with dagger-in-dagger")
                pytest_container = pytest_container.with_env_variable(
                    "_EXPERIMENTAL_DAGGER_RUNNER_HOST", "unix:///var/run/buildkit/buildkitd.sock"
                ).with_unix_socket("/var/run/buildkit/buildkitd.sock", docker_host_socket)

            await pytest_container
            return True
        except dagger.ExecError as e:
            logger.error("Tests failed")
            logger.error(e.stderr)
            sys.exit(1)
