#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from logging import Logger
from typing import Any, List, Optional

import asyncclick as click
import asyncer
from jinja2 import Template
from pipelines.models.steps import CommandResult

ALL_RESULTS_KEY = "_run_all_results"

SUMMARY_TEMPLATE_STR = """
{% if command_results %}
Summary of commands results
========================
{% for command_result in command_results %}
{{ '✅' if  command_result.success else '❌' }} {{ command_result.command.name }}
{% endfor %}
{% endif %}
"""

DETAILS_TEMPLATE_STR = """
{% for command_result in command_results %}
{% if command_result.stdout or command_result.stderr %}
=================================

Details for {{ command_result.command.name }} command
{% if command_result.stdout %}
STDOUT:
{{ command_result.stdout }}
{% endif %}
{% if command_result.stderr %}
STDERR:
{{ command_result.stderr }}
{% endif %}
{% endif %}
{% endfor %}

"""


@dataclass
class LogOptions:
    quiet: bool = True
    help_message: Optional[str] = None


def log_command_results(
    ctx: click.Context, command_results: List[CommandResult], logger: Logger, options: LogOptions = LogOptions()
) -> None:
    """
    Log the output of the subcommands run by `run_all_subcommands`.
    """

    if not options.quiet:
        details_template = Template(DETAILS_TEMPLATE_STR)
        details_message = details_template.render(command_results=command_results)
        logger.info(details_message)

    summary_template = Template(SUMMARY_TEMPLATE_STR)
    summary_message = summary_template.render(command_results=command_results)
    logger.info(summary_message)

    if options.help_message:
        logger.info(options.help_message)


async def invoke_commands_concurrently(ctx: click.Context, commands: List[click.Command]) -> List[Any]:
    """
    Run click commands concurrently and return a list of their return values.
    """

    soon_command_executions_results = []
    async with asyncer.create_task_group() as command_task_group:
        for command in commands:
            soon_command_execution_result = command_task_group.soonify(command.invoke)(ctx)
            soon_command_executions_results.append(soon_command_execution_result)
    return [r.value for r in soon_command_executions_results]


async def invoke_commands_sequentially(ctx: click.Context, commands: List[click.Command]) -> List[Any]:
    """
    Run click commands sequentially and return a list of their return values.
    """
    command_executions_results = []
    for command in commands:
        command_executions_results.append(await command.invoke(ctx))
    return command_executions_results


def get_all_sibling_commands(ctx: click.Context) -> List[click.Command]:
    """
    Get all sibling commands of the current command.
    """
    return [c for c in ctx.parent.command.commands.values() if c.name != ctx.command.name]  # type: ignore
