#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares the CLI commands to run the connectors CI pipelines."""

import os
import sys
from pathlib import Path
from typing import List, Set, Tuple

import anyio
import click
from connector_ops.utils import ConnectorLanguage, SupportLevelEnum, console, get_all_connectors_in_repo
from pipelines import main_logger
from pipelines.bases import ConnectorWithModifiedFiles
from pipelines.builds import run_connector_build_pipeline
from pipelines.connector_changes.base_image_version_migration import (
    run_connector_base_image_upgrade_pipeline,
    run_connector_migration_to_base_image_pipeline,
)
from pipelines.connector_changes.version_bump import run_connector_version_bump_pipeline
from pipelines.contexts import ConnectorContext, ContextState, PublishConnectorContext
from pipelines.format import run_connector_format_pipeline
from pipelines.github import update_global_commit_status_check_for_tests
from pipelines.pipelines.connectors import run_connectors_pipelines
from pipelines.publish import reorder_contexts, run_connector_publish_pipeline
from pipelines.tests import run_connector_test_pipeline
from pipelines.utils import DaggerPipelineCommand, get_connector_modified_files, get_modified_connectors
from rich.table import Table
from rich.text import Text

# HELPERS

ALL_CONNECTORS = get_all_connectors_in_repo()


def validate_environment(is_local: bool, use_remote_secrets: bool):
    """Check if the required environment variables exist."""
    if is_local:
        if not Path(".git").is_dir():
            raise click.UsageError("You need to run this command from the repository root.")
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


def get_selected_connectors_with_modified_files(
    selected_names: Tuple[str],
    selected_support_levels: Tuple[str],
    selected_languages: Tuple[str],
    modified: bool,
    metadata_changes_only: bool,
    metadata_query: str,
    modified_files: Set[Path],
    enable_dependency_scanning: bool = False,
) -> List[ConnectorWithModifiedFiles]:
    """Get the connectors that match the selected criteria.

    Args:
        selected_names (Tuple[str]): Selected connector names.
        selected_support_levels (Tuple[str]): Selected connector support levels.
        selected_languages (Tuple[str]): Selected connector languages.
        modified (bool): Whether to select the modified connectors.
        metadata_changes_only (bool): Whether to select only the connectors with metadata changes.
        modified_files (Set[Path]): The modified files.
        enable_dependency_scanning (bool): Whether to enable the dependency scanning.
    Returns:
        List[ConnectorWithModifiedFiles]: The connectors that match the selected criteria.
    """

    if metadata_changes_only and not modified:
        main_logger.info("--metadata-changes-only overrides --modified")
        modified = True

    selected_modified_connectors = (
        get_modified_connectors(modified_files, ALL_CONNECTORS, enable_dependency_scanning) if modified else set()
    )
    selected_connectors_by_name = {c for c in ALL_CONNECTORS if c.technical_name in selected_names}
    selected_connectors_by_support_level = {connector for connector in ALL_CONNECTORS if connector.support_level in selected_support_levels}
    selected_connectors_by_language = {connector for connector in ALL_CONNECTORS if connector.language in selected_languages}
    selected_connectors_by_query = (
        {connector for connector in ALL_CONNECTORS if connector.metadata_query_match(metadata_query)} if metadata_query else set()
    )

    non_empty_connector_sets = [
        connector_set
        for connector_set in [
            selected_connectors_by_name,
            selected_connectors_by_support_level,
            selected_connectors_by_language,
            selected_connectors_by_query,
            selected_modified_connectors,
        ]
        if connector_set
    ]
    # The selected connectors are the intersection of the selected connectors by name, support_level, language, simpleeval query and modified.
    selected_connectors = set.intersection(*non_empty_connector_sets) if non_empty_connector_sets else set()

    selected_connectors_with_modified_files = []
    for connector in selected_connectors:
        connector_with_modified_files = ConnectorWithModifiedFiles(
            technical_name=connector.technical_name, modified_files=get_connector_modified_files(connector, modified_files)
        )
        if not metadata_changes_only:
            selected_connectors_with_modified_files.append(connector_with_modified_files)
        else:
            if connector_with_modified_files.has_metadata_change:
                selected_connectors_with_modified_files.append(connector_with_modified_files)
    return selected_connectors_with_modified_files


# COMMANDS


