# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import sys
from dataclasses import dataclass
from typing import Dict, Tuple

import anyio
import asyncclick as click
import dagger
from jinja2 import Template

ALL_RESULTS_KEY = "_run_all_results"

SUMMARY_TEMPLATE_STR = """

Summary of Sub Command Results
========================
{% for command_name, result in results.items() %}
{{ '✅' if result[0] else '❌' }} {{ command_prefix }} {{ command_name }}
{% endfor %}
"""

DETAILS_TEMPLATE_STR = """

Detailed Errors for Failed Sub Commands
=================================
{% for command_name, error in failed_commands_details %}
❌ {{ command_prefix }} {{ command_name }}

Error: {{ error }}
{% endfor %}
=================================

"""


@dataclass
class LogOptions:
    list_errors: bool = False
    help_message: str = None


def _log_output(ctx: click.Context, logger, options: LogOptions = LogOptions()):
    """
    Log the output of the subcommands run by `run_all_subcommands`.
    """
    subcommand_results = ctx.obj[ALL_RESULTS_KEY]
    command_path = ctx.command_path

    summary_template = Template(SUMMARY_TEMPLATE_STR)
    summary_message = summary_template.render(results=subcommand_results, command_prefix=command_path)
    logger.info(summary_message)

    result_contains_failures = any(not succeeded for (succeeded, _) in subcommand_results.values())

    if result_contains_failures:
        if options.list_errors:
            failed_commands_details = [(name, error) for name, (success, error) in subcommand_results.items() if not success]
            if failed_commands_details:
                details_template = Template(DETAILS_TEMPLATE_STR)
                details_message = details_template.render(failed_commands_details=failed_commands_details, command_prefix=command_path)
                logger.info(details_message)
        else:
            logger.info(f"Run `{command_path} --list-errors` to see detailed error messages for failed checks.")

    if options.help_message:
        logger.info(options.help_message)


async def _run_sub_command(ctx: click.Context, command: click.Command):
    """
    Run a subcommand and store the result in the context object.
    """
    try:
        await ctx.invoke(command)
        ctx.obj[ALL_RESULTS_KEY][command.name] = (True, None)
    except dagger.ExecError as e:
        ctx.obj[ALL_RESULTS_KEY][command.name] = (False, str(e))


async def run_all_subcommands(ctx: click.Context, log_options: LogOptions = LogOptions()):
    """
    Run all subcommands of a given command and log the results.
    """
    ctx.obj[ALL_RESULTS_KEY] = {}

    parent_command_path = ctx.parent.command_path
    parent_command_name = ctx.parent.command.name
    current_command_name = ctx.command.name

    logger = logging.getLogger(parent_command_name)

    # omit current command from list of subcommands
    all_subcommands_dict = ctx.parent.command.commands
    filtered_subcommands_dict = {name: command for name, command in all_subcommands_dict.items() if name != current_command_name}

    logger.info(f"Running all sub commands of {parent_command_path}...")
    async with anyio.create_task_group() as check_group:
        for command in filtered_subcommands_dict.values():
            check_group.start_soon(_run_sub_command, ctx, command)

    _log_output(ctx, logger, log_options)

    if any(not succeeded for (succeeded, _) in ctx.obj[ALL_RESULTS_KEY].values()):
        sys.exit(1)
