#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the format commands.
"""
from __future__ import annotations

from typing import Optional

import asyncclick as click
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context

from .context import PyPIPublishContext
from .pipeline import PublishToPyPI

CONNECTOR_PATH_PREFIX = "airbyte-integrations/connectors"


@click.command(cls=DaggerPipelineCommand, name="publish", help="Publish a Python package to PyPI.")
@click.option(
    "--pypi-token",
    help="Access token",
    type=click.STRING,
    required=True,
    envvar="PYPI_TOKEN",
)
@click.option(
    "--registry-url",
    help="Which registry to publish to. If not set, the default pypi is used. For test pypi, use https://test.pypi.org/legacy/",
    type=click.STRING,
    default="https://pypi.org/simple",
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
async def publish(
    ctx: click.Context,
    click_pipeline_context: ClickPipelineContext,
    pypi_token: str,
    registry_url: str,
    publish_name: Optional[str],
    publish_version: Optional[str],
) -> bool:
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
        registry=registry_url,
        package_path=ctx.obj["package_path"],
        package_name=publish_name,
        version=publish_version,
    )

    if context.package_path.startswith(CONNECTOR_PATH_PREFIX):
        context.logger.warning("It looks like you are trying to publish a connector. Please use the `connectors` command group instead.")

    dagger_client = await click_pipeline_context.get_dagger_client(pipeline_name=f"Publish {ctx.obj['package_path']} to PyPI")
    context.dagger_client = dagger_client

    await PublishToPyPI(context).run()

    return True
