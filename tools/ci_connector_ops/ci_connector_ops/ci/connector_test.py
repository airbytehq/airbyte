#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import sys

import anyio
import click
import dagger
from ci_connector_ops.ci.actions.connector_builder import get_connector_builder
from ci_connector_ops.ci.actions.format_checks import check_format
from ci_connector_ops.ci.actions.install_requirements import install_requirements
from graphql import GraphQLError


async def run_tests(connector_name):
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        connector_builder = get_connector_builder(client, connector_name)
        format_output = await check_format(client, connector_builder)
        install_requirements_output = await install_requirements(client, connector_builder, ["dev", "tests", "main"])
        print(format_output)
        print(install_requirements_output)


@click.command()
@click.argument("connector_name")
def main(connector_name):
    try:
        anyio.run(run_tests, connector_name)
    except GraphQLError as e:
        print(e.message, file=sys.stderr)
        sys.exit(1)
