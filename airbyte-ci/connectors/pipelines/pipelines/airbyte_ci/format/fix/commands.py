# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import asyncclick as click
from pipelines.airbyte_ci.format.actions import run_format
from pipelines.airbyte_ci.format.containers import (
    format_java_container,
    format_js_container,
    format_license_container,
    format_python_container,
)
from pipelines.cli.click_decorators import click_ignore_unused_kwargs
from pipelines.helpers.cli import run_all_subcommands
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.group(
    help="Run code format checks and fix any failures.",
    chain=True,
)
async def fix():
    pass


@fix.command(name="all")
@click.pass_context
@pass_pipeline_context
async def all_languages(ctx: click.Context, pipeline_context: ClickPipelineContext):
    """Run code format checks and fix any failures."""
    await pipeline_context.get_dagger_client(pipeline_name="Fix all languages")
    await run_all_subcommands(ctx)


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext):
    """Format java, groovy, and sql code via spotless."""
    dagger_client = await ctx.get_dagger_client(pipeline_name="Format java")
    container = format_java_container(dagger_client)
    format_commands = ["./gradlew spotlessApply --scan"]
    await run_format(container, format_commands)


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    dagger_client = await ctx.get_dagger_client(pipeline_name="Format js")
    container = format_js_container(dagger_client)
    format_commands = ["prettier --write ."]
    await run_format(container, format_commands)


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license(ctx: ClickPipelineContext):
    """Add license to python and java code via addlicense."""
    license_file = "LICENSE_SHORT"
    dagger_client = await ctx.get_dagger_client(pipeline_name="Add license")
    container = format_license_container(dagger_client, license_file)
    format_commands = [f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_file} ."]
    await run_format(container, format_commands)


@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def python(ctx: ClickPipelineContext):
    """Format python code via black and isort."""
    dagger_client = await ctx.get_dagger_client(pipeline_name="Format python")
    container = format_python_container(dagger_client)
    format_commands = [
        "poetry install --no-root",
        "poetry run isort --settings-file pyproject.toml .",
        "poetry run black --config pyproject.toml .",
    ]
    await run_format(container, format_commands)
