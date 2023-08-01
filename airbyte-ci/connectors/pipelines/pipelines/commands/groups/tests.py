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


@click.command()
@click.argument("airbyte_ci_package_path")
def tests(
    airbyte_ci_package_path: str,
):
    """Runs the tests for the given airbyte-ci package.

    Args:
        airbyte_ci_package_path (str): Path to the airbyte-ci package to test, relative to airbyte-ci directory
    """
    success = anyio.run(run_test, airbyte_ci_package_path)
    if not success:
        click.Abort()


async def run_test(airbyte_ci_package_path: str) -> bool:
    """Runs the tests for the given airbyte-ci package in a Dagger container.

    Args:
        airbyte_ci_package_path (str): Path to the airbyte-ci package to test, relative to airbyte-ci directory.
    Returns:
        bool: True if the tests passed, False otherwise.
    """
    logger = logging.getLogger(f"{airbyte_ci_package_path}.tests")
    logger.info(f"Running tests for {airbyte_ci_package_path}")
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
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
                    "/airbyte-ci", dagger_client.host().directory("airbyte-ci", exclude=["*/__pycache__", "*/.pytest_cache", "*.venv"])
                )
                .with_workdir(f"/airbyte-ci/{airbyte_ci_package_path}")
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
            return False
