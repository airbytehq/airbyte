#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List

import asyncclick as click
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.airbyte_ci.connectors.up_to_date.pipeline import run_connector_up_to_date_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand


@click.command(
    cls=DaggerPipelineCommand,
    short_help="Get the selected Python connectors up to date.",
)
@click.option(
    "--dev",
    type=bool,
    default=False,
    is_flag=True,
    help="Force update when there are only dev changes.",
)
@click.option(
    "--dep",
    type=str,
    multiple=True,
    default=[],
    help="Give a specific set of `poetry add` dependencies to update. For example: --dep airbyte-cdk==0.80.0 --dep pytest@^6.2",
)

# TODO: flag to skip regression tests
# TODO: flag to make PR
# TODO: also update the manifest.yaml with the cdk version?
@click.pass_context
async def up_to_date(ctx: click.Context, dev: bool, dep: List[str]) -> bool:

    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Update {connector.technical_name} to latest",
            connector=connector,
            is_local=ctx.obj["is_local"],
            git_branch=ctx.obj["git_branch"],
            git_revision=ctx.obj["git_revision"],
            ci_report_bucket=ctx.obj["ci_report_bucket_name"],
            report_output_prefix=ctx.obj["report_output_prefix"],
            use_remote_secrets=ctx.obj["use_remote_secrets"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            dagger_logs_url=ctx.obj.get("dagger_logs_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
            ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
            ci_git_user=ctx.obj["ci_git_user"],
            ci_github_access_token=ctx.obj["ci_github_access_token"],
            enable_report_auto_open=True,
            docker_hub_username=ctx.obj.get("docker_hub_username"),
            docker_hub_password=ctx.obj.get("docker_hub_password"),
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    await run_connectors_pipelines(
        connectors_contexts,
        run_connector_up_to_date_pipeline,
        "Get Python connector up to date",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        dev,
        dep,
    )

    return True
