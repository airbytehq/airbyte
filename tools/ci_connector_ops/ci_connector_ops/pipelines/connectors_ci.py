#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import os
import sys
from pathlib import Path
from typing import List

import anyio
import click
import dagger
from ci_connector_ops.pipelines.actions import builds, environments, secrets, tests
from ci_connector_ops.pipelines.utils import StepStatus
from ci_connector_ops.utils import Connector, ConnectorLanguage, get_changed_connectors
from dagger import Client, Container

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_connector_test_pipelines(dagger_client: Client, connector: Connector, use_gsm_secrets: bool):
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
    main_pipeline_name = f"CI test for {connector.technical_name}"
    pipeline_logger = logging.getLogger(main_pipeline_name)
    connector_ci_client: Client = dagger_client.pipeline(main_pipeline_name)
    connector_client = connector_ci_client.pipeline(f"{connector.technical_name} - Install connector python package")
    connector_under_test: Container = await environments.with_airbyte_connector(connector_client, connector)

    format_check_container: Container = connector_under_test.pipeline(f"{connector.technical_name} - Format Check")
    format_check_status: StepStatus = await tests.check_format(format_check_container)

    unit_test_container: Container = connector_under_test.pipeline(f"{connector.technical_name} - Unit tests")
    unit_tests_status: StepStatus = await tests.run_unit_tests(unit_test_container)

    integration_test_container: Container = connector_under_test.pipeline(f"{connector.technical_name} - Integration tests")
    integration_tests_status: StepStatus = await tests.run_integration_tests(integration_test_container)

    build_dev_image_client = connector_ci_client.pipeline(f"{connector.technical_name} - Build dev image")
    _, connector_image_short_id = await builds.build_dev_image(build_dev_image_client, connector, exclude=[".venv"])

    if not connector.acceptance_test_config:
        acceptance_tests_status = StepStatus.SKIPPED
    else:
        if use_gsm_secrets:
            download_credentials_client = connector_ci_client.pipeline(f"{connector.technical_name} - Download credentials")
            secrets_dir = await secrets.download(download_credentials_client, connector)
            await secrets_dir.export(str(connector.code_directory) + "/secrets")  # TODO remove
        else:
            secrets_dir = connector_ci_client.host().directory(str(connector.code_directory) + "/secrets")

        acceptance_tests_container: Container = build_dev_image_client.pipeline(f"{connector.technical_name} - Acceptance tests")
        # The connector_image_short_id  is used as a cache buster. If it changed the acceptance tests will run.
        connector_source_host_dir = dagger_client.host().directory(str(connector.code_directory), exclude=[".venv", "secrets"])

        acceptance_tests_status, updated_secrets_dir = await tests.run_acceptance_tests(
            acceptance_tests_container,
            connector_source_host_dir,
            secrets_dir,
            connector_image_short_id,
            "airbyte/connector-acceptance-test:dev",
        )

        if use_gsm_secrets and updated_secrets_dir:
            upload_credentials_client = connector_ci_client.pipeline(f"{connector.technical_name} - Upload credentials")
            await secrets.upload(upload_credentials_client, connector, updated_secrets_dir)

    # TODO run QA checks: this should probably be done inside a dagger container to benefit from caching?
    pipeline_logger.info(f"Format -> {format_check_status}")
    pipeline_logger.info(f"Unit tests -> {unit_tests_status}")
    pipeline_logger.info(f"Integration tests -> {integration_tests_status}")
    pipeline_logger.info(f"Acceptance tests -> {acceptance_tests_status}")


async def run_connectors_test_pipelines(connectors: List[Connector], gsm_credentials: str):
    """Runs a CI pipeline for all the connectors passed.

    Args:
        connectors (List[Connector]): List of connectors for which a CI pipeline needs to be run.
        gsm_credentials (str): The GSM credentials to read/write connectors' secrets.
    """
    config = dagger.Config(log_output=sys.stderr)

    async with dagger.Connection(config) as dagger_client:
        async with anyio.create_task_group() as tg:
            for connector in connectors:
                # We scoped this POC only for python and low-code connectors
                if connector.language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
                    tg.start_soon(run_connector_test_pipelines, dagger_client, connector, gsm_credentials)
                else:
                    logger.warning(f"Not running test pipeline for {connector.technical_name} as it's not a Python or Low code connector")


@click.group()
@click.option("--diffed-branch", default="master")
@click.option("--use-gsm-secrets", default=True)
@click.pass_context
def connectors_ci(ctx: click.Context, diffed_branch: str, use_gsm_secrets: str):
    """A command group to gather all the connectors-ci command

    Args:
        ctx (click.Context): The click context.
        diffed_branch (str): The branch used to compare code changes with current branch.
        gsm_credentials (str): The GSM credentials to read/write connectors' secrets.

    Raises:
        click.ClickException: _description_
    """
    if not (os.getcwd().endswith("/airbyte") and Path(".git").is_dir()):
        raise click.ClickException("You need to run this command from the airbyte repository root.")
    os.environ["DIFFED_BRANCH"] = diffed_branch
    ctx.ensure_object(dict)
    if use_gsm_secrets and os.getenv("GCP_GSM_CREDENTIALS") is None:
        raise click.UsageError(
            "You have to set the GCP_GSM_CREDENTIALS if you want to download secrets from GSM. Set the --use-gsm-secrets option to false otherwise."
        )
    ctx.obj["use_gsm_secrets"] = use_gsm_secrets


@connectors_ci.command()
@click.argument("connector_name", nargs=-1)
@click.pass_context
def test_connectors(ctx: click.Context, connector_name: str):
    """Runs a CI pipeline the connector passed as CLI argument.

    Args:
        ctx (click.Context): The click context.
        connector_name (str): The connector technical name. E.G. source-pokeapi
    """
    connectors = [Connector(cn) for cn in connector_name]
    try:
        anyio.run(run_connectors_test_pipelines, connectors, ctx.obj["use_gsm_secrets"])
    except dagger.DaggerError as e:
        logger.error(str(e))
        sys.exit(1)


@connectors_ci.command()
@click.pass_context
def test_all_modified_connectors(ctx: click.Context):
    """Launches a CI pipeline for all the connectors that got modified compared to the DIFFED_BRANCH environment variable.

    Args:
        ctx (click.Context): The click context.
    """
    changed_connectors = get_changed_connectors()
    if changed_connectors:
        try:
            anyio.run(run_connectors_test_pipelines, changed_connectors, ctx.obj["use_gsm_secrets"])
        except dagger.DaggerError as e:
            logger.error(str(e))
            sys.exit(1)
    else:
        logger.info(f"No connector modified after comparing the current branch with {os.environ['DIFFED_BRANCH']}")


if __name__ == "__main__":
    connectors_ci()
