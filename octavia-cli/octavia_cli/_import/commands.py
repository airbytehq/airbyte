#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import List, Type, Union

import airbyte_api_client
import click
from octavia_cli.apply import resources
from octavia_cli.base_commands import OctaviaCommand
from octavia_cli.check_context import requires_init
from octavia_cli.generate import definitions, renderers
from octavia_cli.get.commands import get_json_representation
from octavia_cli.get.resources import Connection as UnmanagedConnection
from octavia_cli.get.resources import Destination as UnmanagedDestination
from octavia_cli.get.resources import Source as UnmanagedSource
from octavia_cli.list.listings import Connections as UnmanagedConnections
from octavia_cli.list.listings import Destinations as UnmanagedDestinations
from octavia_cli.list.listings import Sources as UnmanagedSources


class MissingResourceDependencyError(click.UsageError):
    pass


def build_help_message(resource_type: str) -> str:
    """Helper function to build help message consistently for all the commands in this module.
    Args:
        resource_type (str): source, destination or connection
    Returns:
        str: The generated help message.
    """
    return f"Import an existing {resource_type} to manage it with octavia-cli."


def import_source_or_destination(
    api_client: airbyte_api_client.ApiClient,
    workspace_id: str,
    ResourceClass: Type[Union[UnmanagedSource, UnmanagedDestination]],
    resource_to_get: str,
) -> str:
    """Helper function to import sources & destinations.

    Args:
        api_client (airbyte_api_client.ApiClient): the Airbyte API client.
        workspace_id (str): current Airbyte workspace id.
        ResourceClass (Union[UnmanagedSource, UnmanagedDestination]): the Airbyte Resource Class.
        resource_to_get (str): the name or ID of the resource in the current Airbyte workspace id.

    Returns:
        str: The generated import message.
    """
    remote_configuration = json.loads(get_json_representation(api_client, workspace_id, ResourceClass, resource_to_get))

    resource_type = ResourceClass.__name__.lower()

    definition = definitions.factory(resource_type, api_client, workspace_id, remote_configuration[f"{resource_type}_definition_id"])

    renderer = renderers.ConnectorSpecificationRenderer(remote_configuration["name"], definition)

    new_configuration_path = renderer.import_configuration(project_path=".", configuration=remote_configuration["connection_configuration"])
    managed_resource, state = resources.factory(api_client, workspace_id, new_configuration_path).manage(
        remote_configuration[f"{resource_type}_id"]
    )
    message = f"✅ - Imported {resource_type} {managed_resource.name} in {new_configuration_path}. State stored in {state.path}"
    click.echo(click.style(message, fg="green"))
    message = f"⚠️  - Please update any secrets stored in {new_configuration_path}"
    click.echo(click.style(message, fg="yellow"))


def import_connection(
    api_client: airbyte_api_client.ApiClient,
    workspace_id: str,
    resource_to_get: str,
) -> str:
    """Helper function to import connection.

    Args:
        api_client (airbyte_api_client.ApiClient): the Airbyte API client.
        workspace_id (str): current Airbyte workspace id.
        resource_to_get (str): the name or ID of the resource in the current Airbyte workspace id.

    Returns:
        str: The generated import message.
    """
    remote_configuration = json.loads(get_json_representation(api_client, workspace_id, UnmanagedConnection, resource_to_get))
    # Since #15253 "schedule" is deprecated
    remote_configuration.pop("schedule", None)
    source_name, destination_name = remote_configuration["source"]["name"], remote_configuration["destination"]["name"]
    source_configuration_path = renderers.ConnectorSpecificationRenderer.get_output_path(
        project_path=".", definition_type="source", resource_name=source_name
    )

    destination_configuration_path = renderers.ConnectorSpecificationRenderer.get_output_path(
        project_path=".", definition_type="destination", resource_name=destination_name
    )
    if not source_configuration_path.is_file():
        raise MissingResourceDependencyError(
            f"The source {source_name} is not managed by octavia-cli, please import and apply it before importing your connection."
        )
    elif not destination_configuration_path.is_file():
        raise MissingResourceDependencyError(
            f"The destination {destination_name} is not managed by octavia-cli, please import and apply it before importing your connection."
        )
    else:
        source = resources.factory(api_client, workspace_id, source_configuration_path)
        destination = resources.factory(api_client, workspace_id, destination_configuration_path)
        if not source.was_created:
            raise resources.NonExistingResourceError(
                f"The source defined at {source_configuration_path} does not exists. Please run octavia apply before creating this connection."
            )
        if not destination.was_created:
            raise resources.NonExistingResourceError(
                f"The destination defined at {destination_configuration_path} does not exists. Please run octavia apply before creating this connection."
            )

        connection_name, connection_id = remote_configuration["name"], remote_configuration["connection_id"]
        connection_renderer = renderers.ConnectionRenderer(connection_name, source, destination)
        new_configuration_path = connection_renderer.import_configuration(".", remote_configuration)
        managed_resource, state = resources.factory(api_client, workspace_id, new_configuration_path).manage(connection_id)
        message = f"✅ - Imported connection {managed_resource.name} in {new_configuration_path}. State stored in {state.path}"
        click.echo(click.style(message, fg="green"))


@click.group(
    "import",
    help=f'{build_help_message("source, destination or connection")}. ID or name can be used as argument. Example: \'octavia import source "My Pokemon source"\' or \'octavia import source cb5413b2-4159-46a2-910a-dc282a439d2d\'',
)
@click.pass_context
def _import(ctx: click.Context):  # pragma: no cover
    pass


@_import.command(cls=OctaviaCommand, name="source", help=build_help_message("source"))
@click.argument("resource", type=click.STRING)
@click.pass_context
@requires_init
def source(ctx: click.Context, resource: str):
    click.echo(import_source_or_destination(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], UnmanagedSource, resource))


@_import.command(cls=OctaviaCommand, name="destination", help=build_help_message("destination"))
@click.argument("resource", type=click.STRING)
@click.pass_context
@requires_init
def destination(ctx: click.Context, resource: str):
    click.echo(import_source_or_destination(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], UnmanagedDestination, resource))


@_import.command(cls=OctaviaCommand, name="connection", help=build_help_message("connection"))
@click.argument("resource", type=click.STRING)
@click.pass_context
@requires_init
def connection(ctx: click.Context, resource: str):
    click.echo(import_connection(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], resource))


@_import.command(cls=OctaviaCommand, name="all", help=build_help_message("all"))
@click.pass_context
@requires_init
def all(ctx: click.Context):
    api_client, workspace_id = ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"]
    for _, _, resource_id in UnmanagedSources(api_client, workspace_id).get_listing():
        import_source_or_destination(api_client, workspace_id, UnmanagedSource, resource_id)
    for _, _, resource_id in UnmanagedDestinations(api_client, workspace_id).get_listing():
        import_source_or_destination(api_client, workspace_id, UnmanagedDestination, resource_id)
    for _, resource_id, _, _, _ in UnmanagedConnections(api_client, workspace_id).get_listing():
        import_connection(api_client, workspace_id, resource_id)


AVAILABLE_COMMANDS: List[click.Command] = [source, destination, connection]


def add_commands_to_list():
    for command in AVAILABLE_COMMANDS:
        _import.add_command(command)


add_commands_to_list()
