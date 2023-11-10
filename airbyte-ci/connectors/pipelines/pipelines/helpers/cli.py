#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from logging import Logger
from typing import Any, List

import asyncclick as click
import asyncer
from jinja2 import Template
from pipelines.models.steps import CommandResult, StepStatus

ALL_RESULTS_KEY = "_run_all_results"

SUMMARY_TEMPLATE_STR = """

Summary of commands results
========================
{% for command_name, success in results %}
{{ '✅' if  success else '❌' }} {{ command_prefix }} {{ command_name }}
{% endfor %}
"""

DETAILS_TEMPLATE_STR = """

Detailed Errors for failed commands
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


def log_command_results(ctx: click.Context, command_results: List[CommandResult], logger: Logger, options: LogOptions = LogOptions()):
    """
    Log the output of the subcommands run by `run_all_subcommands`.
    """
    command_path = ctx.command_path

    summary_template = Template(SUMMARY_TEMPLATE_STR)
    results = [(r.command.name, r.status is StepStatus.SUCCESS) for r in command_results]
    summary_message = summary_template.render(results=results, command_prefix=command_path)
    logger.info(summary_message)

    result_contains_failures = any([r.status is StepStatus.FAILURE for r in command_results])

    if result_contains_failures:
        if options.list_errors:
            failed_commands_details = [
                (command_result.command.name, command_result.stderr)
                for command_result in command_results
                if command_result.status is StepStatus.FAILURE
            ]
            if failed_commands_details:
                details_template = Template(DETAILS_TEMPLATE_STR)
                details_message = details_template.render(failed_commands_details=failed_commands_details, command_prefix=command_path)
                logger.info(details_message)
        else:
            logger.info(f"Run `{command_path} --list-errors` to see detailed error messages for failed checks.")

    if options.help_message:
        logger.info(options.help_message)


async def invoke_commands_concurrently(ctx: click.Context, commands: List[click.Command]) -> List[Any]:
    """
    Run click commands concurrently and return a list of their return values.
    """

    soon_command_executions_results = []
    async with asyncer.create_task_group() as command_group:
        for command in commands:
            soon_command_execution_result = command_group.soonify(ctx.invoke)(command)
            soon_command_executions_results.append(soon_command_execution_result)
    return [r.value for r in soon_command_executions_results]


async def invoke_commands_sequentially(ctx: click.Context, commands: List[click.Command]) -> List[Any]:
    """
    Run click commands sequentially and return a list of their return values.
    """
    command_executions_results = []
    for command in commands:
        command_executions_results.append(await ctx.invoke(command))
    return command_executions_results


def get_all_sibling_commands(ctx: click.Context) -> List[click.Command]:
    """
    Get all sibling commands of the current command.
    """
    return [c for c in ctx.parent.command.commands.values() if c.name != ctx.command.name]
