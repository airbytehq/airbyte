#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import sys
from pathlib import Path

import anyio
import click
import dagger
from ci_connector_ops.ci.actions.connector_tests import unit_tests, integration_tests, acceptance_tests
from ci_connector_ops.ci.actions.connector_builder import get_connector_builder
from ci_connector_ops.ci.actions.format_checks import check_format
from ci_connector_ops.ci.actions.build import install_requirements, build_image
from graphql import GraphQLError


async def run_tests(connector_name):
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        connector_builder = get_connector_builder(client, connector_name)
        await check_format(connector_builder)
        successful_install, connector_builder = await install_requirements(client, connector_builder, ["dev", "tests", "main"])
        
        if successful_install == 0:
            await unit_tests(connector_builder)
            await integration_tests(connector_builder)
            await build_image(client, connector_name)
            cat_output = await acceptance_tests(client, connector_name)
            print(cat_output)
        # print(install_requirements_output)


@click.command()
@click.argument("connector_name")
def main(connector_name):
    try:
        anyio.run(run_tests, connector_name)
    except GraphQLError as e:
        print(e.message, file=sys.stderr)
        sys.exit(1)
