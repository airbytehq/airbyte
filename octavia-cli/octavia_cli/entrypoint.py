#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import airbyte_api_client
import click
from airbyte_api_client.api import workspace_api


@click.group()
@click.option("--airbyte-url", envvar="AIRBYTE_URL", default="http://localhost:8000", help="The URL of your Airbyte instance.")
@click.pass_context
def octavia(ctx: click.Context, airbyte_url: str) -> None:
    ctx.ensure_object(dict)
    client_configuration = airbyte_api_client.Configuration(host=f"{airbyte_url}/api")
    api_client = airbyte_api_client.ApiClient(client_configuration)
    # TODO alafanechere workspace check might deserve its own function
    api_instance = workspace_api.WorkspaceApi(api_client)
    api_response = api_instance.list_workspaces()
    # TODO alafanechere prompt user to chose a workspace if multiple workspaces exist
    workspace_id = api_response.workspaces[0].workspace_id
    click.echo(f"🐙 - Octavia is targetting your Airbyte instance running at {airbyte_url} on workspace {workspace_id}")
    ctx.obj["API_CLIENT"] = api_client
    ctx.obj["WORKSPACE_ID"] = workspace_id


@octavia.command(help="Scaffolds a local project directories.")
def init() -> None:
    raise click.ClickException("The init command is not yet implemented.")


@octavia.command(name="list", help="List existing resources on the Airbyte instance.")
def _list() -> None:
    raise click.ClickException("The init command is not yet implemented.")


@octavia.command(name="import", help="Import an existing resources from the Airbyte instance.")
def _import() -> None:
    raise click.ClickException("The init command is not yet implemented.")


@octavia.command(help="Generate a YAML configuration file to manage a resource.")
def create() -> None:
    raise click.ClickException("The init command is not yet implemented.")


@octavia.command(help="Create or update resources according to YAML configurations.")
def apply() -> None:
    raise click.ClickException("The init command is not yet implemented.")


@octavia.command(help="Delete resources")
def delete() -> None:
    raise click.ClickException("The init command is not yet implemented.")
