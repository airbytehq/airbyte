#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Set, Tuple

import asyncclick as click
import asyncer
import dagger
from connector_ops.utils import SCAFFOLD_CONNECTOR_GLOB, Connector, ConnectorLanguage, SupportLevelEnum
from pipelines import main_logger
from pipelines.cli.click_decorators import click_append_to_context_object, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.helpers.connectors.modifed import RepoConnector, get_connector_modified_files, get_modified_connectors
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


async def get_all_connectors_in_directory(
    dagger_client: dagger.Client, target_repo_dir: dagger.Directory, searched_directory_name: str, ignore_glob: Optional[List[str]] = None
) -> Set[Connector]:
    """Retrieve a set of all Connectors in a directory, searches subdirectories.
    We globe the connectors folder for metadata.yaml files and construct Connectors from the directory name.

    Args:
        dagger_client (dagger.Client): The dagger client.
        searched_directory (dagger.Directory): The directory where connectors subdirectories are located.
        ignore_glob (List[str]): List of strings that will be used to ignore connectors if they match connector directory name.
    Returns:
        A set of Connectors.
    """

    def is_ignored(metadata_file):
        if ignore_glob is None:
            return False
        for glob in ignore_glob:
            if glob in metadata_file:
                return True
        return False

    container_with_repo = (
        dagger_client.container().from_("bash:latest").with_workdir("/repo").with_mounted_directory("/repo", target_repo_dir)
    )
    all_metadata_files = (
        await container_with_repo.with_exec(["find", searched_directory_name, "-name", "metadata.yaml"]).stdout()
    ).splitlines()
    async with asyncer.create_task_group() as task_group:
        tasks = []
        for metadata_file in all_metadata_files:
            if not is_ignored(metadata_file):
                relative_connector_path = str(Path(metadata_file).parent)
            connector_directory = target_repo_dir.directory(relative_connector_path)
            tasks.append(task_group.soonify(RepoConnector.load_from_directory)(relative_connector_path, connector_directory))
    return {t.value for t in tasks}


def log_selected_connectors(selected_connectors_with_modified_files: List[RepoConnector]) -> None:
    if selected_connectors_with_modified_files:
        selected_connectors_names = [c.technical_name for c in selected_connectors_with_modified_files]
        main_logger.info(f"Will run on the following {len(selected_connectors_names)} connectors: {', '.join(selected_connectors_names)}.")
    else:
        main_logger.info("No connectors to run.")


