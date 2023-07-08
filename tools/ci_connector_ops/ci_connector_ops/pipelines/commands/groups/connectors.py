#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares the CLI commands to run the connectors CI pipelines."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import anyio
import click
from ci_connector_ops.pipelines import main_logger
from ci_connector_ops.pipelines.builds import run_connector_build_pipeline
from ci_connector_ops.pipelines.contexts import ConnectorContext, ContextState, PublishConnectorContext
from ci_connector_ops.pipelines.format import run_connectors_format_pipelines
from ci_connector_ops.pipelines.github import update_global_commit_status_check_for_tests
from ci_connector_ops.pipelines.pipelines.connectors import run_connectors_pipelines
from ci_connector_ops.pipelines.publish import reorder_contexts, run_connector_publish_pipeline
from ci_connector_ops.pipelines.tests import run_connector_test_pipeline
from ci_connector_ops.pipelines.utils import DaggerPipelineCommand, get_modified_connectors, get_modified_metadata_files
from ci_connector_ops.utils import ConnectorLanguage, console, get_all_released_connectors
from rich.table import Table
from rich.text import Text

# HELPERS


def validate_environment(is_local: bool, use_remote_secrets: bool):
    """Check if the required environment variables exist."""
    if is_local:
        if not (os.getcwd().endswith("/airbyte") and Path(".git").is_dir()):
            raise click.UsageError("You need to run this command from the airbyte repository root.")
    else:
        required_env_vars_for_ci = [
            "GCP_GSM_CREDENTIALS",
            "CI_REPORT_BUCKET_NAME",
            "CI_GITHUB_ACCESS_TOKEN",
        ]
        for required_env_var in required_env_vars_for_ci:
            if os.getenv(required_env_var) is None:
                raise click.UsageError(f"When running in a CI context a {required_env_var} environment variable must be set.")
    if use_remote_secrets and os.getenv("GCP_GSM_CREDENTIALS") is None:
        raise click.UsageError(
            "You have to set the GCP_GSM_CREDENTIALS if you want to download secrets from GSM. Set the --use-remote-secrets option to false otherwise."
        )


# COMMANDS


@click.group(help="Commands related to connectors and connector acceptance tests.")
@click.option("--use-remote-secrets", default=True)  # specific to connectors
@click.option(
    "--name", "names", multiple=True, help="Only test a specific connector. Use its technical name. e.g source-pokeapi.", type=str
)
@click.option("--language", "languages", multiple=True, help="Filter connectors to test by language.", type=click.Choice(ConnectorLanguage))
@click.option(
    "--release-stage",
    "release_stages",
    multiple=True,
    help="Filter connectors to test by release stage.",
    type=click.Choice(["alpha", "beta", "generally_available"]),
)
@click.option("--modified/--not-modified", help="Only test modified connectors in the current branch.", default=False, type=bool)
@click.option("--concurrency", help="Number of connector tests pipeline to run in parallel.", default=5, type=int)
@click.option(
    "--execute-timeout",
    help="The maximum time in seconds for the execution of a Dagger request before an ExecuteTimeoutError is raised. Passing None results in waiting forever.",
    default=None,
    type=int,
)
@click.pass_context
def connectors(
    ctx: click.Context,
    use_remote_secrets: bool,
    names: Tuple[str],
    languages: Tuple[ConnectorLanguage],
    release_stages: Tuple[str],
    modified: bool,
    concurrency: int,
    execute_timeout: int,
):
    """Group all the connectors-ci command."""
    validate_environment(ctx.obj["is_local"], use_remote_secrets)

    ctx.ensure_object(dict)
    ctx.obj["use_remote_secrets"] = use_remote_secrets
    ctx.obj["connector_names"] = names
    ctx.obj["connector_languages"] = languages
    ctx.obj["release_states"] = release_stages
    ctx.obj["modified"] = modified
    ctx.obj["concurrency"] = concurrency
    ctx.obj["execute_timeout"] = execute_timeout

    all_connectors = get_all_released_connectors()

    # We get the modified connectors and downstream connector deps, and files
    modified_connectors_and_files = get_modified_connectors(ctx.obj["modified_files"])

    # We select all connectors by default
    # and attach modified files to them
    selected_connectors_and_files = {connector: modified_connectors_and_files.get(connector, []) for connector in all_connectors}

    if names:
        selected_connectors_and_files = {
            connector: selected_connectors_and_files[connector]
            for connector in selected_connectors_and_files
            if connector.technical_name in names
        }
    if languages:
        selected_connectors_and_files = {
            connector: selected_connectors_and_files[connector]
            for connector in selected_connectors_and_files
            if connector.language in languages
        }
    if release_stages:
        selected_connectors_and_files = {
            connector: selected_connectors_and_files[connector]
            for connector in selected_connectors_and_files
            if connector.release_stage in release_stages
        }
    if modified:
        selected_connectors_and_files = modified_connectors_and_files

    ctx.obj["selected_connectors_and_files"] = selected_connectors_and_files
    ctx.obj["selected_connectors_names"] = [c.technical_name for c in selected_connectors_and_files.keys()]


