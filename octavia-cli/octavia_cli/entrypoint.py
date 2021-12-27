#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import click

import openapi_client
from .list import commands as list_commands

@click.group()
@click.option("--airbyte-url", envvar="AIRBYTE_URL", default="http://localhost:8000", help="The URL of your Airbyte instance.")
@click.pass_context
def octavia(ctx, airbyte_url):
    ctx.ensure_object(dict)
    client_configuration = openapi_client.Configuration(host=f"{airbyte_url}/api")
    ctx.obj["API_CLIENT"] = openapi_client.ApiClient(client_configuration)
    click.secho(f"🐙 - Octavia is targetting your Airbyte instance running at {airbyte_url}")

octavia.add_command(list_commands._list)


@octavia.command(help="Scaffolds a local project directories.")
def init():
    raise click.ClickException("The init command is not yet implemented.")

@octavia.command(name="import", help="Import an existing resources from the Airbyte instance.")
def _import():
    raise click.ClickException("The init command is not yet implemented.")


@octavia.command(help="Generate a YAML configuration file to manage a resource.")
def create():
    raise click.ClickException("The init command is not yet implemented.")


@octavia.command(help="Create or update resources according to YAML configurations.")
def apply():
    raise click.ClickException("The init command is not yet implemented.")


@octavia.command(help="Delete resources")
def delete():
    raise click.ClickException("The init command is not yet implemented.")

if __name__ == '__main__':
    octavia()