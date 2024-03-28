#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
import requests  # type: ignore
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.airbyte_ci.connectors.upgrade_java_cdk.pipeline import run_connector_java_cdk_upgrade_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand


@click.command(cls=DaggerPipelineCommand, short_help="Upgrade Java CDK version")
@click.argument("target-java-cdk-version", type=str, default="")
@click.pass_context
async def upgrade_java_cdk_version(
    ctx: click.Context,
    target_java_cdk_version: str,
) -> bool:
    """Upgrade CDK version"""

    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Upgrade Java CDK version of connector {connector.technical_name}",
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

    new_java_cdk_version = target_java_cdk_version
    if new_java_cdk_version == "":
        cdk_version_properties = connectors_contexts.get_repo_file(
            "/airbyte-cdk/java/airbyte-cdk/core/src/main/resources/version.properties"
        )
        version_properties_content = cdk_version_properties.contents()
        new_java_cdk_version = re.search(r"version *= *(?P<version>[0-9]*\.[0-9]*\.[0-9]*)", og_build_gradle_content).group("version")

    await run_connectors_pipelines(
        connectors_contexts,
        run_connector_cdk_upgrade_pipeline,
        "Upgrade CDK version pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        new_java_cdk_version,
    )

    return True
