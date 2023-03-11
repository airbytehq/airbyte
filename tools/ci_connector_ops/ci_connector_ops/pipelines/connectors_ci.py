#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List, Tuple

import anyio
import click
import dagger
from ci_connector_ops.pipelines.actions import environments, tests
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.github import update_commit_status_check
from ci_connector_ops.pipelines.models import ConnectorTestReport, Step, StepResult, StepStatus
from ci_connector_ops.pipelines.utils import (
    DAGGER_CONFIG,
    get_current_git_branch,
    get_current_git_revision,
    get_modified_connectors,
    get_modified_files,
)
from ci_connector_ops.utils import ConnectorLanguage, get_all_released_connectors
from rich.logging import RichHandler

GITHUB_GLOBAL_CONTEXT = "[POC please ignore] Connectors CI"
GITHUB_GLOBAL_DESCRIPTION = "Running connectors tests"
REQUIRED_ENV_VARS_FOR_CI = [
    "GCP_GSM_CREDENTIALS",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
    "TEST_REPORTS_BUCKET_NAME",
    "CI_GITHUB_ACCESS_TOKEN",
]

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])

logger = logging.getLogger(__name__)


async def run(test_context: ConnectorTestContext) -> ConnectorTestReport:
    """Runs a CI pipeline for a single connector.
    A visual DAG can be found on the README.md file of the pipelines modules.

    Args:
        test_context (ConnectorTestContext): The initialized test context.

    Returns:
        ConnectorTestReport: The test reports holding tests results.
    """
    async with test_context:
        qa_checks_results = await tests.run_qa_checks(test_context)
        connector_source_code = await environments.with_airbyte_connector(test_context, install=False)
        connector_under_test = await environments.with_airbyte_connector(test_context)

        code_format_checks_results_future = asyncio.create_task(tests.code_format_checks(connector_source_code))
        unit_tests_results, connector_under_test_exit_code = await asyncio.gather(
            tests.run_unit_tests(connector_under_test), connector_under_test.exit_code()
        )

        package_install_result = StepResult(Step.PACKAGE_INSTALL, StepStatus.from_exit_code(connector_under_test_exit_code))

        if unit_tests_results.status is StepStatus.SUCCESS:
            integration_test_future = asyncio.create_task(tests.run_integration_tests(connector_under_test))
            acceptance_tests_results, test_context.updated_secrets_dir = await tests.run_acceptance_tests(
                test_context,
            )
            integration_tests_result = await integration_test_future

        else:
            integration_tests_result = StepResult(Step.INTEGRATION_TESTS, StepStatus.SKIPPED, stdout="Skipped because unit tests failed")
            acceptance_tests_results = StepResult(Step.ACCEPTANCE_TESTS, StepStatus.SKIPPED, stdout="Skipped because unit tests failed")

        test_context.test_report = ConnectorTestReport(
            test_context,
            steps_results=[
                package_install_result,
                await code_format_checks_results_future,
                unit_tests_results,
                integration_tests_result,
                acceptance_tests_results,
                qa_checks_results,
            ],
        )

    return test_context.test_report


async def run_connectors_test_pipelines(test_contexts: List[ConnectorTestContext]):
    """Runs a CI pipeline for all the connectors passed.

    Args:
        test_contexts (List[ConnectorTestContext]): List of connector test contexts for which a CI pipeline needs to be run.
    """
    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        async with anyio.create_task_group() as tg:
            for test_context in test_contexts:
                test_context.dagger_client = dagger_client.pipeline(f"{test_context.connector.technical_name} - Test Pipeline")
                tg.start_soon(run, test_context)


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
@click.pass_context
def connectors_ci(
    ctx: click.Context,
    use_remote_secrets: str,
    is_local: bool,
    git_branch: str,
    git_revision: str,
    diffed_branch: str,
    gha_workflow_run_id: str,
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
        for required_env_var in REQUIRED_ENV_VARS_FOR_CI:
            if os.getenv(required_env_var) is None:
                raise click.UsageError(f"When running in a CI context a {required_env_var} environment variable must be set.")
    if use_remote_secrets and os.getenv("GCP_GSM_CREDENTIALS") is None:
        raise click.UsageError(
            "You have to set the GCP_GSM_CREDENTIALS if you want to download secrets from GSM. Set the --use-remote-secrets option to false otherwise."
        )


if __name__ == "__main__":
    connectors_ci()
