#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import asyncclick as click
from pipelines.airbyte_ci.format.actions import run_check
from pipelines.airbyte_ci.format.containers import (
    format_java_container,
    format_js_container,
    format_license_container,
    format_python_container,
)
from pipelines.cli.click_decorators import click_ignore_unused_kwargs
from pipelines.helpers.cli import LogOptions, run_all_subcommands
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.group(
    help="Run code format checks and fail if any checks fail.",
    chain=True,
)
async def check():
    pass


@check.command(name="all")
@click.option("--list-errors", is_flag=True, default=False, help="Show detailed error messages for failed checks.")
@click.pass_context
async def all_languages(ctx: click.Context, list_errors: bool):
    """
    Run all format checks and fail if any checks fail.
    """
    log_options = LogOptions(
        list_errors=list_errors,
        help_message="Run `airbyte-ci format check all --list-errors` to see detailed error messages for failed checks.",
    )
    await run_all_subcommands(ctx, log_options)


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext):
    """Format java, groovy, and sql code via spotless."""
    dagger_client = await ctx.get_dagger_client(pipeline_name="Check java formatting")
    container = format_java_container(dagger_client)
    check_commands = ["./gradlew spotlessCheck --scan"]
    await run_check(container, check_commands)


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    """Format yaml and json code via prettier."""
    dagger_client = await ctx.get_dagger_client(pipeline_name="Check js formatting")
    container = format_js_container(dagger_client)
    check_commands = ["prettier --check ."]
    await run_check(container, check_commands)


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license(ctx: ClickPipelineContext):
    """Add license to python and java code via addlicense."""
    license_file = "LICENSE_SHORT"
    dagger_client = await ctx.get_dagger_client(pipeline_name="Check license header")
    container = format_license_container(dagger_client, license_file)
    check_commands = [f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_file} --check ."]
    await run_check(container, check_commands)


@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def python(ctx: ClickPipelineContext):
    """Format python code via black and isort."""
    dagger_client = await ctx.get_dagger_client(pipeline_name="Check python formatting")
    container = format_python_container(dagger_client)
    check_commands = [
        "poetry install --no-root",
        "poetry run isort --settings-file pyproject.toml --check-only .",
        "poetry run black --config pyproject.toml --check .",
    ]
    await run_check(container, check_commands)
