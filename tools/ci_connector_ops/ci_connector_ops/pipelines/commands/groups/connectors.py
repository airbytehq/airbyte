#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares the CLI commands to run the connectors CI pipelines."""

import logging
import os
import sys
from pathlib import Path
from typing import Tuple

import anyio
import click
import dagger
from ci_connector_ops.pipelines.contexts import CIContext, ConnectorContext
from ci_connector_ops.pipelines.github import update_commit_status_check
from ci_connector_ops.pipelines.pipelines.connectors import run_connectors_build_pipelines, run_connectors_test_pipelines
from ci_connector_ops.pipelines.utils import DaggerPipelineCommand, get_modified_connectors
from ci_connector_ops.utils import ConnectorLanguage, get_all_released_connectors
from rich.logging import RichHandler

# CONSTANTS

GITHUB_GLOBAL_CONTEXT = "[POC please ignore] Connectors CI"
GITHUB_GLOBAL_DESCRIPTION = "Running connectors tests"

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])

logger = logging.getLogger(__name__)


# HELPERS


def validate_environment(is_local: bool, use_remote_secrets: bool):
    """Check if the required environment variables exist."""
    if is_local:
        if not (os.getcwd().endswith("/airbyte") and Path(".git").is_dir()):
            raise click.UsageError("You need to run this command from the airbyte repository root.")
    else:
        required_env_vars_for_ci = [
            "GCP_GSM_CREDENTIALS",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_DEFAULT_REGION",
            "TEST_REPORTS_BUCKET_NAME",
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
@click.pass_context
def connectors(
    ctx: click.Context,
    use_remote_secrets: str,
    names: Tuple[str],
    languages: Tuple[ConnectorLanguage],
    release_stages: Tuple[str],
    modified: bool,
    concurrency: int,
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
    update_commit_status_check(
        ctx.obj["git_revision"],
        "pending",
        ctx.obj["gha_workflow_run_url"],
        GITHUB_GLOBAL_DESCRIPTION,
        GITHUB_GLOBAL_CONTEXT,
        should_send=ctx.obj["ci_context"] == CIContext.PULL_REQUEST,
        logger=logger,
    )

    selected_connectors = get_all_released_connectors()
    modified_connectors = get_modified_connectors(ctx.obj["modified_files_in_branch"])
    if modified:
        selected_connectors = modified_connectors
    else:
        selected_connectors.update(modified_connectors)
    if names:
        selected_connectors = {connector for connector in selected_connectors if connector.technical_name in names}
    if languages:
        selected_connectors = {connector for connector in selected_connectors if connector.language in languages}
    if release_stages:
        selected_connectors = {connector for connector in selected_connectors if connector.release_stage in release_stages}

    if not selected_connectors:
        click.secho("No connector were selected according to your inputs. Please double check your filters.", fg="yellow")
        sys.exit(0)

    ctx.obj["selected_connectors"] = selected_connectors
    ctx.obj["selected_connectors_names"] = [c.technical_name for c in selected_connectors]


@connectors.command(cls=DaggerPipelineCommand, help="Test all the selected connectors.")
@click.pass_context
def test(
    ctx: click.Context,
) -> bool:
    """Runs a test pipeline for the selected connectors.

    Args:
        ctx (click.Context): The click context.
    """
    click.secho(f"Will run the test pipeline for the following connectors: {', '.join(ctx.obj['selected_connectors_names'])}.", fg="green")

    connectors_tests_contexts = [
        ConnectorContext(
            connector,
            ctx.obj["is_local"],
            ctx.obj["git_branch"],
            ctx.obj["git_revision"],
            ctx.obj["use_remote_secrets"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
        )
        for connector in ctx.obj["selected_connectors"]
    ]
    try:
        anyio.run(run_connectors_test_pipelines, connectors_tests_contexts, ctx.obj["concurrency"])
        update_commit_status_check(
            ctx.obj["git_revision"],
            "success",
            ctx.obj["gha_workflow_run_url"],
            GITHUB_GLOBAL_DESCRIPTION,
            GITHUB_GLOBAL_CONTEXT,
            should_send=ctx.obj.get("ci_context") == CIContext.PULL_REQUEST,
            logger=logger,
        )
    except dagger.DaggerError as e:
        click.secho(str(e), err=True, fg="red")
        update_commit_status_check(
            ctx.obj["git_revision"],
            "error",
            ctx.obj["gha_workflow_run_url"],
            GITHUB_GLOBAL_DESCRIPTION,
            GITHUB_GLOBAL_CONTEXT,
            should_send=ctx.obj.get("ci_context") == CIContext.PULL_REQUEST,
            logger=logger,
        )
        return False
    return True


@connectors.command(cls=DaggerPipelineCommand, help="Build all images for the selected connectors.")
@click.pass_context
def build(ctx: click.Context) -> bool:
    click.secho(f"Will build the following connectors: {', '.join(ctx.obj['selected_connectors_names'])}.", fg="green")
    connectors_contexts = [
        ConnectorContext(
            connector,
            ctx.obj["is_local"],
            ctx.obj["git_branch"],
            ctx.obj["git_revision"],
            ctx.obj["use_remote_secrets"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
        )
        for connector in ctx.obj["selected_connectors"]
    ]
    anyio.run(run_connectors_build_pipelines, connectors_contexts, ctx.obj["concurrency"])
    return True
