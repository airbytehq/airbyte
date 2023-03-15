#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import itertools
import logging
import os
import sys
from pathlib import Path
from typing import List, Tuple

import anyio
import asyncer
import click
import dagger
from ci_connector_ops.pipelines import checks, tests
from ci_connector_ops.pipelines.bases import ConnectorTestReport
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.github import update_commit_status_check
from ci_connector_ops.pipelines.utils import (
    DAGGER_CONFIG,
    get_current_epoch_time,
    get_current_git_branch,
    get_current_git_revision,
    get_modified_connectors,
    get_modified_files,
)
from ci_connector_ops.utils import ConnectorLanguage, get_all_released_connectors
from rich.logging import RichHandler

GITHUB_GLOBAL_CONTEXT = "[POC please ignore] Connectors CI"
GITHUB_GLOBAL_DESCRIPTION = "Running connectors tests"


logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])

logger = logging.getLogger(__name__)


async def run(context: ConnectorTestContext) -> ConnectorTestReport:
    """Runs a CI pipeline for a single connector.
    A visual DAG can be found on the README.md file of the pipelines modules.

    Args:
        context (ConnectorTestContext): The initialized connector test context.

    Returns:
        ConnectorTestReport: The test reports holding tests results.
    """
    async with context:
        async with asyncer.create_task_group() as task_group:
            tasks = [
                task_group.soonify(checks.QaChecks(context).run)(),
                task_group.soonify(checks.CodeFormatChecks(context).run)(),
                task_group.soonify(tests.run_all_tests)(context),
            ]
        results = list(itertools.chain(*(task.value for task in tasks)))

        context.test_report = ConnectorTestReport(context, steps_results=results)

    return context.test_report


async def run_connectors_test_pipelines(contexts: List[ConnectorTestContext]):
    """Runs a CI pipeline for all the connectors passed.

    Args:
        contexts (List[ConnectorTestContext]): List of connector test contexts for which a CI pipeline needs to be run.
    """
    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        async with anyio.create_task_group() as tg:
            for context in contexts:
                context.dagger_client = dagger_client.pipeline(f"{context.connector.technical_name} - Test Pipeline")
                tg.start_soon(run, context)


@click.group()
@click.option("--use-remote-secrets", default=True)
@click.option("--is-local/--is-ci", default=True)
@click.option("--git-branch", default=get_current_git_branch, envvar="CI_GIT_BRANCH")
@click.option("--git-revision", default=get_current_git_revision, envvar="CI_GIT_REVISION")
@click.option(
    "--diffed-branch",
    help="Branch to which the git diff will happen to detect new or modified connectors",
    default="origin/master",
    type=str,
)
@click.option("--gha-workflow-run-id", help="[CI Only] The run id of the GitHub action workflow", default=None, type=str)
@click.option("--ci-context", default="manual", envvar="CI_CONTEXT", type=click.Choice(["manual", "pull_request", "nightly_builds"]))
@click.option("--pipeline-start-timestamp", default=get_current_epoch_time, envvar="CI_PIPELINE_START_TIMESTAMP", type=int)
@click.pass_context
def connectors_ci(
    ctx: click.Context,
    use_remote_secrets: str,
    is_local: bool,
    git_branch: str,
    git_revision: str,
    diffed_branch: str,
    gha_workflow_run_id: str,
    ci_context: str,
    pipeline_start_timestamp: int,
):
    """A command group to gather all the connectors-ci command"""

    validate_environment(is_local, use_remote_secrets)

    ctx.ensure_object(dict)
    ctx.obj["use_remote_secrets"] = use_remote_secrets
    ctx.obj["is_local"] = is_local
    ctx.obj["git_branch"] = git_branch
    ctx.obj["git_revision"] = git_revision
    ctx.obj["gha_workflow_run_id"] = gha_workflow_run_id
    ctx.obj["gha_workflow_run_url"] = (
        f"https://github.com/airbytehq/airbyte/actions/runs/{gha_workflow_run_id}" if gha_workflow_run_id else None
    )
    ctx.obj["ci_context"] = ci_context
    ctx.obj["pipeline_start_timestamp"] = pipeline_start_timestamp
    update_commit_status_check(
        ctx.obj["git_revision"],
        "pending",
        ctx.obj["gha_workflow_run_url"],
        GITHUB_GLOBAL_DESCRIPTION,
        GITHUB_GLOBAL_CONTEXT,
        should_send=not ctx.obj["is_local"],
        logger=logger,
    )

    ctx.obj["modified_files"] = get_modified_files(git_branch, git_revision, diffed_branch, is_local)


@connectors_ci.command()
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
@click.pass_context
def test_connectors(ctx: click.Context, names: Tuple[str], languages: Tuple[ConnectorLanguage], release_stages: Tuple[str], modified: bool):
    """Runs a CI pipeline the connector passed as CLI argument.

    Args:
        ctx (click.Context): The click context.
        connector_name (str): The connector technical name. E.G. source-pokeapi
    """
    connectors_under_test = get_all_released_connectors()
    modified_connectors = get_modified_connectors(ctx.obj["modified_files"])
    if modified:
        connectors_under_test = modified_connectors
    else:
        connectors_under_test.update(modified_connectors)
    if names:
        connectors_under_test = {connector for connector in connectors_under_test if connector.technical_name in names}
    if languages:
        connectors_under_test = {connector for connector in connectors_under_test if connector.language in languages}
    if release_stages:
        connectors_under_test = {connector for connector in connectors_under_test if connector.release_stage in release_stages}
    connectors_under_test_names = [c.technical_name for c in connectors_under_test]
    if connectors_under_test_names:
        click.secho(f"Will run the test pipeline for the following connectors: {', '.join(connectors_under_test_names)}.", fg="green")
        click.secho(
            "If you're running this command for the first time the Dagger engine image will be pulled, it can take a short minute..."
        )
    else:
        click.secho("No connector test will run according to your inputs.", fg="yellow")
        sys.exit(0)

    connectors_tests_contexts = [
        ConnectorTestContext(
            connector,
            ctx.obj["is_local"],
            ctx.obj["git_branch"],
            ctx.obj["git_revision"],
            ctx.obj["use_remote_secrets"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
        )
        for connector in connectors_under_test
        if connector.language
        in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]  # TODO: remove this once we implement pipelines for Java connector
    ]
    try:
        anyio.run(run_connectors_test_pipelines, connectors_tests_contexts)
        update_commit_status_check(
            ctx.obj["git_revision"],
            "success",
            ctx.obj["gha_workflow_run_url"],
            GITHUB_GLOBAL_DESCRIPTION,
            GITHUB_GLOBAL_CONTEXT,
            should_send=not ctx.obj["is_local"],
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
            should_send=not ctx.obj["is_local"],
            logger=logger,
        )


def validate_environment(is_local: bool, use_remote_secrets: bool):

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


if __name__ == "__main__":
    connectors_ci()
