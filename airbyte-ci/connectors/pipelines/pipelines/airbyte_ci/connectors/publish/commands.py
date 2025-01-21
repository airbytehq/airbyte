#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Callable, Dict, Iterable, List

import asyncclick as click
from pipelines import main_logger
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.airbyte_ci.connectors.publish.context import PublishConnectorContext, RolloutMode
from pipelines.airbyte_ci.connectors.publish.pipeline import (
    reorder_contexts,
    run_connector_promote_pipeline,
    run_connector_publish_pipeline,
    run_connector_rollback_pipeline,
)
from pipelines.cli.click_decorators import click_ci_requirements_option
from pipelines.cli.confirm_prompt import confirm
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.cli.secrets import wrap_gcp_credentials_in_secret, wrap_in_secret
from pipelines.consts import DEFAULT_PYTHON_PACKAGE_REGISTRY_CHECK_URL, DEFAULT_PYTHON_PACKAGE_REGISTRY_URL, ContextState
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles
from pipelines.helpers.utils import fail_if_missing_docker_hub_creds
from pipelines.models.secrets import Secret

ROLLOUT_MODE_TO_PIPELINE_FUNCTION: Dict[RolloutMode, Callable] = {
    RolloutMode.PUBLISH: run_connector_publish_pipeline,
    RolloutMode.PROMOTE: run_connector_promote_pipeline,
    RolloutMode.ROLLBACK: run_connector_rollback_pipeline,
}


# Third-party connectors can't be published with this pipeline, skip them.
# This is not the same as partner connectors. Partner connectors use our tech stack and can
# be published just fine. Third-party connectors are in their own subdirectory.
def filter_out_third_party_connectors(
    selected_connectors_with_modified_files: Iterable[ConnectorWithModifiedFiles],
) -> List[ConnectorWithModifiedFiles]:
    """
    Return the list of connectors filtering out the connectors stored in connectors/third-party directory.
    """
    filtered_connectors = []
    for connector in selected_connectors_with_modified_files:
        if connector.is_third_party:
            main_logger.info(f"Skipping third party connector {connector.technical_name} from the list of connectors")
        else:
            filtered_connectors.append(connector)
    return filtered_connectors


@click.command(cls=DaggerPipelineCommand, help="Publish all images for the selected connectors.")
@click_ci_requirements_option()
@click.option("--pre-release/--main-release", help="Use this flag if you want to publish pre-release images.", default=True, type=bool)
@click.option(
    "--spec-cache-gcs-credentials",
    help="The service account key to upload files to the GCS bucket hosting spec cache.",
    type=click.STRING,
    required=True,
    envvar="SPEC_CACHE_GCS_CREDENTIALS",
    callback=wrap_gcp_credentials_in_secret,
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
    callback=wrap_gcp_credentials_in_secret,
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
    "--python-registry-token",
    help="Access token for python registry",
    type=click.STRING,
    envvar="PYTHON_REGISTRY_TOKEN",
    callback=wrap_in_secret,
)
@click.option(
    "--python-registry-url",
    help="Which python registry url to publish to. If not set, the default pypi is used. For test pypi, use https://test.pypi.org/legacy/",
    type=click.STRING,
    default=DEFAULT_PYTHON_PACKAGE_REGISTRY_URL,
    envvar="PYTHON_REGISTRY_URL",
)
@click.option(
    "--python-registry-check-url",
    help="Which url to check whether a certain version is published already. If not set, the default pypi is used. For test pypi, use https://test.pypi.org/pypi/",
    type=click.STRING,
    default=DEFAULT_PYTHON_PACKAGE_REGISTRY_CHECK_URL,
    envvar="PYTHON_REGISTRY_CHECK_URL",
)
@click.option(
    "--promote-release-candidate",
    help="Promote a release candidate to a main release.",
    type=click.BOOL,
    default=False,
    is_flag=True,
)
@click.option(
    "--rollback-release-candidate",
    help="Rollback a release candidate to a previous version.",
    type=click.BOOL,
    default=False,
    is_flag=True,
)
@click.pass_context
async def publish(
    ctx: click.Context,
    pre_release: bool,
    spec_cache_gcs_credentials: Secret,
    spec_cache_bucket_name: str,
    metadata_service_bucket_name: str,
    metadata_service_gcs_credentials: Secret,
    slack_webhook: str,
    python_registry_token: Secret,
    python_registry_url: str,
    python_registry_check_url: str,
    promote_release_candidate: bool,
    rollback_release_candidate: bool,
) -> bool:
    if promote_release_candidate and rollback_release_candidate:
        raise click.UsageError("You can't promote and rollback a release candidate at the same time.")
    elif promote_release_candidate:
        rollout_mode = RolloutMode.PROMOTE
    elif rollback_release_candidate:
        rollout_mode = RolloutMode.ROLLBACK
    else:
        rollout_mode = RolloutMode.PUBLISH

    ctx.obj["selected_connectors_with_modified_files"] = filter_out_third_party_connectors(
        ctx.obj["selected_connectors_with_modified_files"]
    )
    if not ctx.obj["selected_connectors_with_modified_files"]:
        return True

    if ctx.obj["is_local"]:
        confirm(
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
                docker_hub_username=Secret("docker_hub_username", ctx.obj["secret_stores"]["in_memory"]),
                docker_hub_password=Secret("docker_hub_password", ctx.obj["secret_stores"]["in_memory"]),
                slack_webhook=slack_webhook,
                ci_report_bucket=ctx.obj["ci_report_bucket_name"],
                report_output_prefix=ctx.obj["report_output_prefix"],
                is_local=ctx.obj["is_local"],
                git_branch=ctx.obj["git_branch"],
                git_revision=ctx.obj["git_revision"],
                diffed_branch=ctx.obj["diffed_branch"],
                git_repo_url=ctx.obj["git_repo_url"],
                gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
                dagger_logs_url=ctx.obj.get("dagger_logs_url"),
                pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
                ci_context=ctx.obj.get("ci_context"),
                ci_gcp_credentials=ctx.obj["ci_gcp_credentials"],
                pull_request=ctx.obj.get("pull_request"),
                s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
                s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
                use_local_cdk=ctx.obj.get("use_local_cdk"),
                python_registry_token=python_registry_token,
                python_registry_url=python_registry_url,
                python_registry_check_url=python_registry_check_url,
                rollout_mode=rollout_mode,
                ci_github_access_token=ctx.obj.get("ci_github_access_token"),
            )
            for connector in ctx.obj["selected_connectors_with_modified_files"]
        ]
    )
    main_logger.warn("Concurrency is forced to 1. For stability reasons we disable parallel publish pipelines.")
    ctx.obj["concurrency"] = 1

    ran_publish_connector_contexts = await run_connectors_pipelines(
        publish_connector_contexts,
        ROLLOUT_MODE_TO_PIPELINE_FUNCTION[rollout_mode],
        f"{rollout_mode.value} connectors",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
    )
    return all(context.state is ContextState.SUCCESSFUL for context in ran_publish_connector_contexts)
