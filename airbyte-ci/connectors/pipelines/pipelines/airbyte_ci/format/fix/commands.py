# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Optional

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.fix.utils import run_format
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.group(
    help="Run code format checks and fix any failures.",
    invoke_without_command=True,
    chain=True,
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def fix(ctx: click.Context, pipeline_ctx: ClickPipelineContext):
    """Run code format checks and fix any failures."""
    # TODO: fix this client hacking
    ctx.obj["dagger_client"] = await pipeline_ctx.get_dagger_client(pipeline_name="Format License")

    if ctx.invoked_subcommand is None:
        print("Running all formatters...")
        await ctx.invoke(java)
        await ctx.invoke(js)
        await ctx.invoke(license)
        await ctx.invoke(python)


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext):
    """Format java, groovy, and sql code via spotless."""
    await run_format(
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
        format_commands=["./gradlew spotlessApply --scan"],
    )


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    await run_format(
        ctx,
        base_image="node:18.18.0-slim",
        include=["**/*.yaml", "**/*.yml", "**.*/json", "package.json", "package-lock.json"],
        install_commands=["npm install -g npm@10.1.0", "npm install -g prettier@2.8.1"],
        format_commands=["prettier --write ."],
    )


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license(ctx: ClickPipelineContext):
    """Add license to python and java code via addlicense."""
    license_file = "LICENSE_SHORT"

    await run_format(
        ctx,
        base_image="golang:1.17",
        include=["**/*.java", "**/*.py", license_file],
        install_commands=["go get -u github.com/google/addlicense"],
        format_commands=[f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_file} ."],
    )


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def python(ctx: ClickPipelineContext):
    """Format python code via black and isort."""
    await run_format(
        ctx,
        base_image="python:3.10.13-slim",
        env_vars={"PIPX_BIN_DIR": "/usr/local/bin"},
        include=["**/*.py", "pyproject.toml", "poetry.lock"],
        install_commands=["pip install pipx", "pipx ensurepath", "pipx install poetry"],
        format_commands=[
            "poetry install",
            "poetry run isort --settings-file pyproject.toml .",
            "poetry run black --config pyproject.toml .",
        ],
    )
