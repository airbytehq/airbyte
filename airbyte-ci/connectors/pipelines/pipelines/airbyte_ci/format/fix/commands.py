# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import asyncclick as click
from pipelines.airbyte_ci.format.actions import run_format
from pipelines.airbyte_ci.format.containers import (
    format_java_container,
    format_js_container,
    format_license_container,
    format_python_container,
)
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
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
    logger = logging.getLogger("format")
    ctx.obj["dagger_client"] = await pipeline_ctx.get_dagger_client(pipeline_name="Format repository")

    if ctx.invoked_subcommand is None:
        logger.info("Running all formatters...")
        for command in fix.commands.values():
            await ctx.invoke(command)


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext):
    """Format java, groovy, and sql code via spotless."""
    container = format_java_container(ctx)
    format_commands = ["./gradlew spotlessApply --scan"]
    await run_format(container, format_commands)


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    container = format_js_container(ctx)
    format_commands = ["prettier --write ."]
    await run_format(container, format_commands)


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license(ctx: ClickPipelineContext):
    """Add license to python and java code via addlicense."""
    license_file = "LICENSE_SHORT"
    container = format_license_container(ctx, license_file)
    format_commands = [f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_file} ."]
    await run_format(container, format_commands)


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def python(ctx: ClickPipelineContext):
    """Format python code via black and isort."""
    container = format_python_container(ctx)
    format_commands = [
        "poetry install --no-root",
        "poetry run isort --settings-file pyproject.toml .",
        "poetry run black --config pyproject.toml .",
    ]
    await run_format(container, format_commands)
