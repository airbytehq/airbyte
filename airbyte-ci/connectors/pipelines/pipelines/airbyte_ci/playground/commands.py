#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import asyncclick as click
from pipelines.cli.click_decorators import LazyPassDecorator, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext
from pipelines.helpers.utils import sh_dash_c
from pipelines.consts import DOCKER_VERSION

pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)


@click.command()
@click.argument("poetry_package_path")
@click.option("--test-directory", default="tests", help="The directory containing the tests to run.")
@pass_pipeline_context
@click_ignore_unused_kwargs
async def playground(
    ctx: ClickPipelineContext,
    poetry_package_path: str,
    test_directory: str,
):
    """
    TODO
    1. Make async
    1. Call a dagger pipeline

    Blockers:
    1. Need asyncio to run dagger pipeline
    """
    print(f"params: {ctx.params}")

    logger = logging.getLogger(f"{poetry_package_path}.tests")
    logger.info(f"Running tests for {poetry_package_path}")
    # The following directories are always mounted because a lot of tests rely on them
    directories_to_always_mount = [".git", ".github", "docs", "airbyte-integrations", "airbyte-ci", "airbyte-cdk", "pyproject.toml"]
    directories_to_mount = list(set([poetry_package_path, *directories_to_always_mount]))

    dagger_client = await ctx.get_dagger_client(pipeline_name="format_ci")
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
                exclude=["**/__pycache__", "**/.pytest_cache", "**/.venv", "**.log", "**/.gradle"],
                include=directories_to_mount,
            ),
        )
        .with_workdir(f"/airbyte/{poetry_package_path}")
        .with_exec(["poetry", "install"])
        .with_unix_socket("/var/run/docker.sock", dagger_client.host().unix_socket("/var/run/docker.sock"))
        .with_exec(["poetry", "run", "pytest", test_directory])
    )

    success = await pytest_container
    if not success:
        click.Abort()

