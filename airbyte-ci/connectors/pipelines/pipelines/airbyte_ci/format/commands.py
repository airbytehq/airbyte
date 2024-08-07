#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the format commands.
"""
from __future__ import annotations

import logging
import sys
from typing import Dict, List

import asyncclick as click
from pipelines.airbyte_ci.format.configuration import FORMATTERS_CONFIGURATIONS, Formatter
from pipelines.airbyte_ci.format.format_command import FormatCommand
from pipelines.cli.click_decorators import click_ci_requirements_option, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.helpers.cli import LogOptions, invoke_commands_concurrently, invoke_commands_sequentially, log_command_results
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context
from pipelines.models.steps import StepStatus


@click.group(
    name="format",
    help="Commands related to formatting.",
)
@click.option("--quiet", "-q", help="Hide details of the formatter execution.", default=False, is_flag=True)
@click_ci_requirements_option()
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def format_code(pipeline_context: ClickPipelineContext) -> None:
    pass


@format_code.group(
    help="Run code format checks and fail if any checks fail.",
    chain=True,
)
async def check() -> None:
    pass


@format_code.group(
    help="Run code format checks and fix any failures.",
    chain=True,
)
async def fix() -> None:
    pass


# Check and fix commands only differ in the export_formatted_code parameter value: check does not export, fix does.
FORMATTERS_CHECK_COMMANDS: Dict[Formatter, FormatCommand] = {
    config.formatter: FormatCommand(
        config.formatter, config.file_filter, config.get_format_container_fn, config.format_commands, export_formatted_code=False
    )
    for config in FORMATTERS_CONFIGURATIONS
}

FORMATTERS_FIX_COMMANDS: Dict[Formatter, FormatCommand] = {
    config.formatter: FormatCommand(
        config.formatter, config.file_filter, config.get_format_container_fn, config.format_commands, export_formatted_code=True
    )
    for config in FORMATTERS_CONFIGURATIONS
}

# Register language specific check commands
for formatter, check_command in FORMATTERS_CHECK_COMMANDS.items():
    check.add_command(check_command, name=formatter.value)

# Register language specific fix commands
for formatter, fix_command in FORMATTERS_FIX_COMMANDS.items():
    fix.add_command(fix_command, name=formatter.value)


@check.command(name="all", help="Run all format checks and fail if any checks fail.")
@click.pass_context
async def all_checks(ctx: click.Context) -> None:
    """
    Run all format checks and fail if any checks fail.
    """

    # We disable logging and exit on failure because its this the current command that takes care of reporting.
    all_commands: List[click.Command] = [
        command.set_enable_logging(False).set_exit_on_failure(False) for command in FORMATTERS_CHECK_COMMANDS.values()
    ]
    command_results = await invoke_commands_concurrently(ctx, all_commands)
    failure = any([r.status is StepStatus.FAILURE for r in command_results])
    logger = logging.getLogger(check.commands["all"].name)
    log_options = LogOptions(
        quiet=ctx.obj["quiet"],
        help_message="Run `airbyte-ci format fix all` to fix the code format.",
    )
    log_command_results(ctx, command_results, logger, log_options)
    if failure:
        sys.exit(1)


@fix.command(name="all", help="Fix all format failures. Exits with status 1 if any file was modified.")
@click.pass_context
async def all_fix(ctx: click.Context) -> None:
    """Run code format checks and fix any failures."""
    logger = logging.getLogger(fix.commands["all"].name)

    # We have to run license command sequentially because it modifies the same set of files as other commands.
    # If we ran it concurrently with language commands, we face race condition issues.
    # We also want to run it before language specific formatter as they might reformat the license header.
    sequential_commands: List[click.Command] = [
        FORMATTERS_FIX_COMMANDS[Formatter.LICENSE].set_enable_logging(False).set_exit_on_failure(False),
    ]
    command_results = await invoke_commands_sequentially(ctx, sequential_commands)

    # We can run language commands concurrently because they modify different set of files.
    # We disable logging and exit on failure because its this the current command that takes care of reporting.
    concurrent_commands: List[click.Command] = [
        FORMATTERS_FIX_COMMANDS[Formatter.JAVA].set_enable_logging(False).set_exit_on_failure(False),
        FORMATTERS_FIX_COMMANDS[Formatter.PYTHON].set_enable_logging(False).set_exit_on_failure(False),
        FORMATTERS_FIX_COMMANDS[Formatter.JS].set_enable_logging(False).set_exit_on_failure(False),
    ]

    command_results += await invoke_commands_concurrently(ctx, concurrent_commands)
    failure = any([r.status is StepStatus.FAILURE for r in command_results])

    log_options = LogOptions(
        quiet=ctx.obj["quiet"],
        help_message="You can stage the formatted files `git add .` and commit them with `git commit -m 'chore: format code'`.",
    )

    log_command_results(ctx, command_results, logger, log_options)
    if failure:
        # We exit this command with status 1 because we want to make it fail when fix is modifying files.
        # It allows us to run it in a Git hook and fail the commit/push if the code is not formatted.
        sys.exit(1)
