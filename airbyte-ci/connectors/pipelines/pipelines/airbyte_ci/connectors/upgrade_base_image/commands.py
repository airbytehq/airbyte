#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import anyio
import click
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.migrate_to_base_image.pipeline import run_connector_base_image_upgrade_pipeline
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand


@click.command(cls=DaggerPipelineCommand, short_help="Upgrades the base image version used by the selected connectors.")
@click.option("--set-if-not-exists", default=True)
@click.option(
    "--docker-hub-username",
    help="Your username to connect to DockerHub to read the registries.",
    type=click.STRING,
    required=True,
    envvar="DOCKER_HUB_USERNAME",
)
@click.option(
    "--docker-hub-password",
    help="Your password to connect to DockerHub to read the registries.",
    type=click.STRING,
    required=True,
    envvar="DOCKER_HUB_PASSWORD",
)
@click.pass_context
def upgrade_base_image(ctx: click.Context, set_if_not_exists: bool, docker_hub_username: str, docker_hub_password: str) -> bool:
    """Upgrades the base image version used by the selected connectors."""

    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Upgrade base image versions of connector {connector.technical_name}",
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
            open_report_in_browser=False,
            docker_hub_username=docker_hub_username,
            docker_hub_password=docker_hub_password,
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    anyio.run(
        run_connectors_pipelines,
        connectors_contexts,
        run_connector_base_image_upgrade_pipeline,
        "Upgrade base image pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        set_if_not_exists,
    )

    return True
