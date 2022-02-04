#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

import airbyte_api_client
import click
from airbyte_api_client.api import workspace_api

from .check_context import check_api_health, check_is_initialized, check_workspace_exists
from .init import commands as init_commands
from .list import commands as list_commands

AVAILABLE_COMMANDS: List[click.Command] = [list_commands._list, init_commands.init]


@click.group()
@click.option("--airbyte-url", envvar="AIRBYTE_URL", default="http://localhost:8000", help="The URL of your Airbyte instance.")
@click.option(
    "--workspace-id",
    envvar="AIRBYTE_WORKSPACE_ID",
    default=None,
    help="The id of the workspace on which you want octavia-cli to work. Defaults to the first one found on your Airbyte instance.",
)
@click.pass_context
def octavia(ctx: click.Context, airbyte_url: str, workspace_id: str) -> None:
    ctx.ensure_object(dict)
    ctx.obj["API_CLIENT"] = get_api_client(airbyte_url)
    ctx.obj["WORKSPACE_ID"] = get_workspace_id(ctx.obj["API_CLIENT"], workspace_id)
    ctx.obj["PROJECT_IS_INITIALIZED"] = check_is_initialized()
    click.echo(
        click.style(
            f"🐙 - Octavia is targetting your Airbyte instance running at {airbyte_url} on workspace {ctx.obj['WORKSPACE_ID']}.", fg="green"
        )
    )
    if not ctx.obj["PROJECT_IS_INITIALIZED"]:
        click.echo(click.style("🐙 - Project is not yet initialized.", fg="red", bold=True))


def get_api_client(airbyte_url):
    client_configuration = airbyte_api_client.Configuration(host=f"{airbyte_url}/api")
    api_client = airbyte_api_client.ApiClient(client_configuration)
    check_api_health(api_client)
    return api_client


def get_workspace_id(api_client, user_defined_workspace_id):
    if user_defined_workspace_id:
        check_workspace_exists(api_client, user_defined_workspace_id)
        return user_defined_workspace_id
    else:
        api_instance = workspace_api.WorkspaceApi(api_client)
        api_response = api_instance.list_workspaces(_check_return_type=False)
        return api_response.workspaces[0]["workspaceId"]


def add_commands_to_octavia():
    for command in AVAILABLE_COMMANDS:
        octavia.add_command(command)


@octavia.command(name="import", help="Import an existing resources from the Airbyte instance.")
def _import() -> None:
    raise click.ClickException("The import command is not yet implemented.")


@octavia.command(help="Generate a YAML configuration file to manage a resource.")
def create() -> None:
    raise click.ClickException("The create command is not yet implemented.")


@octavia.command(help="Create or update resources according to YAML configurations.")
def apply() -> None:
    raise click.ClickException("The apply command is not yet implemented.")


@octavia.command(help="Delete resources")
def delete() -> None:
    raise click.ClickException("The delete command is not yet implemented.")


add_commands_to_octavia()
