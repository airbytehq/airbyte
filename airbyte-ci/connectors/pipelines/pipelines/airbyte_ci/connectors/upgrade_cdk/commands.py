#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.airbyte_ci.connectors.upgrade_cdk.pipeline import run_connector_cdk_upgrade_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand


@click.command(cls=DaggerPipelineCommand, short_help="Upgrade CDK version")
@click.argument("target-cdk-version", type=str, default="latest")
@click.pass_context
async def upgrade_cdk(
    ctx: click.Context,
    target_cdk_version: str,
) -> bool:
    """Upgrade CDK version"""

    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Upgrade CDK version of connector {connector.technical_name}",
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
            enable_report_auto_open=False,
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    await run_connectors_pipelines(
        connectors_contexts,
        run_connector_cdk_upgrade_pipeline,
        "Upgrade CDK version pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        target_cdk_version,
    )

    return True
