#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

import airbyte_api_client
import click
import pkg_resources
from airbyte_api_client.api import workspace_api
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody

from .apply import commands as apply_commands
from .check_context import check_api_health, check_is_initialized, check_workspace_exists
from .generate import commands as generate_commands
from .init import commands as init_commands
from .list import commands as list_commands
from .telemetry import TelemetryClient, build_user_agent

AVAILABLE_COMMANDS: List[click.Command] = [list_commands._list, init_commands.init, generate_commands.generate, apply_commands.apply]


def set_context_object(ctx: click.Context, airbyte_url: str, workspace_id: str, enable_telemetry: bool) -> click.Context:
    """Fill the context object with resources that will be reused by other commands.
    Performs check and telemetry sending in case of error.

    Args:
        ctx (click.Context): Current command context.
        airbyte_url (str): The airbyte instance url.
        workspace_id (str): The user_defined workspace id.
        enable_telemetry (bool): Whether the telemetry should send data.

    Raises:
        e: Raise whatever error that might happen during the execution.

    Returns:
        click.Context: The context with it's updated object.
    """
    telemetry_client = TelemetryClient(enable_telemetry)
    try:
        ctx.ensure_object(dict)
        ctx.obj["OCTAVIA_VERSION"] = pkg_resources.require("octavia-cli")[0].version
        ctx.obj["TELEMETRY_CLIENT"] = telemetry_client
        api_client = get_api_client(airbyte_url)
        ctx.obj["WORKSPACE_ID"] = get_workspace_id(api_client, workspace_id)
        ctx.obj["ANONYMOUS_DATA_COLLECTION"] = get_anonymous_data_collection(api_client, ctx.obj["WORKSPACE_ID"])
        api_client.user_agent = build_user_agent(ctx.obj["OCTAVIA_VERSION"])
        ctx.obj["API_CLIENT"] = api_client
        ctx.obj["PROJECT_IS_INITIALIZED"] = check_is_initialized()
    except Exception as e:
        telemetry_client.send_command_telemetry(ctx, error=e)
        raise e
    return ctx


@click.group()
@click.option("--airbyte-url", envvar="AIRBYTE_URL", default="http://localhost:8000", help="The URL of your Airbyte instance.")
@click.option(
    "--workspace-id",
    envvar="AIRBYTE_WORKSPACE_ID",
    default=None,
    help="The id of the workspace on which you want octavia-cli to work. Defaults to the first one found on your Airbyte instance.",
)
@click.option(
    "--enable-telemetry/--disable-telemetry",
    envvar="OCTAVIA_ENABLE_TELEMETRY",
    default=True,
    help="Enable or disable telemetry for product improvement.",
)
@click.pass_context
def octavia(ctx: click.Context, airbyte_url: str, workspace_id: str, enable_telemetry: bool) -> None:
    ctx = set_context_object(ctx, airbyte_url, workspace_id, enable_telemetry)
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


def get_anonymous_data_collection(api_client, workspace_id):
    api_instance = workspace_api.WorkspaceApi(api_client)
    api_response = api_instance.get_workspace(WorkspaceIdRequestBody(workspace_id), _check_return_type=False)
    return api_response.anonymous_data_collection


def add_commands_to_octavia():
    for command in AVAILABLE_COMMANDS:
        octavia.add_command(command)


@octavia.command(name="import", help="[NOT IMPLEMENTED]  Import an existing resources from the Airbyte instance.")
def _import() -> None:
    raise click.ClickException("The import command is not yet implemented.")


@octavia.command(help="[NOT IMPLEMENTED] Delete resources")
def delete() -> None:
    raise click.ClickException("The delete command is not yet implemented.")


add_commands_to_octavia()
