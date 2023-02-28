#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

import anyio
import click
import dagger
from ci_connector_ops.pipelines.actions import build_contexts, builds, tests
from ci_connector_ops.pipelines.utils import StepStatus, write_connector_secrets_to_local_storage
from ci_connector_ops.utils import Connector, ConnectorLanguage, get_changed_connectors
from dagger import Client, Container

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_connector_test_pipelines(dagger_client: Client, connector: Connector, gsm_credentials: Optional[str]):
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
    build_context_client: Client = connector_ci_client.pipeline(f"{connector.technical_name} - Build context")
    build_context: Container = build_contexts.get_build_context(build_context_client, connector)
    format_check_container: Container = build_context.pipeline(f"{connector.technical_name} - Format Check")
    format_check_status: StepStatus = await tests.check_format(format_check_container)

    install_container: Container = build_context.pipeline(f"{connector.technical_name} - Install connector")
    installed_connector: Container = await builds.install(connector_ci_client, install_container, extras=["tests", "dev", "main"])

    unit_test_container: Container = installed_connector.pipeline(f"{connector.technical_name} - Unit tests")
    unit_tests_status: StepStatus = await tests.run_unit_tests(unit_test_container)

    integration_test_container: Container = installed_connector.pipeline(f"{connector.technical_name} - Integration tests")
    integration_tests_status: StepStatus = await tests.run_integration_tests(integration_test_container)

    build_dev_image_client = connector_ci_client.pipeline(f"{connector.technical_name} - Build dev image")
    _, connector_image_short_id = await builds.build_dev_image(build_dev_image_client, connector, exclude=[".venv"])

    if gsm_credentials:
        write_connector_secrets_to_local_storage(connector, gsm_credentials)

    acceptance_tests_container: Container = build_dev_image_client.pipeline(f"{connector.technical_name} - Acceptance tests")
    # The connector_image_short_id  is used as a cache buster. If it changed the acceptance tests will run.
    acceptance_tests_status: StepStatus = await tests.run_acceptance_tests(
        acceptance_tests_container, connector, connector_image_short_id, "airbyte/connector-acceptance-test:dev"
    )

    # TODO run QA checks: this should probably be done inside a dagger container to benefit from caching?
    # TODO Upload modified secrets to GSM
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
@click.option("--gcp-gsm-credentials", envvar="GCP_GSM_CREDENTIALS")
@click.pass_context
def connectors_ci(ctx: click.Context, diffed_branch: str, gcp_gsm_credentials: str):
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
    if not gcp_gsm_credentials:
        logger.warning("You did not set GCP_GSM_CREDENTIALS. Acceptances test on connector requiring secrets won't run as expected.")
        ctx.obj["gsm_credentials"] = None
    else:
        ctx.obj["gsm_credentials"] = json.loads(gcp_gsm_credentials)


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
        anyio.run(run_connectors_test_pipelines, connectors, ctx.obj["gsm_credentials"])
    except dagger.DaggerError as e:
        logger.error(e.message)
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
            anyio.run(run_connectors_test_pipelines, changed_connectors, ctx.obj["gsm_credentials"])
        except dagger.DaggerError as e:
            logger.error(e.message)
            sys.exit(1)
    else:
        logger.info(f"No connector modified after comparing the current branch with {os.environ['DIFFED_BRANCH']}")
