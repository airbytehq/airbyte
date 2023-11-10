#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.actions import run_check
from pipelines.airbyte_ci.format.containers import (
    format_java_container,
    format_js_container,
    format_license_container,
    format_python_container,
)
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.cli import LogOptions, get_all_sibling_commands, invoke_commands_concurrently, log_command_results
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context
from pipelines.models.steps import CommandResult, StepStatus


# HELPERS
async def get_check_command_result(click_command: click.Command, checks_commands, container) -> CommandResult:
    try:
        stdout = await run_check(container, checks_commands).stdout()
        return CommandResult(click_command, status=StepStatus.SUCCESS, stdout=stdout)
    except dagger.ExecError as e:
        return CommandResult(click_command, status=StepStatus.FAILURE, stderr=e.stderr, stdout=e.stdout, exc_info=e)


@click.group(
    help="Run code format checks and fail if any checks fail.",
    chain=True,
)
async def check():
    pass


@check.command(name="all")
@click.option("--list-errors", is_flag=True, default=False, help="Show detailed error messages for failed checks.")
@click.pass_context
async def all_checks(ctx: click.Context, list_errors: bool):
    """
    Run all format checks and fail if any checks fail.
    """
    all_commands = get_all_sibling_commands(ctx)

    command_results = await invoke_commands_concurrently(ctx, all_commands)
    failure = any([r.status is StepStatus.FAILURE for r in command_results])
    parent_command = ctx.parent.command
    logger = logging.getLogger(parent_command.name)
    log_options = LogOptions(
        list_errors=list_errors,
        help_message="Run `airbyte-ci format check all --list-errors` to see detailed error messages for failed checks. Run `airbyte-ci format fix all` for a best effort fix.",
    )
    log_command_results(ctx, command_results, logger, log_options)
    if failure:
        raise click.Abort()


@check.command(cls=DaggerPipelineCommand)
@pass_pipeline_context
async def python(pipeline_context: ClickPipelineContext) -> CommandResult:
    """Format python code via black and isort."""

    dagger_client = await pipeline_context.get_dagger_client(pipeline_name="Check python formatting")
    container = format_python_container(dagger_client)
    check_commands = [
        "poetry install --no-root",
        "poetry run isort --settings-file pyproject.toml --check-only .",
        "poetry run black --config pyproject.toml --check .",
    ]
    return await get_check_command_result(check.commands["python"], check_commands, container)


@check.command(cls=DaggerPipelineCommand)
@pass_pipeline_context
async def java(pipeline_context: ClickPipelineContext) -> CommandResult:
    """Format java, groovy, and sql code via spotless."""
    dagger_client = await pipeline_context.get_dagger_client(pipeline_name="Check java formatting")
    container = format_java_container(dagger_client)
    check_commands = ["./gradlew spotlessCheck --scan"]
    return await get_check_command_result(check.commands["java"], check_commands, container)


@check.command(cls=DaggerPipelineCommand)
@pass_pipeline_context
async def js(pipeline_context: ClickPipelineContext):
    """Format yaml and json code via prettier."""
    dagger_client = await pipeline_context.get_dagger_client(pipeline_name="Check js formatting")
    container = format_js_container(dagger_client)
    check_commands = ["prettier --check ."]
    return await get_check_command_result(check.commands["js"], check_commands, container)


@check.command("license")
@pass_pipeline_context
async def license_check(pipeline_context: ClickPipelineContext):
    """Add license to python and java code via addlicense."""
    license_file = "LICENSE_SHORT"
    dagger_client = await pipeline_context.get_dagger_client(pipeline_name="Check license header")
    container = format_license_container(dagger_client, license_file)
    check_commands = [f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_file} --check ."]
    return await get_check_command_result(check.commands["license"], check_commands, container)
