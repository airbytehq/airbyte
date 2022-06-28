#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional, Tuple

import airbyte_api_client
import click
import pkg_resources
from airbyte_api_client.api import workspace_api
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody

from .api_http_headers import ApiHttpHeader, merge_api_headers, set_api_headers_on_api_client
from .apply import commands as apply_commands
from .check_context import check_api_health, check_is_initialized, check_workspace_exists
from .generate import commands as generate_commands
from .get import commands as get_commands
from .init import commands as init_commands
from .list import commands as list_commands
from .telemetry import TelemetryClient, build_user_agent

AVAILABLE_COMMANDS: List[click.Command] = [
    list_commands._list,
    get_commands.get,
    init_commands.init,
    generate_commands.generate,
    apply_commands.apply,
]


def set_context_object(
    ctx: click.Context,
    airbyte_url: str,
    workspace_id: str,
    enable_telemetry: bool,
    option_based_api_http_headers: Optional[List[Tuple[str, str]]],
    api_http_headers_file_path: Optional[str],
) -> click.Context:
    """Fill the context object with resources that will be reused by other commands.
    Performs check and telemetry sending in case of error.

    Args:
        ctx (click.Context): Current command context.
        airbyte_url (str): The airbyte instance url.
        workspace_id (str): The user_defined workspace id.
        enable_telemetry (bool): Whether the telemetry should send data.
        option_based_api_http_headers (Optional[List[Tuple[str, str]]]): Option based headers.
        api_http_headers_file_path (Optional[str]): Path to the YAML file with http headers.

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
        user_agent = build_user_agent(ctx.obj["OCTAVIA_VERSION"])
        api_http_headers = merge_api_headers(option_based_api_http_headers, api_http_headers_file_path)
        api_client = get_api_client(airbyte_url, user_agent, api_http_headers)
        ctx.obj["WORKSPACE_ID"] = get_workspace_id(api_client, workspace_id)
        ctx.obj["ANONYMOUS_DATA_COLLECTION"] = get_anonymous_data_collection(api_client, ctx.obj["WORKSPACE_ID"])
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
    type=bool,
)
@click.option(
    "--api-http-header",
    "-ah",
    "option_based_api_http_headers",
    help='Additional HTTP header name and header value pairs to pass to use when calling Airbyte\'s API ex. --api-http-header "Authorization" "Basic dXNlcjpwYXNzd29yZA=="',
    multiple=True,
    nargs=2,
    type=click.Tuple([str, str]),
)
@click.option(
    "--api-http-headers-file-path",
    help=f"Path to the Yaml file with API HTTP headers. Please check the {init_commands.API_HTTP_HEADERS_TARGET_PATH} file.",
    type=click.Path(exists=True, readable=True),
)
@click.pass_context
def octavia(
    ctx: click.Context,
    airbyte_url: str,
    workspace_id: str,
    enable_telemetry: bool,
    option_based_api_http_headers: Optional[List[Tuple[str, str]]] = None,
    api_http_headers_file_path: Optional[str] = None,
) -> None:

    ctx = set_context_object(ctx, airbyte_url, workspace_id, enable_telemetry, option_based_api_http_headers, api_http_headers_file_path)

    click.echo(
        click.style(
            f"🐙 - Octavia is targetting your Airbyte instance running at {airbyte_url} on workspace {ctx.obj['WORKSPACE_ID']}.", fg="green"
        )
    )
    if not ctx.obj["PROJECT_IS_INITIALIZED"]:
        click.echo(click.style("🐙 - Project is not yet initialized.", fg="red", bold=True))


def get_api_client(airbyte_url: str, user_agent: str, api_http_headers: Optional[List[ApiHttpHeader]]):
    client_configuration = airbyte_api_client.Configuration(host=f"{airbyte_url}/api")
    api_client = airbyte_api_client.ApiClient(client_configuration)
    api_client.user_agent = user_agent
    if api_http_headers:
        set_api_headers_on_api_client(api_client, api_http_headers)

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
    return api_response.get("anonymous_data_collection", True)


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
