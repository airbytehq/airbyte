#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import click


@click.group()
@click.option("--airbyte-url", envvar="AIRBYTE_URL", default="http://localhost:8000", help="The URL of your Airbyte instance.")
def octavia(airbyte_url):
    # TODO: check if the airbyte_url is reachable
    click.secho(f"🐙 - Octavia is targetting your Airbyte instance running at {airbyte_url}")


@octavia.command(help="Scaffolds a local project directories.")
def init():
    raise click.ClickException("The init command is not yet implemented.")


@octavia.command(name="list", help="List existing resources on the Airbyte instance.")
def _list():
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