@click.group(help="Commands related to connectors and connector acceptance tests.")
@click.option("--use-remote-secrets", default=True)  # specific to connectors
@click.option(
    "--name",
    "names",
    multiple=True,
    help="Only test a specific connector. Use its technical name. e.g source-pokeapi.",
    type=click.Choice([c.technical_name for c in ALL_CONNECTORS]),
)
@click.option("--language", "languages", multiple=True, help="Filter connectors to test by language.", type=click.Choice(ConnectorLanguage))
@click.option(
    "--support-level",
    "support_levels",
    multiple=True,
    help="Filter connectors to test by support_level.",
    type=click.Choice(SupportLevelEnum),
)
@click.option("--modified/--not-modified", help="Only test modified connectors in the current branch.", default=False, type=bool)
@click.option(
    "--metadata-changes-only/--not-metadata-changes-only",
    help="Only test connectors with modified metadata files in the current branch.",
    default=False,
    type=bool,
)
@click.option(
    "--metadata-query",
    help="Filter connectors by metadata query using `simpleeval`. e.g. 'data.ab_internal.ql == 200'",
    type=str,
)
@click.option("--concurrency", help="Number of connector tests pipeline to run in parallel.", default=5, type=int)
@click.option(
    "--execute-timeout",
    help="The maximum time in seconds for the execution of a Dagger request before an ExecuteTimeoutError is raised. Passing None results in waiting forever.",
    default=None,
    type=int,
)
@click.option(
    "--enable-dependency-scanning/--disable-dependency-scanning",
    help="When enabled, the dependency scanning will be performed to detect the connectors to test according to a dependency change.",
    default=False,
    type=bool,
)
@click.option(
    "--use-local-cdk",
    is_flag=True,
    help=("Build with the airbyte-cdk from the local repository. " "This is useful for testing changes to the CDK."),
    default=False,
    type=bool,
)
@click.option(
    "--enable-report-auto-open/--disable-report-auto-open",
    is_flag=True,
    help=("When enabled, finishes by opening a browser window to display an HTML report."),
    default=True,
    type=bool,
)
@click.pass_context
def connectors(
    ctx: click.Context,
    use_remote_secrets: bool,
    names: Tuple[str],
    languages: Tuple[ConnectorLanguage],
    support_levels: Tuple[str],
    modified: bool,
    metadata_changes_only: bool,
    metadata_query: str,
    concurrency: int,
    execute_timeout: int,
    enable_dependency_scanning: bool,
    use_local_cdk: bool,
    enable_report_auto_open: bool,
):
    """Group all the connectors-ci command."""
    validate_environment(ctx.obj["is_local"], use_remote_secrets)

    ctx.ensure_object(dict)
    ctx.obj["use_remote_secrets"] = use_remote_secrets
    ctx.obj["concurrency"] = concurrency
    ctx.obj["execute_timeout"] = execute_timeout
    ctx.obj["use_local_cdk"] = use_local_cdk
    ctx.obj["open_report_in_browser"] = enable_report_auto_open
    ctx.obj["selected_connectors_with_modified_files"] = get_selected_connectors_with_modified_files(
        names,
        support_levels,
        languages,
        modified,
        metadata_changes_only,
        metadata_query,
        ctx.obj["modified_files"],
        enable_dependency_scanning,
    )
    log_selected_connectors(ctx.obj["selected_connectors_with_modified_files"])


