#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
from pipelines import main_logger
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.airbyte_ci.connectors.publish.context import PublishConnectorContext
from pipelines.airbyte_ci.connectors.publish.pipeline import reorder_contexts, run_connector_publish_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.consts import ContextState
from pipelines.helpers.utils import fail_if_missing_docker_hub_creds


@click.command(cls=DaggerPipelineCommand, help="Publish all images for the selected connectors.")
@click.option("--pre-release/--main-release", help="Use this flag if you want to publish pre-release images.", default=True, type=bool)
@click.option(
    "--spec-cache-gcs-credentials",
    help="The service account key to upload files to the GCS bucket hosting spec cache.",
    type=click.STRING,
    required=True,
    envvar="SPEC_CACHE_GCS_CREDENTIALS",
)
@click.option(
    "--spec-cache-bucket-name",
    help="The name of the GCS bucket where specs will be cached.",
    type=click.STRING,
    required=True,
    envvar="SPEC_CACHE_BUCKET_NAME",
)
@click.option(
    "--metadata-service-gcs-credentials",
    help="The service account key to upload files to the GCS bucket hosting the metadata files.",
    type=click.STRING,
    required=True,
    envvar="METADATA_SERVICE_GCS_CREDENTIALS",
)
@click.option(
    "--metadata-service-bucket-name",
    help="The name of the GCS bucket where metadata files will be uploaded.",
    type=click.STRING,
    required=True,
    envvar="METADATA_SERVICE_BUCKET_NAME",
)
@click.option(
    "--slack-webhook",
    help="The Slack webhook URL to send notifications to.",
    type=click.STRING,
    envvar="SLACK_WEBHOOK",
)
@click.option(
    "--slack-channel",
    help="The Slack webhook URL to send notifications to.",
    type=click.STRING,
    envvar="SLACK_CHANNEL",
    default="#connector-publish-updates",
)
@click.pass_context
async def publish(
    ctx: click.Context,
    pre_release: bool,
    spec_cache_gcs_credentials: str,
    spec_cache_bucket_name: str,
    metadata_service_bucket_name: str,
    metadata_service_gcs_credentials: str,
    slack_webhook: str,
    slack_channel: str,
):
    ctx.obj["spec_cache_gcs_credentials"] = spec_cache_gcs_credentials
    ctx.obj["spec_cache_bucket_name"] = spec_cache_bucket_name
    ctx.obj["metadata_service_bucket_name"] = metadata_service_bucket_name
    ctx.obj["metadata_service_gcs_credentials"] = metadata_service_gcs_credentials
    if ctx.obj["is_local"]:
        click.confirm(
            "Publishing from a local environment is not recommended and requires to be logged in Airbyte's DockerHub registry, do you want to continue?",
            abort=True,
        )

    fail_if_missing_docker_hub_creds(ctx)

    publish_connector_contexts = reorder_contexts(
        [
            PublishConnectorContext(
                connector=connector,
                pre_release=pre_release,
                spec_cache_gcs_credentials=spec_cache_gcs_credentials,
                spec_cache_bucket_name=spec_cache_bucket_name,
                metadata_service_gcs_credentials=metadata_service_gcs_credentials,
                metadata_bucket_name=metadata_service_bucket_name,
                docker_hub_username=ctx.obj["docker_hub_username"],
                docker_hub_password=ctx.obj["docker_hub_password"],
                slack_webhook=slack_webhook,
                reporting_slack_channel=slack_channel,
                ci_report_bucket=ctx.obj["ci_report_bucket_name"],
                report_output_prefix=ctx.obj["report_output_prefix"],
                is_local=ctx.obj["is_local"],
                git_branch=ctx.obj["git_branch"],
                git_revision=ctx.obj["git_revision"],
                gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
                dagger_logs_url=ctx.obj.get("dagger_logs_url"),
                pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
                ci_context=ctx.obj.get("ci_context"),
                ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
                pull_request=ctx.obj.get("pull_request"),
                s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
                s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
                use_local_cdk=ctx.obj.get("use_local_cdk"),
            )
            for connector in ctx.obj["selected_connectors_with_modified_files"]
        ]
    )

    main_logger.warn("Concurrency is forced to 1. For stability reasons we disable parallel publish pipelines.")
    ctx.obj["concurrency"] = 1

    publish_connector_contexts = await run_connectors_pipelines(
        publish_connector_contexts,
        run_connector_publish_pipeline,
        "Publishing connectors",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
    )
    return all(context.state is ContextState.SUCCESSFUL for context in publish_connector_contexts)
