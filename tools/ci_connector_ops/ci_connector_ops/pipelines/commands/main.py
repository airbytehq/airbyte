#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import click
from .metadata_service import metadata_service

@click.group(help="Airbyte CI top-level command group.")
@click.pass_context
def airbyte_ci(ctx):
    pass

@airbyte_ci.group(help="Commands related to connectors and connector acceptance tests.")
@click.pass_context
def connectors(ctx):
    pass

@connectors.command(help="Run CAT for a specific connector.")
@click.pass_context
def test_connectors(ctx):
    raise NotImplementedError("test_connector not implemented yet")

airbyte_ci.add_command(metadata_service)

if __name__ == '__main__':
    airbyte_ci()

