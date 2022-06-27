#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import List, Type, Union

import airbyte_api_client
import click
from octavia_cli.base_commands import OctaviaCommand
from octavia_cli.generate import definitions
from octavia_cli.generate.renderers import ConnectorSpecificationRenderer
from octavia_cli.get.commands import get_json_representation
from octavia_cli.get.resources import Destination, Source

COMMON_HELP_MESSAGE_PREFIX = "Import a JSON representation of a remote"


def build_help_message(resource_type: str) -> str:
    """Helper function to build help message consistently for all the commands in this module.
    Args:
        resource_type (str): source, destination or connection
    Returns:
        str: The generated help message.
    """
    return f"Import a JSON representation of a remote {resource_type}."


def import_resource(
    api_client: airbyte_api_client.ApiClient,
    workspace_id: str,
    ResourceCls: Type[Union[Source, Destination]],
    resource_to_get: str,
) -> str:
    """Helper function to retrieve a resource json representation and avoid repeating the same logic for Source/Destination and connection.
    Args:
        api_client (airbyte_api_client.ApiClient): The Airbyte API client.
        workspace_id (str): Current workspace id.
        ResourceCls (Type[Union[Source, Destination]]): Resource class to use
        resource_to_get (str): resource name or id to get JSON representation for.
    Returns:
        str: The resource's JSON representation.
    """
    config = json.loads(get_json_representation(api_client, workspace_id, ResourceCls, resource_to_get))

    resource_type = ResourceCls.__name__.lower()

    definition = definitions.factory(resource_type, api_client, workspace_id, config[f"{resource_type}_definition_id"])

    renderer = ConnectorSpecificationRenderer(config["name"], definition)

    output_path = renderer.import_configuration(project_path=".", configuration=config["connection_configuration"])
    message = f"✅ - Imported {resource_type} in {output_path}."
    click.echo(click.style(message, fg="green"))


@click.group(
    "import",
    help=f'{build_help_message("source, destination or connection")} ID or name can be used as argument. Example: \'octavia import source "My Pokemon source"\' or \'octavia import source cb5413b2-4159-46a2-910a-dc282a439d2d\'',
)
@click.pass_context
def _import(ctx: click.Context):  # pragma: no cover
    pass


@_import.command(cls=OctaviaCommand, name="source", help=build_help_message("source"))
@click.argument("resource", type=click.STRING)
@click.pass_context
def source(ctx: click.Context, resource: str):
    click.echo(import_resource(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], Source, resource))


@_import.command(cls=OctaviaCommand, name="destination", help=build_help_message("destination"))
@click.argument("resource", type=click.STRING)
@click.pass_context
def destination(ctx: click.Context, resource: str):
    click.echo(import_resource(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], Destination, resource))


@_import.command(cls=OctaviaCommand, name="connection", help=build_help_message("connection"))
@click.argument("resource", type=click.STRING)
@click.pass_context
def connection(ctx: click.Context, resource: str):
    pass


AVAILABLE_COMMANDS: List[click.Command] = [source, destination, connection]


def add_commands_to_list():
    for command in AVAILABLE_COMMANDS:
        _import.add_command(command)


add_commands_to_list()
