#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

import click
from octavia_cli.base_commands import OctaviaCommand

from .deletings import Connections, DestinationConnectorsDefinitions, Destinations, SourceConnectorsDefinitions, Sources


@click.group("delete", help="Delete existing Airbyte resources.")
@click.pass_context
def _delete(ctx: click.Context):  # pragma: no cover
    pass


@click.group("connectors", help="Delete specific source and destination connector available on your Airbyte instance.")
@click.pass_context
def connectors(ctx: click.Context):  # pragma: no cover
    pass


@click.group("workspace", help="Delete existing resorce in workspace.")
@click.pass_context
def workspace(ctx: click.Context):  # pragma: no cover
    pass


@connectors.command(cls=OctaviaCommand, name="sources", help="Delete specific source connector available on your Airbyte instance.")
@click.option("--sourceDefinitionId", "-i", "source_definition_id", required=True, type=str)
@click.pass_context
def sources_connectors(ctx: click.Context, source_definition_id: str):
    api_client = ctx.obj["API_CLIENT"]
    definitions = SourceConnectorsDefinitions(api_client, source_definition_id)
    click.echo(definitions)
    pass


@connectors.command(
    cls=OctaviaCommand, name="destinations", help="Delete specific destination connector available on your Airbyte instance"
)
@click.option("--destinationDefinitionId", "-i", "destination_definition_id", required=True, type=str)
@click.pass_context
def destinations_connectors(ctx: click.Context, destination_definition_id: str):
    api_client = ctx.obj["API_CLIENT"]
    definitions = DestinationConnectorsDefinitions(api_client, destination_definition_id)
    click.echo(definitions)
    pass


@workspace.command(cls=OctaviaCommand, help="Delete existing sources in a workspace.")
@click.option("--sourceId", "-i", "source_id", required=True, type=str)
@click.pass_context
def sources(ctx: click.Context, source_id: str):
    api_client = ctx.obj["API_CLIENT"]
    sources = Sources(api_client, source_id)
    click.echo(sources)
    pass


@workspace.command(cls=OctaviaCommand, help="Delete existing destinations in a workspace.")
@click.option("--destinationId", "-i", "destination_id", required=True, type=str)
@click.pass_context
def destinations(ctx: click.Context, destination_id: str):
    api_client = ctx.obj["API_CLIENT"]
    destinations = Destinations(api_client, destination_id)
    click.echo(destinations)
    pass


@workspace.command(cls=OctaviaCommand, help="Delete existing connections in a workspace.")
@click.option("--connectionId", "-i", "connection_id", required=True, type=str)
@click.pass_context
def connections(ctx: click.Context, connection_id: str):
    api_client = ctx.obj["API_CLIENT"]
    connections = Connections(api_client, connection_id)
    click.echo(connections)
    pass


AVAILABLE_COMMANDS: List[click.Command] = [connectors, workspace]


def add_commands_to_list():
    for command in AVAILABLE_COMMANDS:
        _delete.add_command(command)


add_commands_to_list()
