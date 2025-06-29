#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from pathlib import Path
from typing import List, Set, Tuple

import asyncclick as click
from connector_ops.utils import Connector, ConnectorLanguage, SupportLevelEnum, get_all_connectors_in_repo  # type: ignore

from pipelines import main_logger
from pipelines.cli.airbyte_ci import wrap_in_secret
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles, get_connector_modified_files, get_modified_connectors
from pipelines.helpers.git import get_modified_files
from pipelines.helpers.utils import transform_strs_to_paths

ALL_CONNECTORS = get_all_connectors_in_repo()
CONNECTORS_WITH_STRICT_ENCRYPT_VARIANTS = {
    Connector(c.relative_connector_path.replace("-strict-encrypt", ""))
    for c in ALL_CONNECTORS
    if c.technical_name.endswith("-strict-encrypt")
}


def log_selected_connectors(selected_connectors_with_modified_files: List[ConnectorWithModifiedFiles]) -> None:
    """Logs selected connector names into main logger, or says no connectors to run."""
    if selected_connectors_with_modified_files:
        selected_connectors_names = [c.technical_name for c in selected_connectors_with_modified_files]
        main_logger.info(f"Will run on the following {len(selected_connectors_names)} connectors: {', '.join(selected_connectors_names)}.")
    else:
        main_logger.info("No connectors to run.")


def get_base_connector_and_variants(connector: Connector) -> Set[Connector]:
    """Returns the connector's name and it's strict-encrypt variant."""
    base_connector_path = connector.relative_connector_path.replace("-strict-encrypt", "")
    base_connector = Connector(base_connector_path)
    strict_encrypt_connector_path = f"{base_connector.relative_connector_path}-strict-encrypt"
    if base_connector in CONNECTORS_WITH_STRICT_ENCRYPT_VARIANTS:
        return {base_connector, Connector(strict_encrypt_connector_path)}
    else:
        return {base_connector}


def update_selected_connectors_with_variants(selected_connectors: Set[Connector]) -> Set[Connector]:
    """Returns the connectors and their variants."""
    updated_selected_connectors = set()
    for selected_connector in selected_connectors:
        updated_selected_connectors.update(get_base_connector_and_variants(selected_connector))
    return updated_selected_connectors


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

    # We always want to pair selection of a base connector with its variant, e vice versa
    selected_connectors = update_selected_connectors_with_variants(selected_connectors)

    selected_connectors_with_modified_files = []
    for connector in selected_connectors:
        connector_with_modified_files = ConnectorWithModifiedFiles(
            relative_connector_path=connector.relative_connector_path,
            modified_files=get_connector_modified_files(connector, modified_files),
        )
        if not metadata_changes_only:
            selected_connectors_with_modified_files.append(connector_with_modified_files)
        else:
            if connector_with_modified_files.has_metadata_change:
                selected_connectors_with_modified_files.append(connector_with_modified_files)

    return selected_connectors_with_modified_files


def validate_environment(is_local: bool) -> None:
    """Check if the required environment variables exist."""
    if is_local:
        if not Path(".git").is_dir():
            raise click.UsageError("You need to run this command from the repository root.")
    else:
        required_env_vars_for_ci = [
            "CI_GITHUB_ACCESS_TOKEN",
            "DOCKER_HUB_USERNAME",
            "DOCKER_HUB_PASSWORD",
        ]
        for required_env_var in required_env_vars_for_ci:
            if os.getenv(required_env_var) is None:
                raise click.UsageError(f"When running in a CI context a {required_env_var} environment variable must be set.")


@click.group(
    cls=LazyGroup,
    help="Commands related to connectors and connector acceptance tests.",
    lazy_subcommands={
        "build": "pipelines.airbyte_ci.connectors.build_image.commands.build",
        "test": "pipelines.airbyte_ci.connectors.test.commands.test",
        "list": "pipelines.airbyte_ci.connectors.list.commands.list_connectors",
        "publish": "pipelines.airbyte_ci.connectors.publish.commands.publish",
        "bump-version": "pipelines.airbyte_ci.connectors.bump_version.commands.bump_version",
        "migrate-to-manifest-only": "pipelines.airbyte_ci.connectors.migrate_to_manifest_only.commands.migrate_to_manifest_only",
        "migrate-to-inline-schemas": "pipelines.airbyte_ci.connectors.migrate_to_inline_schemas.commands.migrate_to_inline_schemas",
        "generate-erd": "pipelines.airbyte_ci.connectors.generate_erd.commands.generate_erd",
        "upgrade-cdk": "pipelines.airbyte_ci.connectors.upgrade_cdk.commands.upgrade_cdk",
        "up-to-date": "pipelines.airbyte_ci.connectors.up_to_date.commands.up_to_date",
        "pull-request": "pipelines.airbyte_ci.connectors.pull_request.commands.pull_request",
    },
)
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
@click.option(
    "--modified/--not-modified",
    help="Only test modified connectors in the current branch. Archived connectors are ignored",
    default=False,
    type=bool,
)
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
    "--use-cdk-ref",
    help=(
        "Build with the airbyte-cdk from the specified git ref. "
        "This is useful for testing against dev versions or previous versions of the CDK. "
        "Ignored for java connectors and if `--use-local-cdk` is set."
    ),
    type=str,
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
    callback=wrap_in_secret,
)
@click.option(
    "--docker-hub-password",
    help="Your password to connect to DockerHub.",
    type=click.STRING,
    required=False,
    envvar="DOCKER_HUB_PASSWORD",
    callback=wrap_in_secret,
)
@click_merge_args_into_context_obj
@click.pass_context
@click_ignore_unused_kwargs
async def connectors(
    ctx: click.Context,
) -> None:
    """Group all the connectors-ci command."""
    validate_environment(ctx.obj["is_local"])

    modified_files = []
    if ctx.obj["modified"] or ctx.obj["metadata_changes_only"]:
        modified_files = transform_strs_to_paths(
            await get_modified_files(
                ctx.obj["git_branch"],
                ctx.obj["git_revision"],
                ctx.obj["diffed_branch"],
                ctx.obj["is_local"],
                ctx.obj["ci_context"],
                ctx.obj["git_repo_url"],
            )
        )

    ctx.obj["selected_connectors_with_modified_files"] = get_selected_connectors_with_modified_files(
        ctx.obj["names"],
        ctx.obj["support_levels"],
        ctx.obj["languages"],
        ctx.obj["modified"],
        ctx.obj["metadata_changes_only"],
        ctx.obj["metadata_query"],
        set(modified_files),
        ctx.obj["enable_dependency_scanning"],
    )
    log_selected_connectors(ctx.obj["selected_connectors_with_modified_files"])
