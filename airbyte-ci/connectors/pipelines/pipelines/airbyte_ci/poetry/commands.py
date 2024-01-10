#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the format commands.
"""
from __future__ import annotations

import logging
import sys
from typing import Any, Dict, List

import asyncclick as click
from pipelines.airbyte_ci.format.configuration import FORMATTERS_CONFIGURATIONS, Formatter
from pipelines.airbyte_ci.format.format_command import FormatCommand
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.helpers.cli import LogOptions, invoke_commands_concurrently, invoke_commands_sequentially, log_command_results
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context
from pipelines.models.steps import StepStatus
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from .pipeline import PyPIPublishContext, PublishToPyPI


@click.group(
    name="poetry",
    help="Commands related to running poetry commands.",
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def poetry(pipeline_context: ClickPipelineContext) -> None:
    pass


@poetry.command(cls=DaggerPipelineCommand, name="publish", help="Publish a Python package to PyPI.")
@click.option(
    "--pypi-username",
    help="Your username to connect to PyPI.",
    type=click.STRING,
    required=True,
    envvar="PYPI_USERNAME",
)
@click.option(
    "--pypi-password",
    help="Your password to connect to PyPI.",
    type=click.STRING,
    required=True,
    envvar="PYPI_PASSWORD",
)
@click.option(
    "--pypi-repository",
    help="The PyPI repository to publish to (pypi, test-pypi).",
    type=click.Choice(["pypi", "testpypi"]),
    default="pypi",
)
@click.option(
    "--package-path",
    help="The path to publish",
    type=click.STRING,
    required=True,
)
@pass_pipeline_context
@click.pass_context
async def publish(ctx: click.Context,
    package_path: str,
    pypi_username: str,
    pypi_password: str,
    pypi_repository: str,
    click_pipeline_context: ClickPipelineContext
                  ) -> None:
    context = PyPIPublishContext(
        is_local=ctx.obj["is_local"],
        git_branch=ctx.obj["git_branch"],
        git_revision=ctx.obj["git_revision"],
        ci_report_bucket=ctx.obj["ci_report_bucket_name"],
        report_output_prefix=ctx.obj["report_output_prefix"],
        gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
        dagger_logs_url=ctx.obj.get("dagger_logs_url"),
        pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
        ci_context=ctx.obj.get("ci_context"),
        ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
        pypi_username=pypi_username,
        pypi_password=pypi_password,
        pypi_repository=pypi_repository,
        package_path=package_path
    )
    dagger_client = await click_pipeline_context.get_dagger_client(pipeline_name=f"Publish {package_path} to PyPI")
    context.dagger_client = dagger_client

    await PublishToPyPI(context).run()

