#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import List

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.actions import run_format
from pipelines.airbyte_ci.format.containers import (
    format_java_container,
    format_js_container,
    format_license_container,
    format_python_container,
)
from pipelines.cli.click_decorators import click_ignore_unused_kwargs
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.cli import (
    LogOptions,
    get_all_sibling_commands,
    invoke_commands_concurrently,
    invoke_commands_sequentially,
    log_command_results,
)
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context
from pipelines.models.steps import CommandResult, StepStatus

# HELPERS


async def get_format_command_result(click_command: click.Command, container: dagger.Container, format_commands: List[str]) -> CommandResult:
    """Run a format command and return the CommandResult.
    A command is considered successful if the export operation of run_format is successful.

    Args:
        click_command (click.Command): The click command to run
        container (dagger.Container): The container to run the format_commands in
        format_commands (List[str]): The list of commands to run to format the repository

    Returns:
        CommandResult: The result of running the command
    """
    try:
        successful_export = await run_format(container, format_commands)
        status = StepStatus.SUCCESS if successful_export else StepStatus.FAILURE
        return CommandResult(click_command, status=status)
    except dagger.ExecError as e:
        return CommandResult(click_command, status=StepStatus.FAILURE, stderr=e.stderr, stdout=e.stdout, exc_info=e)


@click.group(
    help="Run code format checks and fix any failures.",
    chain=True,
)
async def fix():
    pass


@fix.command(cls=DaggerPipelineCommand, name="all")
@click.pass_context
async def all_fix(ctx: click.Context):
    """Run code format checks and fix any failures."""
    parent_command = ctx.parent.command
    logger = logging.getLogger(parent_command.name)

    concurrent_commands = [
        fix.commands["python"],
        fix.commands["java"],
        fix.commands["js"],
    ]
    sequential_commands = [fix.commands["license"]]

    # We can run language commands concurrently because they modify different set of files.
    command_results = await invoke_commands_concurrently(ctx, concurrent_commands)

    # We have to run license command sequentially because it modifies the same set of files as other commands.
    # If we ran it concurrently with language commands, we face race condition issues.
    command_results += await invoke_commands_sequentially(ctx, sequential_commands)
    failure = any([r.status is StepStatus.FAILURE for r in command_results])

    log_options = LogOptions(list_errors=True)

    log_command_results(ctx, command_results, logger, log_options)

    return not failure


@fix.command(cls=DaggerPipelineCommand)
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext) -> CommandResult:
    """Format java, groovy, and sql code via spotless."""
    dagger_client = await ctx.get_dagger_client(pipeline_name="Format java")
    container = format_java_container(dagger_client)
    format_commands = ["./gradlew spotlessApply --scan"]
    return await get_format_command_result(fix.commands["java"], container, format_commands)


@fix.command(cls=DaggerPipelineCommand)
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext) -> CommandResult:
    dagger_client = await ctx.get_dagger_client(pipeline_name="Format js")
    container = format_js_container(dagger_client)
    format_commands = ["prettier --write ."]
    return await get_format_command_result(fix.commands["js"], container, format_commands)


@fix.command("license")
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license_fix(ctx: ClickPipelineContext) -> CommandResult:
    """Add license to python and java code via addlicense."""
    license_file = "LICENSE_SHORT"
    dagger_client = await ctx.get_dagger_client(pipeline_name="Add license")
    container = format_license_container(dagger_client, license_file)
    format_commands = [f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_file} ."]
    return await get_format_command_result(fix.commands["license"], container, format_commands)


@fix.command(cls=DaggerPipelineCommand)
@pass_pipeline_context
@click_ignore_unused_kwargs
async def python(ctx: ClickPipelineContext) -> CommandResult:
    """Format python code via black and isort."""
    dagger_client = await ctx.get_dagger_client(pipeline_name="Format python")
    container = format_python_container(dagger_client)
    format_commands = [
        "poetry install --no-root",
        "poetry run isort --settings-file pyproject.toml .",
        "poetry run black --config pyproject.toml .",
    ]
    return await get_format_command_result(fix.commands["python"], container, format_commands)
