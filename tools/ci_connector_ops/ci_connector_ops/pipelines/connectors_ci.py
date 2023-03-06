#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List

import anyio
import click
import dagger
from ci_connector_ops.pipelines.actions import builds, environments, remote_storage, secrets, tests
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.models import ConnectorTestReport, Step, StepResult, StepStatus
from ci_connector_ops.pipelines.utils import get_current_git_branch, get_current_git_revision
from ci_connector_ops.utils import Connector, ConnectorLanguage, get_changed_connectors_between_branches

REQUIRED_ENV_VARS_FOR_CI = ["GCP_GSM_CREDENTIALS", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION", "TEST_REPORTS_BUCKET_NAME"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup(test_context: ConnectorTestContext) -> ConnectorTestContext:
    main_pipeline_name = f"CI test for {test_context.connector.technical_name}"
    test_context.logger = logging.getLogger(main_pipeline_name)
    test_context.secrets_dir = await secrets.get_connector_secret_dir(test_context)
    test_context.updated_secrets_dir = None
    return test_context


async def teardown(test_context: ConnectorTestContext, test_report: ConnectorTestReport) -> ConnectorTestContext:
    teardown_pipeline = test_context.dagger_client.pipeline(f"Teardown {test_context.connector.technical_name}")
    if test_context.should_save_updated_secrets:
        await secrets.upload(
            teardown_pipeline,
            test_context.connector,
            test_context.updated_secrets_dir,
        )

    test_context.logger.info(str(test_report))
    local_test_reports_path_root = "tools/ci_connector_ops/test_reports/"

    connector_name = test_report.connector_test_context.connector.technical_name
    connector_version = test_report.connector_test_context.connector.version
    git_revision = test_report.connector_test_context.git_revision
    git_branch = test_report.connector_test_context.git_branch.replace("/", "_")
    suffix = f"{connector_name}/{git_branch}/{connector_version}/{git_revision}.json"
    local_report_path = Path(local_test_reports_path_root + suffix)
    local_report_path.parents[0].mkdir(parents=True, exist_ok=True)
    local_report_path.write_text(test_report.to_json())
    if test_report.should_be_saved:
        s3_reports_path_root = "python-poc/tests/history/"
        s3_key = s3_reports_path_root + suffix
        await remote_storage.upload_to_s3(teardown_pipeline, str(local_report_path), s3_key, os.environ["TEST_REPORTS_BUCKET_NAME"])
    return test_context


async def run(test_context: ConnectorTestContext) -> ConnectorTestReport:
    """Runs a CI pipeline for a single connector.
    1. Create a build context
    2. Check code format
    3. Install connector
    4. Run unit tests
    5. Run integration tests
    6. Download and write connector secret to local storage.
    7. Run acceptance tests

    Args:
        dagger_client (Client): The dagger client to use.
        connector (Connector): The connector under test.
        gsm_credentials (str): The GSM credentials to read/write connector's secrets.
    """

    test_context = await setup(test_context)
    connector_source_code = await environments.with_airbyte_connector(test_context, install=False)
    connector_under_test = await environments.with_airbyte_connector(test_context)

    format_check_results, unit_tests_results, connector_under_test_exit_code, qa_checks_results = await asyncio.gather(
        tests.check_format(connector_source_code),
        tests.run_unit_tests(connector_under_test),
        connector_under_test.exit_code(),
        tests.run_qa_checks(test_context),
    )

    package_install_result = StepResult(Step.PACKAGE_INSTALL, StepStatus.from_exit_code(connector_under_test_exit_code))

    if unit_tests_results.status is StepStatus.SUCCESS:
        integration_test_future = asyncio.create_task(tests.run_integration_tests(connector_under_test))
        docker_build_future = asyncio.create_task(builds.build_dev_image(test_context, exclude=[".venv"]))

        _, connector_image_short_id = await docker_build_future

        docker_build_result = StepResult(Step.DOCKER_BUILD, StepStatus.SUCCESS)
        acceptance_tests_results, test_context.updated_secrets_dir = await tests.run_acceptance_tests(
            test_context,
            connector_image_short_id,
        )

        integration_tests_result = await integration_test_future

    else:
        integration_tests_result = StepResult(Step.INTEGRATION_TESTS, StepStatus.SKIPPED, stdout="Skipped because unit tests failed")
        docker_build_result = StepResult(Step.DOCKER_BUILD, StepStatus.SKIPPED, stdout="Skipped because unit tests failed")
        acceptance_tests_results = StepResult(Step.ACCEPTANCE_TESTS, StepStatus.SKIPPED, stdout="Skipped because unit tests failed")

    test_report = ConnectorTestReport(
        test_context,
        steps_results=[
            package_install_result,
            format_check_results,
            unit_tests_results,
            integration_tests_result,
            docker_build_result,
            acceptance_tests_results,
            qa_checks_results,
        ],
    )

    await teardown(test_context, test_report)
    return test_report


async def run_connectors_test_pipelines(test_contexts: List[ConnectorTestContext]):
    """Runs a CI pipeline for all the connectors passed.

    Args:
        connectors (List[Connector]): List of connectors for which a CI pipeline needs to be run.
        gsm_credentials (str): The GSM credentials to read/write connectors' secrets.
    """
    config = dagger.Config(log_output=sys.stderr)

    async with dagger.Connection(config) as dagger_client:
        async with anyio.create_task_group() as tg:
            for test_context in test_contexts:
                # We scoped this POC only for python and low-code connectors
                if test_context.connector.language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
                    test_context.dagger_client = dagger_client.pipeline(f"{test_context.connector.technical_name} - Test Pipeline")
                    tg.start_soon(run, test_context)
                else:
                    logger.warning(
                        f"Not running test pipeline for {test_context.connector.technical_name} as it's not a Python or Low code connector"
                    )


# TODO update docstring
@click.group()
@click.option("--use-remote-secrets", default=True)
@click.option("--is-local", default=True)
@click.option("--git-branch", default=lambda: get_current_git_branch(), envvar="CI_GIT_BRANCH")
@click.option("--git-revision", default=lambda: get_current_git_revision(), envvar="CI_GIT_REVISION")
@click.pass_context
def connectors_ci(ctx: click.Context, use_remote_secrets: str, is_local: bool, git_branch: str, git_revision: str):
    """A command group to gather all the connectors-ci command"""
    if not (os.getcwd().endswith("/airbyte") and Path(".git").is_dir()):
        raise click.ClickException("You need to run this command from the airbyte repository root.")
    ctx.ensure_object(dict)
    if use_remote_secrets and os.getenv("GCP_GSM_CREDENTIALS") is None:
        raise click.UsageError(
            "You have to set the GCP_GSM_CREDENTIALS if you want to download secrets from GSM. Set the --use-gsm-secrets option to false otherwise."
        )
    if not is_local:
        for required_env_var in REQUIRED_ENV_VARS_FOR_CI:
            if os.getenv(required_env_var) is None:
                raise click.UsageError(f"When running in a CI context a {required_env_var} environment variable must be set.")
    ctx.obj["use_remote_secrets"] = use_remote_secrets
    ctx.obj["is_local"] = is_local
    ctx.obj["git_branch"] = git_branch
    ctx.obj["git_revision"] = git_revision


@connectors_ci.command()
@click.argument("connector_name", nargs=-1)
@click.pass_context
def test_connectors(ctx: click.Context, connector_name: str):
    """Runs a CI pipeline the connector passed as CLI argument.

    Args:
        ctx (click.Context): The click context.
        connector_name (str): The connector technical name. E.G. source-pokeapi
    """
    connectors_tests_contexts = [ConnectorTestContext(Connector(cn), **ctx.obj) for cn in connector_name]
    try:
        anyio.run(run_connectors_test_pipelines, connectors_tests_contexts)
    except dagger.DaggerError as e:
        logger.error(str(e))
        sys.exit(1)


@connectors_ci.command()
@click.pass_context
@click.option("--diffed-branch", default="origin/master")
def test_all_modified_connectors(ctx: click.Context, diffed_branch: str):
    """Launches a CI pipeline for all the connectors that got modified compared to the DIFFED_BRANCH environment variable.

    Args:
        ctx (click.Context): The click context.
    """

    changed_connectors = get_changed_connectors_between_branches(ctx.obj["git_branch"], diffed_branch)
    connectors_tests_contexts = [ConnectorTestContext(connector, **ctx.obj) for connector in changed_connectors]
    if changed_connectors:
        try:
            anyio.run(run_connectors_test_pipelines, connectors_tests_contexts)
        except dagger.DaggerError as e:
            logger.error(str(e))
            sys.exit(1)
    else:
        logger.info(f"No connector modified after comparing the current branch with {os.environ['DIFFED_BRANCH']}")


if __name__ == "__main__":
    connectors_ci()
