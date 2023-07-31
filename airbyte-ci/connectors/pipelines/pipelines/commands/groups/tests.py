#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the tests command to test airbyte-ci projects.
"""

import logging
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
    anyio.run(run_test, airbyte_ci_package_path)


async def run_test(airbyte_ci_package_path: str):
    """Runs the tests for the given airbyte-ci package in a Dagger container.

    Args:
        airbyte_ci_package_path (str): Path to the airbyte-ci package to test, relative to airbyte-ci directory.
    """
    logger = logging.getLogger(f"{airbyte_ci_package_path}.tests")
    logger.info(f"Running tests for {airbyte_ci_package_path}")
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
        try:
            pytest_stdout = await (
                dagger_client.container()
                .from_("python:3.10-slim")
                .with_exec(["apt-get", "update"])
                .with_exec(["apt-get", "install", "-y", "bash", "git"])
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
                .with_exec(["poetry", "run", "pytest", "tests"])
            ).stdout()
            logger.info("Successfully ran tests")
            logger.info(pytest_stdout)
        except dagger.ExecError as e:
            logger.error("Tests failed")
            logger.error(e.stdout)
            logger.error(e.stderr)
