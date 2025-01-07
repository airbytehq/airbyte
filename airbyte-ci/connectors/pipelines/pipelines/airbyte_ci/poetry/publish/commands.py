#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the format commands.
"""

from __future__ import annotations

from typing import Optional

import asyncclick as click
from packaging import version

from pipelines.airbyte_ci.steps.python_registry import PublishToPythonRegistry
from pipelines.cli.confirm_prompt import confirm
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.cli.secrets import wrap_in_secret
from pipelines.consts import DEFAULT_PYTHON_PACKAGE_REGISTRY_CHECK_URL, DEFAULT_PYTHON_PACKAGE_REGISTRY_URL
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context
from pipelines.models.contexts.python_registry_publish import PythonRegistryPublishContext
from pipelines.models.secrets import Secret
from pipelines.models.steps import StepStatus


async def _has_metadata_yaml(context: PythonRegistryPublishContext) -> bool:
    dir_to_publish = context.get_repo_dir(context.package_path)
    return "metadata.yaml" in await dir_to_publish.entries()


def _validate_python_version(_ctx: dict, _param: dict, value: Optional[str]) -> Optional[str]:
    """
    Check if an given version is valid.
    """
    if value is None:
        return value
    try:
        version.Version(value)
        return value
    except version.InvalidVersion:
        raise click.BadParameter(f"Version {value} is not a valid version.")


@click.command(cls=DaggerPipelineCommand, name="publish", help="Publish a Python package to a registry.")
@click.option(
    "--python-registry-token",
    help="Access token",
    type=click.STRING,
    required=True,
    envvar="PYTHON_REGISTRY_TOKEN",
    callback=wrap_in_secret,
)
@click.option(
    "--python-registry-url",
    help="Which registry to publish to. If not set, the default pypi is used. For test pypi, use https://test.pypi.org/legacy/",
    type=click.STRING,
    default=DEFAULT_PYTHON_PACKAGE_REGISTRY_URL,
    envvar="PYTHON_REGISTRY_URL",
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
    callback=_validate_python_version,
)
@pass_pipeline_context
@click.pass_context
async def publish(
    ctx: click.Context,
    click_pipeline_context: ClickPipelineContext,
    python_registry_token: Secret,
    python_registry_url: str,
    publish_name: Optional[str],
    publish_version: Optional[str],
) -> bool:
    context = PythonRegistryPublishContext(
        is_local=ctx.obj["is_local"],
        git_branch=ctx.obj["git_branch"],
        git_revision=ctx.obj["git_revision"],
        diffed_branch=ctx.obj["diffed_branch"],
        git_repo_url=ctx.obj["git_repo_url"],
        ci_report_bucket=ctx.obj["ci_report_bucket_name"],
        report_output_prefix=ctx.obj["report_output_prefix"],
        gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
        dagger_logs_url=ctx.obj.get("dagger_logs_url"),
        pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
        ci_context=ctx.obj.get("ci_context"),
        ci_gcp_credentials=ctx.obj["ci_gcp_credentials"],
        python_registry_token=python_registry_token,
        registry=python_registry_url,
        registry_check_url=DEFAULT_PYTHON_PACKAGE_REGISTRY_CHECK_URL,
        package_path=ctx.obj["package_path"],
        package_name=publish_name,
        version=publish_version,
    )

    dagger_client = await click_pipeline_context.get_dagger_client()
    context.dagger_client = dagger_client

    if await _has_metadata_yaml(context):
        confirm(
            "It looks like you are trying to publish a connector. In most cases, the `connectors` command group should be used instead. Do you want to continue?",
            abort=True,
        )

    publish_result = await PublishToPythonRegistry(context).run()

    return publish_result.status is StepStatus.SUCCESS
