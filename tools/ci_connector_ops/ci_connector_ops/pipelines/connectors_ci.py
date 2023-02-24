#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
import sys
from typing import List

import anyio
import click
import dagger
from ci_connector_ops.ci.actions import build_contexts, connector_builds, tests
from ci_connector_ops.utils import Connector, get_changed_connectors
from dagger.api.gen import Container, Pipeline
from graphql import GraphQLError


async def run_pipeline(connectors: List[Connector]):

    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as main_client:
        for connector in connectors:
            connector_ci: Pipeline = main_client.Pipeline(f"{connector.technical_name} CI")
            build_context: Container = build_contexts.python_connectors.get_build_context(connector_ci, connector)
            format_check_exit_code: int = tests.python_connectors.check_format(build_context)

            installed_connector: Container = connector_builds.python_connectors.install(connector_ci, build_context)

            unit_tests_exit_code: int = tests.python_connectors.run_unit_tests(installed_connector)
            integration_tests_exit_code: int = tests.python_connectors.run_integration_tests(installed_connector)

            print(f"Format: {format_check_exit_code}")
            print(f"Unit tests: {unit_tests_exit_code}")
            print(f"Integration tests: {integration_tests_exit_code}")


@click.command()
@click.option("--diffed-branch", default="master")
def main(diffed_branch):
    try:
        os.environ["DIFFED_BRANCH"] = diffed_branch
        changed_connectors = get_changed_connectors()
        anyio.run(changed_connectors)
    except GraphQLError as e:
        print(e.message, file=sys.stderr)
        sys.exit(1)
