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
    click.echo("Airbyte-ci format is deprecated. Run `pre-commit run` instead.")
    sys.exit(1)


@fix.command(name="all", help="Fix all format failures. Exits with status 1 if any file was modified.")
@click.pass_context
async def all_fix(ctx: click.Context) -> None:
    click.echo("Airbyte-ci format is deprecated. Run `pre-commit run` instead.")
    sys.exit(1)