def get_selected_connectors_with_modified_files(
    all_connectors: Set[RepoConnector],
    selected_names: Tuple[str],
    selected_support_levels: Tuple[str],
    selected_languages: Tuple[str],
    modified: bool,
    metadata_changes_only: bool,
    metadata_query: str,
    modified_files: Set[Path],
    enable_dependency_scanning: bool = False,
) -> List[RepoConnector]:
    """Get the connectors that match the selected criteria.

    Args:
        all_connectors (Set[str]): All the connectors in the repository.
        selected_names (Tuple[str]): Selected connector names.
        selected_support_levels (Tuple[str]): Selected connector support levels.
        selected_languages (Tuple[str]): Selected connector languages.
        modified (bool): Whether to select the modified connectors.
        metadata_changes_only (bool): Whether to select only the connectors with metadata changes.
        modified_files (Set[Path]): The modified files.
        enable_dependency_scanning (bool): Whether to enable the dependency scanning.
    Returns:
        List[RepoConnector]: The connectors that match the selected criteria.
    """

    if metadata_changes_only and not modified:
        main_logger.info("--metadata-changes-only overrides --modified")
        modified = True

    selected_modified_connectors = (
        get_modified_connectors(modified_files, all_connectors, enable_dependency_scanning) if modified else set()
    )
    selected_connectors_by_name = {c for c in all_connectors if c.technical_name in selected_names}
    selected_connectors_by_support_level = {connector for connector in all_connectors if connector.support_level in selected_support_levels}
    selected_connectors_by_language = {connector for connector in all_connectors if connector.language in selected_languages}
    selected_connectors_by_query = (
        {connector for connector in all_connectors if connector.metadata_query_match(metadata_query)} if metadata_query else set()
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
        connector.modified_files = get_connector_modified_files(connector, modified_files)

        if not metadata_changes_only:
            selected_connectors_with_modified_files.append(connector)
        else:
            if connector.has_metadata_change:
                selected_connectors_with_modified_files.append(connector)
    return selected_connectors_with_modified_files


def validate_environment(is_local: bool):
    """Check if the required environment variables exist."""
    if not is_local:
        required_env_vars_for_ci = [
            "GCP_GSM_CREDENTIALS",
            "CI_REPORT_BUCKET_NAME",
            "CI_GITHUB_ACCESS_TOKEN",
            "DOCKER_HUB_USERNAME",
            "DOCKER_HUB_PASSWORD",
        ]
        for required_env_var in required_env_vars_for_ci:
            if os.getenv(required_env_var) is None:
                raise click.UsageError(f"When running in a CI context a {required_env_var} environment variable must be set.")


def should_use_remote_secrets(use_remote_secrets: Optional[bool]) -> bool:
    """Check if the connector secrets should be loaded from Airbyte GSM or from the local secrets directory.

    Args:
        use_remote_secrets (Optional[bool]): Whether to use remote connector secrets or local connector secrets according to user inputs.

    Raises:
        click.UsageError: If the --use-remote-secrets flag was provided but no GCP_GSM_CREDENTIALS environment variable was found.

    Returns:
        bool: Whether to use remote connector secrets (True) or local connector secrets (False).
    """
    gcp_gsm_credentials_is_set = bool(os.getenv("GCP_GSM_CREDENTIALS"))
    if use_remote_secrets is None:
        if gcp_gsm_credentials_is_set:
            main_logger.info("GCP_GSM_CREDENTIALS environment variable found, using remote connector secrets.")
            return True
        else:
            main_logger.info("No GCP_GSM_CREDENTIALS environment variable found, using local connector secrets.")
            return False
    if use_remote_secrets:
        if gcp_gsm_credentials_is_set:
            main_logger.info("GCP_GSM_CREDENTIALS environment variable found, using remote connector secrets.")
            return True
        else:
            raise click.UsageError("The --use-remote-secrets flag was provided but no GCP_GSM_CREDENTIALS environment variable was found.")
    else:
        main_logger.info("Using local connector secrets as the --use-local-secrets flag was provided")
        return False


@click.group(
    cls=LazyGroup,
    help="Commands related to connectors and connector acceptance tests.",
    lazy_subcommands={
        "build": "pipelines.airbyte_ci.connectors.build_image.commands.build",
        "test": "pipelines.airbyte_ci.connectors.test.commands.test",
        "list": "pipelines.airbyte_ci.connectors.list.commands.list_connectors",
        "publish": "pipelines.airbyte_ci.connectors.publish.commands.publish",
        "bump_version": "pipelines.airbyte_ci.connectors.bump_version.commands.bump_version",
        "migrate_to_base_image": "pipelines.airbyte_ci.connectors.migrate_to_base_image.commands.migrate_to_base_image",
        "upgrade_base_image": "pipelines.airbyte_ci.connectors.upgrade_base_image.commands.upgrade_base_image",
    },
)
@click.option(
    "--use-remote-secrets/--use-local-secrets",
    help="Use Airbyte GSM connector secrets or local connector secrets.",
    type=bool,
    default=None,
)
@click.option(
    "--name",
    "names",
    multiple=True,
    help="Only test a specific connector. Use its technical name. e.g source-pokeapi.",
    type=str,
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
@click.option(
    "--docker-hub-username",
    help="Your username to connect to DockerHub.",
    type=click.STRING,
    required=False,
    envvar="DOCKER_HUB_USERNAME",
)
@click.option(
    "--docker-hub-password",
    help="Your password to connect to DockerHub.",
    type=click.STRING,
    required=False,
    envvar="DOCKER_HUB_PASSWORD",
)
@click.option(
    "--connectors_directory",
    help="Path to the directory containing the connectors in the target repo.",
    type=click.STRING,
    default="airbyte-integrations/connectors",
)
@click.option(
    "--ignored_connectors_glob",
    help="String that will be used to ignore connectors if they match connector directory name.",
    type=click.STRING,
    multiple=True,
    default=[SCAFFOLD_CONNECTOR_GLOB],
)
@click_merge_args_into_context_obj
@click_append_to_context_object("use_remote_secrets", lambda ctx: should_use_remote_secrets(ctx.obj["use_remote_secrets"]))
@click.pass_context
@pass_pipeline_context
@click_ignore_unused_kwargs
async def connectors(ctx: click.Context, pipeline_context: ClickPipelineContext):
    """Group all the connectors-ci command."""
    validate_environment(ctx.obj["is_local"])
    dagger_client = await pipeline_context.get_dagger_client("connector")
    ctx.obj["all_connectors"] = await get_all_connectors_in_directory(
        dagger_client,
        ctx.obj["target_repo_state"].repo_dir,
        ctx.obj["connectors_directory"],
        ignore_glob=ctx.obj["ignored_connectors_glob"],
    )
    ctx.obj["selected_connectors_with_modified_files"] = get_selected_connectors_with_modified_files(
        ctx.obj["all_connectors"],
        ctx.obj["names"],
        ctx.obj["support_levels"],
        ctx.obj["languages"],
        ctx.obj["modified"],
        ctx.obj["metadata_changes_only"],
        ctx.obj["metadata_query"],
        ctx.obj["target_repo_state"].modified_files,
        ctx.obj["enable_dependency_scanning"],
    )
    log_selected_connectors(ctx.obj["selected_connectors_with_modified_files"])