@connectors.command(cls=DaggerPipelineCommand, help="Test all the selected connectors.")
@click.pass_context
def test(
    ctx: click.Context,
) -> bool:
    """Runs a test pipeline for the selected connectors.

    Args:
        ctx (click.Context): The click context.
    """
    if ctx.obj["is_ci"] and ctx.obj["pull_request"] and ctx.obj["pull_request"].draft:
        main_logger.info("Skipping connectors tests for draft pull request.")
        sys.exit(0)

    main_logger.info(f"Will run the test pipeline for the following connectors: {', '.join(ctx.obj['selected_connectors_names'])}")
    if ctx.obj["selected_connectors_and_files"]:
        update_global_commit_status_check_for_tests(ctx.obj, "pending")
    else:
        main_logger.warn("No connector were selected for testing.")
        update_global_commit_status_check_for_tests(ctx.obj, "success")
        return True

    connectors_tests_contexts = [
        ConnectorContext(
            pipeline_name=f"Testing connector {connector.technical_name}",
            connector=connector,
            is_local=ctx.obj["is_local"],
            git_branch=ctx.obj["git_branch"],
            git_revision=ctx.obj["git_revision"],
            modified_files=modified_files,
            ci_report_bucket=ctx.obj["ci_report_bucket_name"],
            report_output_prefix=ctx.obj["report_output_prefix"],
            use_remote_secrets=ctx.obj["use_remote_secrets"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            dagger_logs_url=ctx.obj.get("dagger_logs_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
            pull_request=ctx.obj.get("pull_request"),
            ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
        )
        for connector, modified_files in ctx.obj["selected_connectors_and_files"].items()
    ]
    try:
        anyio.run(
            run_connectors_pipelines,
            [connector_context for connector_context in connectors_tests_contexts],
            run_connector_test_pipeline,
            "Test Pipeline",
            ctx.obj["concurrency"],
            ctx.obj["dagger_logs_path"],
            ctx.obj["execute_timeout"],
        )
    except Exception as e:
        main_logger.error("An error occurred while running the test pipeline", exc_info=e)
        update_global_commit_status_check_for_tests(ctx.obj, "failure")
        return False

    @ctx.call_on_close
    def send_commit_status_check() -> None:
        if ctx.obj["is_ci"]:
            global_success = all(connector_context.state is ContextState.SUCCESSFUL for connector_context in connectors_tests_contexts)
            update_global_commit_status_check_for_tests(ctx.obj, "success" if global_success else "failure")

    # If we reach this point, it means that all the connectors have been tested so the pipeline did its job and can exit with success.
    return True


@connectors.command(cls=DaggerPipelineCommand, help="Build all images for the selected connectors.")
@click.pass_context
def build(ctx: click.Context) -> bool:
    main_logger.info(f"Will build the following connectors: {', '.join(ctx.obj['selected_connectors_names'])}.")
    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Build connector {connector.technical_name}",
            connector=connector,
            is_local=ctx.obj["is_local"],
            git_branch=ctx.obj["git_branch"],
            git_revision=ctx.obj["git_revision"],
            modified_files=modified_files,
            ci_report_bucket=ctx.obj["ci_report_bucket_name"],
            report_output_prefix=ctx.obj["report_output_prefix"],
            use_remote_secrets=ctx.obj["use_remote_secrets"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            dagger_logs_url=ctx.obj.get("dagger_logs_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
            ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
        )
        for connector, modified_files in ctx.obj["selected_connectors_and_files"].items()
    ]
    anyio.run(
        run_connectors_pipelines,
        connectors_contexts,
        run_connector_build_pipeline,
        "Build Pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
    )

    return True


@connectors.command(cls=DaggerPipelineCommand, help="Publish all images for the selected connectors.")
@click.option("--pre-release/--main-release", help="Use this flag if you want to publish pre-release images.", default=True, type=bool)
@click.option(
    "--spec-cache-gcs-credentials",
    help="The service account key to upload files to the GCS bucket hosting spec cache.",
    type=click.STRING,
    required=False,  # Not required for pre-release pipelines, downstream validation happens for main release pipelines
    envvar="SPEC_CACHE_GCS_CREDENTIALS",
)
@click.option(
    "--spec-cache-bucket-name",
    help="The name of the GCS bucket where specs will be cached.",
    type=click.STRING,
    required=False,  # Not required for pre-release pipelines, downstream validation happens for main release pipelines
    envvar="SPEC_CACHE_BUCKET_NAME",
)
@click.option(
    "--metadata-service-gcs-credentials",
    help="The service account key to upload files to the GCS bucket hosting the metadata files.",
    type=click.STRING,
    required=False,  # Not required for pre-release pipelines, downstream validation happens for main release pipelines
    envvar="METADATA_SERVICE_GCS_CREDENTIALS",
)
@click.option(
    "--metadata-service-bucket-name",
    help="The name of the GCS bucket where metadata files will be uploaded.",
    type=click.STRING,
    required=False,  # Not required for pre-release pipelines, downstream validation happens for main release pipelines
    envvar="METADATA_SERVICE_BUCKET_NAME",
)
@click.option(
    "--docker-hub-username",
    help="Your username to connect to DockerHub.",
    type=click.STRING,
    required=True,
    envvar="DOCKER_HUB_USERNAME",
)
@click.option(
    "--docker-hub-password",
    help="Your password to connect to DockerHub.",
    type=click.STRING,
    required=True,
    envvar="DOCKER_HUB_PASSWORD",
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
    default="#publish-on-merge-updates",
)
@click.pass_context
def publish(
    ctx: click.Context,
    pre_release: bool,
    spec_cache_gcs_credentials: str,
    spec_cache_bucket_name: str,
    metadata_service_bucket_name: str,
    metadata_service_gcs_credentials: str,
    docker_hub_username: str,
    docker_hub_password: str,
    slack_webhook: str,
    slack_channel: str,
):
    ctx.obj["spec_cache_gcs_credentials"] = spec_cache_gcs_credentials
    ctx.obj["spec_cache_bucket_name"] = spec_cache_bucket_name
    ctx.obj["metadata_service_bucket_name"] = metadata_service_bucket_name
    ctx.obj["metadata_service_gcs_credentials"] = metadata_service_gcs_credentials

    validate_publish_options(pre_release, ctx.obj)
    if ctx.obj["is_local"]:
        click.confirm(
            "Publishing from a local environment is not recommend and requires to be logged in Airbyte's DockerHub registry, do you want to continue?",
            abort=True,
        )
    if ctx.obj["modified"]:
        selected_connectors_and_files = get_modified_connectors(get_modified_metadata_files(ctx.obj["modified_files"]))
        selected_connectors_names = [connector.technical_name for connector in selected_connectors_and_files.keys()]
    else:
        selected_connectors_and_files = ctx.obj["selected_connectors_and_files"]
        selected_connectors_names = ctx.obj["selected_connectors_names"]

    main_logger.info(f"Will publish the following connectors: {', '.join(selected_connectors_names)}")
    publish_connector_contexts = reorder_contexts(
        [
            PublishConnectorContext(
                connector=connector,
                pre_release=pre_release,
                modified_files=modified_files,
                spec_cache_gcs_credentials=spec_cache_gcs_credentials,
                spec_cache_bucket_name=spec_cache_bucket_name,
                metadata_service_gcs_credentials=metadata_service_gcs_credentials,
                metadata_bucket_name=metadata_service_bucket_name,
                docker_hub_username=docker_hub_username,
                docker_hub_password=docker_hub_password,
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
            )
            for connector, modified_files in selected_connectors_and_files.items()
        ]
    )

    main_logger.warn("Concurrency is forced to 1. For stability reasons we disable parallel publish pipelines.")
    ctx.obj["concurrency"] = 1

    publish_connector_contexts = anyio.run(
        run_connectors_pipelines,
        publish_connector_contexts,
        run_connector_publish_pipeline,
        "Publishing connectors",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
    )
    return all(context.state is ContextState.SUCCESSFUL for context in publish_connector_contexts)


def validate_publish_options(pre_release: bool, context_object: Dict[str, Any]):
    """Validate that the publish options are set correctly."""
    for k in ["spec_cache_bucket_name", "spec_cache_gcs_credentials", "metadata_service_bucket_name", "metadata_service_gcs_credentials"]:
        if not pre_release and context_object.get(k) is None:
            click.Abort(f'The --{k.replace("_", "-")} option is required when running a main release publish pipeline.')


@connectors.command(cls=DaggerPipelineCommand, help="List all selected connectors.")
@click.pass_context
def list(
    ctx: click.Context,
):
    selected_connectors = [
        (connector, bool(modified_files))
        for connector, modified_files in ctx.obj["selected_connectors_and_files"].items()
        if connector.metadata
    ]

    selected_connectors = sorted(selected_connectors, key=lambda x: x[0].technical_name)
    table = Table(title=f"{len(selected_connectors)} selected connectors")
    table.add_column("Modified")
    table.add_column("Connector")
    table.add_column("Language")
    table.add_column("Release stage")
    table.add_column("Version")
    table.add_column("Folder")

    for connector, modified in selected_connectors:
        modified = "X" if modified else ""
        connector_name = Text(connector.technical_name)
        language = Text(connector.language.value) if connector.language else "N/A"
        release_stage = Text(connector.release_stage)
        version = Text(connector.version)
        folder = Text(str(connector.code_directory))
        table.add_row(modified, connector_name, language, release_stage, version, folder)

    console.print(table)
    return True


@connectors.command(cls=DaggerPipelineCommand, help="Autoformat connector code.")
@click.pass_context
def format(ctx: click.Context) -> bool:

    if ctx.obj["modified"]:
        # We only want to format the connector that with modified files on the current branch.
        connectors_and_files_to_format = [
            (connector, modified_files) for connector, modified_files in ctx.obj["selected_connectors_and_files"].items() if modified_files
        ]
    else:
        # We explicitly want to format specific connectors
        connectors_and_files_to_format = [
            (connector, modified_files) for connector, modified_files in ctx.obj["selected_connectors_and_files"].items()
        ]

    if connectors_and_files_to_format:
        main_logger.info(
            f"Will format the following connectors: {', '.join([connector.technical_name for connector, _ in connectors_and_files_to_format])}."
        )
    else:
        main_logger.info("No connectors to format.")
    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Format connector {connector.technical_name}",
            connector=connector,
            is_local=ctx.obj["is_local"],
            git_branch=ctx.obj["git_branch"],
            git_revision=ctx.obj["git_revision"],
            modified_files=modified_files,
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
            pull_request=ctx.obj.get("pull_request"),
            should_save_report=False,
        )
        for connector, modified_files in connectors_and_files_to_format
    ]

    anyio.run(
        run_connectors_format_pipelines,
        connectors_contexts,
        ctx.obj["ci_git_user"],
        ctx.obj["ci_github_access_token"],
        ctx.obj["git_branch"],
        ctx.obj["is_local"],
        ctx.obj["execute_timeout"],
    )

    return True
