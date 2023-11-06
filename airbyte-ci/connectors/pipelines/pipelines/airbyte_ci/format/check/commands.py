# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import sys
from typing import List

import anyio
import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.actions import run_check
from pipelines.airbyte_ci.format.check.utils import log_output
from pipelines.airbyte_ci.format.containers import (
    format_java_container,
    format_js_container,
    format_license_container,
    format_python_container,
)
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.group(
    help="Run code format checks and fail if any checks fail.",
    invoke_without_command=True,
    chain=True,
)
@click.option("--list-errors", is_flag=True, default=False, help="Show detailed error messages for failed checks.")
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def check(ctx: click.Context, pipeline_ctx: ClickPipelineContext, list_errors: bool):
    """Run code format checks and fail if any checks fail."""
    logger = logging.getLogger("check")

    ctx.obj["dagger_client"] = await pipeline_ctx.get_dagger_client(pipeline_name="Check repository formatting")
    ctx.obj["check_results"] = {}

    if ctx.invoked_subcommand is None:
        logger.info("Running all checks...")
        async with anyio.create_task_group() as check_group:
            for command in ctx.command.commands.values():
                check_group.start_soon(run_check_command, ctx, command)

    log_output(ctx.obj["check_results"], list_errors, logger)

    if any(not succeeded for (succeeded, _) in ctx.obj["check_results"].values()):
        sys.exit(1)


async def run_check_command(ctx, command):
    try:
        await ctx.invoke(command)
        ctx.obj["check_results"][command.name] = (True, None)
    except dagger.ExecError as e:
        ctx.obj["check_results"][command.name] = (False, str(e))


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext):
    """Format java, groovy, and sql code via spotless."""
    container = format_java_container(ctx)
    check_commands = ["./gradlew spotlessCheck --scan"]
    await run_check(container, check_commands)


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    """Format yaml and json code via prettier."""
    container = format_js_container(ctx)
    check_commands = ["prettier --check ."]
    await run_check(container, check_commands)


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license(ctx: ClickPipelineContext):
    """Add license to python and java code via addlicense."""
    license_file = "LICENSE_SHORT"
    container = format_license_container(ctx, license_file)
    check_commands = [f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_file} --check ."]
    await run_check(container, check_commands)


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def python(ctx: ClickPipelineContext):
    """Format python code via black and isort."""
    container = format_python_container(ctx)
    check_commands = [
        "poetry install --no-root",
        "poetry run isort --settings-file pyproject.toml --check-only .",
        "poetry run black --config pyproject.toml --check .",
    ]
    await run_check(container, check_commands)
