#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the format commands.
"""
from __future__ import annotations

import logging
import sys
from typing import Any, Dict, List, Optional

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
@click.option(
    "--package-path",
    help="The path to publish",
    type=click.STRING,
    required=True,
)
@click.option(
    "--docker-image",
    help="The docker image to run the command in.",
    type=click.STRING,
    default="mwalbeck/python-poetry"
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def poetry(pipeline_context: ClickPipelineContext) -> None:
    pass


@poetry.command(cls=DaggerPipelineCommand, name="publish", help="Publish a Python package to PyPI.")
@click.option(
    "--pypi-token",
    help="Access token",
    type=click.STRING,
    required=True,
    envvar="PYPI_TOKEN",
)
@click.option(
    "--test-pypi",
    help="Whether to publish to test.pypi.org instead of pypi.org.",
    type=click.BOOL,
    is_flag=True,
    default=False,
)
@click.option(
    "--publish-name",
    help="The name of the package to publish. If not set, the name will be inferred from the pyproject.toml file of the package.",
    type=click.STRING,
)
@click.option(
    "--publish-version",
    help="The version of the package to publish. If not set, the version will be inferred from the pyproject.toml file of the package.",
    type=click.STRING,
)
@pass_pipeline_context
@click.pass_context
async def publish(ctx: click.Context,
    click_pipeline_context: ClickPipelineContext,
    pypi_token: str,
    test_pypi: bool,
    publish_name: Optional[str],
    publish_version: Optional[str]) -> None:
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
        pypi_token=pypi_token,
        test_pypi=test_pypi,
        package_path=ctx.obj["package_path"],
        build_docker_image=ctx.obj["docker_image"],
        package_name=publish_name,
        version=publish_version,
    )
    dagger_client = await click_pipeline_context.get_dagger_client(pipeline_name=f"Publish {ctx.obj['package_path']} to PyPI")
    context.dagger_client = dagger_client

    await PublishToPyPI(context).run()

    return True

