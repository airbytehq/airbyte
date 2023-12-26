#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from pathlib import Path
from typing import List

import asyncclick as click
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.consts import DOCKER_VERSION
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.command()
@click.argument("poetry_package_path")
@click.option(
    "-c",
    "--poetry-run-command",
    multiple=True,
    help="The poetry run command to run.",
    required=True,
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def test(pipeline_context: ClickPipelineContext):
    """Runs the tests for the given airbyte-ci package

    Args:
        pipeline_context (ClickPipelineContext): The context object.
    """
    poetry_package_path = pipeline_context.params["poetry_package_path"]
    if not Path(f"{poetry_package_path}/pyproject.toml").exists():
        raise click.UsageError(f"Could not find pyproject.toml in {poetry_package_path}")

    commands_to_run: List[str] = pipeline_context.params["poetry_run_command"]

    logger = logging.getLogger(f"{poetry_package_path}.tests")
    logger.info(f"Running tests for {poetry_package_path}")

    # The following directories are always mounted because a lot of tests rely on them
    directories_to_always_mount = [
        ".git",  # This is needed as some package tests rely on being in a git repo
        ".github",
        "docs",
        "airbyte-integrations",
        "airbyte-ci",
        "airbyte-cdk",
        "pyproject.toml",
        "LICENSE_SHORT",
        "poetry.lock",
        "spotless-maven-pom.xml",
        "tools/gradle/codestyle/java-google-style.xml",
    ]
    directories_to_mount = list(set([poetry_package_path, *directories_to_always_mount]))

    pipeline_name = f"Unit tests for {poetry_package_path}"
    dagger_client = await pipeline_context.get_dagger_client(pipeline_name=pipeline_name)
    test_container = await (
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
                exclude=["**/__pycache__", "**/.pytest_cache", "**/.venv", "**.log", "**/.gradle"],
                include=directories_to_mount,
            ),
        )
        .with_workdir(f"/airbyte/{poetry_package_path}")
        .with_exec(["poetry", "install", "--with=dev"])
        .with_unix_socket("/var/run/docker.sock", dagger_client.host().unix_socket("/var/run/docker.sock"))
        .with_env_variable("CI", str(pipeline_context.params["is_ci"]))
        .with_workdir(f"/airbyte/{poetry_package_path}")
    )
    for command in commands_to_run:
        test_container = test_container.with_exec(["poetry", "run", *command.split(" ")])
    await test_container
