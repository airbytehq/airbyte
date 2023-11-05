# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import sys
from typing import Optional

import anyio
import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.check.utils import run_check
from pipelines.cli.click_decorators import (
    LazyPassDecorator,
    click_append_to_context_object,
    click_ignore_unused_kwargs,
    click_merge_args_into_context_obj,
)
from pipelines.cli.lazy_group import LazyGroup
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext

pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)


@click.group(
    help="Run code format checks and fail if any checks fail.",
    invoke_without_command=True,
    chain=True,
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def check(ctx: click.Context, pipeline_ctx: ClickPipelineContext):
    """Run code format checks and fail if any checks fail."""
    # TODO: fix this client hacking
    ctx.obj["dagger_client"] = await pipeline_ctx.get_dagger_client(pipeline_name="Format License")

    if ctx.invoked_subcommand is None:
        print("Running all checks...")
        async with anyio.create_task_group() as check_group:
            check_group.start_soon(ctx.invoke, java)
            check_group.start_soon(ctx.invoke, js)
            check_group.start_soon(ctx.invoke, license)
            check_group.start_soon(ctx.invoke, python)


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext):
    """Format java, groovy, and sql code via spotless."""

    await run_check(
        ctx,
        base_image="openjdk:17.0.1-jdk-slim",
        include=[
            "**/*.java",
            "**/*.sql",
            "**/*.gradle",
            "gradlew",
            "gradlew.bat",
            "gradle",
            "**/deps.toml",
            "**/gradle.properties",
            "**/version.properties",
            "tools/gradle/codestyle/java-google-style.xml",
            "tools/gradle/codestyle/sql-dbeaver.properties",
        ],
        install_commands=[],
        check_commands=["./gradlew spotlessCheck --scan"],
    )


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    """Format yaml and json code via prettier."""
    await run_check(
        ctx,
        base_image="node:18.18.0-slim",
        include=["**/*.yaml", "**/*.yml", "**.*/json", "package.json", "package-lock.json"],
        install_commands=["npm install -g npm@10.1.0", "npm install -g prettier@2.8.1"],
        check_commands=["prettier --check ."],
    )


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license(ctx: ClickPipelineContext):
    """Add license to python and java code via addlicense."""
    license_file = "LICENSE_SHORT"

    await run_check(
        ctx,
        base_image="golang:1.17",
        include=["**/*.java", "**/*.py", license_file],
        install_commands=["go get -u github.com/google/addlicense"],
        check_commands=[f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_file} --check ."],
    )


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def python(ctx: ClickPipelineContext):
    """Format python code via black and isort."""
    await run_check(
        ctx,
        base_image="python:3.10.13-slim",
        env_vars={"PIPX_BIN_DIR": "/usr/local/bin"},
        include=["**/*.py", "pyproject.toml", "poetry.lock"],
        install_commands=["pip install pipx", "pipx ensurepath", "pipx install poetry"],
        check_commands=[
            "poetry install",
            "poetry run isort --settings-file pyproject.toml --check-only .",
            "poetry run black --config pyproject.toml --check .",
        ],
    )
