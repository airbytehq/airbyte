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
from pipelines.consts import DOCKER_VERSION
from pipelines.utils import sh_dash_c


@click.command()
@click.argument("poetry_package_path")
@click.option("--test-directory", default="tests", help="The directory containing the tests to run.")
def test(
    poetry_package_path: str,
    test_directory: str,
):
    """Runs the tests for the given airbyte-ci package.

    Args:
        poetry_package_path (str): Path to the poetry package to test, relative to airbyte-ci directory.
        test_directory (str): The directory containing the tests to run.
    """
    success = anyio.run(run_test, poetry_package_path, test_directory)
    if not success:
        click.Abort()


async def run_test(poetry_package_path: str, test_directory: str) -> bool:
    """Runs the tests for the given airbyte-ci package in a Dagger container.

    Args:
        airbyte_ci_package_path (str): Path to the airbyte-ci package to test, relative to airbyte-ci directory.
    Returns:
        bool: True if the tests passed, False otherwise.
    """
    logger = logging.getLogger(f"{poetry_package_path}.tests")
    logger.info(f"Running tests for {poetry_package_path}")
    # The following directories are always mounted because a lot of tests rely on them
    directories_to_always_mount = [".git", "airbyte-integrations", "airbyte-ci", "airbyte-cdk", "pyproject.toml"]
    directories_to_mount = list(set([poetry_package_path, *directories_to_always_mount]))
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
        try:
            docker_host_socket = dagger_client.host().unix_socket("/var/run/buildkit/buildkitd.sock")
            pytest_container = await (
                dagger_client.container()
                .from_("python:3.10.12")
                .with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")
                .with_exec(
                    sh_dash_c(
                        [
                            "apt-get update",
                            "apt-get install -y bash git curl",
                            "pip install pipx",
                            "pipx ensurepath",
                            "pipx install poetry",
                        ]
                    )
                )
                .with_env_variable("VERSION", DOCKER_VERSION)
                .with_exec(sh_dash_c(["curl -fsSL https://get.docker.com | sh"]))
                .with_mounted_directory(
                    "/airbyte",
                    dagger_client.host().directory(
                        ".",
                        exclude=["**/__pycache__", "**/.pytest_cache", "**/.venv", "**.log", "**/build", "**/.gradle"],
                        include=directories_to_mount,
                    ),
                )
                .with_workdir(f"/airbyte/{poetry_package_path}")
                .with_exec(["poetry", "install"])
                .with_unix_socket("/var/run/docker.sock", dagger_client.host().unix_socket("/var/run/docker.sock"))
                .with_exec(["poetry", "run", "pytest", test_directory])
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