@connectors.command(cls=DaggerPipelineCommand, help="Test all the selected connectors.")
@click.option(
    "--code-tests-only",
    is_flag=True,
    help=("Only execute code tests. " "Metadata checks, QA, and acceptance tests will be skipped."),
    default=False,
    type=bool,
)
@click.option(
    "--fail-fast",
    help="When enabled, tests will fail fast.",
    default=False,
    type=bool,
    is_flag=True,
)
@click.option(
    "--fast-tests-only",
    help="When enabled, slow tests are skipped.",
    default=False,
    type=bool,
    is_flag=True,
)
@click.pass_context
def test(
    ctx: click.Context,
    code_tests_only: bool,
    fail_fast: bool,
    fast_tests_only: bool,
) -> bool:
    """Runs a test pipeline for the selected connectors.

    Args:
        ctx (click.Context): The click context.
    """
    if ctx.obj["is_ci"] and ctx.obj["pull_request"] and ctx.obj["pull_request"].draft:
        main_logger.info("Skipping connectors tests for draft pull request.")
        sys.exit(0)

    if ctx.obj["selected_connectors_with_modified_files"]:
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
            ci_report_bucket=ctx.obj["ci_report_bucket_name"],
            report_output_prefix=ctx.obj["report_output_prefix"],
            use_remote_secrets=ctx.obj["use_remote_secrets"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            dagger_logs_url=ctx.obj.get("dagger_logs_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
            pull_request=ctx.obj.get("pull_request"),
            ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
            fail_fast=fail_fast,
            fast_tests_only=fast_tests_only,
            code_tests_only=code_tests_only,
            use_local_cdk=ctx.obj.get("use_local_cdk"),
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
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
@click.option(
    "--use-host-gradle-dist-tar",
    is_flag=True,
    help="Use gradle distTar output from host for java connectors.",
    default=False,
    type=bool,
)
@click.pass_context
def build(ctx: click.Context, use_host_gradle_dist_tar: bool) -> bool:
    """Runs a build pipeline for the selected connectors."""

    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Build connector {connector.technical_name}",
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
            use_local_cdk=ctx.obj.get("use_local_cdk"),
            open_report_in_browser=ctx.obj.get("open_report_in_browser"),
            use_host_gradle_dist_tar=use_host_gradle_dist_tar,
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]
    if use_host_gradle_dist_tar and not ctx.obj["is_local"]:
        raise Exception("flag --use-host-gradle-dist-tar requires --is-local")
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
    default="#connector-publish-updates",
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
    if ctx.obj["is_local"]:
        click.confirm(
            "Publishing from a local environment is not recommended and requires to be logged in Airbyte's DockerHub registry, do you want to continue?",
            abort=True,
        )

    publish_connector_contexts = reorder_contexts(
        [
            PublishConnectorContext(
                connector=connector,
                pre_release=pre_release,
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
            for connector in ctx.obj["selected_connectors_with_modified_files"]
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


@connectors.command(cls=DaggerPipelineCommand, help="List all selected connectors.")
@click.pass_context
def list(
    ctx: click.Context,
):
    selected_connectors = sorted(ctx.obj["selected_connectors_with_modified_files"], key=lambda x: x.technical_name)
    table = Table(title=f"{len(selected_connectors)} selected connectors")
    table.add_column("Modified")
    table.add_column("Connector")
    table.add_column("Language")
    table.add_column("Release stage")
    table.add_column("Version")
    table.add_column("Folder")

    for connector in selected_connectors:
        modified = "X" if connector.modified_files else ""
        connector_name = Text(connector.technical_name)
        language = Text(connector.language.value) if connector.language else "N/A"
        try:
            support_level = Text(connector.support_level)
        except Exception:
            support_level = "N/A"
        try:
            version = Text(connector.version)
        except Exception:
            version = "N/A"
        folder = Text(str(connector.code_directory))
        table.add_row(modified, connector_name, language, support_level, version, folder)

    console.print(table)
    return True


@connectors.command(name="format", cls=DaggerPipelineCommand, help="Autoformat connector code.")
@click.pass_context
def format_code(ctx: click.Context) -> bool:
    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Format connector {connector.technical_name}",
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
            pull_request=ctx.obj.get("pull_request"),
            should_save_report=False,
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    anyio.run(
        run_connectors_pipelines,
        connectors_contexts,
        run_connector_format_pipeline,
        "Format connectors pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
    )

    return True


@connectors.command(cls=DaggerPipelineCommand, help="Upgrades the base image version used by the selected connectors..")
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


@connectors.command(cls=DaggerPipelineCommand, help="Bump a connector version: update metadata.yaml and changelog.")
@click.argument("bump-type", type=click.Choice(["patch", "minor", "major"]))
@click.argument("pull-request-number", type=str)
@click.argument("changelog-entry", type=str)
@click.pass_context
def bump_version(
    ctx: click.Context,
    bump_type: str,
    pull_request_number: str,
    changelog_entry: str,
) -> bool:
    """Bump a connector version: update metadata.yaml and changelog."""

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
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    anyio.run(
        run_connectors_pipelines,
        connectors_contexts,
        run_connector_version_bump_pipeline,
        "Version bump pipeline pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        bump_type,
        changelog_entry,
        pull_request_number,
    )

    return True


@connectors.command(
    cls=DaggerPipelineCommand,
    help="Make the selected connectors use our base image: remove dockerfile, update metadata.yaml and update documentation.",
)
@click.argument("pull-request-number", type=str)
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
def migrate_to_base_image(
    ctx: click.Context,
    pull_request_number: str,
    docker_hub_username: str,
    docker_hub_password: str,
) -> bool:
    """Bump a connector version: update metadata.yaml, changelog and delete legacy files."""

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
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    anyio.run(
        run_connectors_pipelines,
        connectors_contexts,
        run_connector_migration_to_base_image_pipeline,
        "Migration to base image pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        pull_request_number,
    )

    return True


def log_selected_connectors(selected_connectors_with_modified_files: List[ConnectorWithModifiedFiles]) -> None:
    if selected_connectors_with_modified_files:
        selected_connectors_names = [c.technical_name for c in selected_connectors_with_modified_files]
        main_logger.info(f"Will run on the following {len(selected_connectors_names)} connectors: {', '.join(selected_connectors_names)}.")
    else:
        main_logger.info("No connectors to run.")
