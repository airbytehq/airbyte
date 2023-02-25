#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
import sys
from typing import List

import anyio
import click
import dagger
from ci_connector_ops.pipelines.actions import build_contexts, builds, tests
from ci_connector_ops.pipelines.utils import StepStatus
from ci_connector_ops.utils import Connector, get_changed_connectors
from dagger.api.gen import Client, Container
from graphql import GraphQLError


async def run_connector_test_pipelines(dagger_client: Client, connector: Connector):
    connector_ci: Client = dagger_client.pipeline(f"{connector.technical_name} CI")
    build_context: Container = build_contexts.get_build_context(connector_ci.pipeline("Build context"), connector)
    format_check_status: StepStatus = await tests.check_format(build_context.pipeline("Format Check"))

    installed_connector: Container = await builds.install(connector_ci, build_context.pipeline("Install connector"))

    unit_tests_status: StepStatus = await tests.run_unit_tests(installed_connector.pipeline("Unit tests"))
    integration_tests_status: StepStatus = await tests.run_integration_tests(installed_connector.pipeline("Integration tests"))
    acceptance_tests_status: StepStatus = await tests.run_acceptance_tests(dagger_client.pipeline("Acceptance tests"), connector, "dev")

    print(f"Format: {format_check_status}")
    print(f"Unit tests: {unit_tests_status}")
    print(f"Integration tests: {integration_tests_status}")
    print(f"Acceptance tests: {acceptance_tests_status}")


async def run_connectors_test_pipelines(connectors: List[Connector]):
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as dagger_client:
        for connector in connectors:
            await run_connector_test_pipelines(dagger_client, connector)


@click.group()
@click.option("--diffed-branch", default="master")
def connectors_ci(diffed_branch):
    os.environ["DIFFED_BRANCH"] = diffed_branch


@connectors_ci.command()
@click.argument("connector_name")
def test_connector(connector_name):
    connector = Connector(connector_name)
    try:
        anyio.run(run_connectors_test_pipelines, [connector])
    except GraphQLError as e:
        print(e.message, file=sys.stderr)
        sys.exit(1)


@connectors_ci.command()
def test_all_modified_connector():
    changed_connectors = get_changed_connectors()
    if changed_connectors:
        try:
            anyio.run(run_connectors_test_pipelines, changed_connectors)
        except GraphQLError as e:
            print(e.message, file=sys.stderr)
            sys.exit(1)
    else:
        click.echo(f"No connector modified after comparing the current branch with {os.environ['DIFFED_BRANCH']}")
