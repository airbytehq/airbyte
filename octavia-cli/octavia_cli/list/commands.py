#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

import click

from .listings import Connections, DestinationConnectorsDefinitions, Destinations, SourceConnectorsDefinitions, Sources


@click.group("list", help="List existing Airbyte resources.")
@click.pass_context
def _list(ctx: click.Context):  # pragma: no cover
    pass


@click.group("connectors", help="Latest information on supported sources and destinations connectors.")
@click.pass_context
def connectors(ctx: click.Context):  # pragma: no cover
    pass


@click.group("workspace", help="Latest information on workspace's sources and destinations.")
@click.pass_context
def workspace(ctx: click.Context):  # pragma: no cover
    pass


@connectors.command(name="sources", help="Latest information on supported sources.")
@click.pass_context
def sources_connectors(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    definitions = SourceConnectorsDefinitions(api_client)
    click.echo(definitions)


@connectors.command(name="destination", help="Latest information on supported destinations.")
@click.pass_context
def destinations_connectors(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    definitions = DestinationConnectorsDefinitions(api_client)
    click.echo(definitions)


@workspace.command(help="List existing sources in a workspace.")
@click.pass_context
def sources(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    workspace_id = ctx.obj["WORKSPACE_ID"]
    sources = Sources(api_client, workspace_id)
    click.echo(sources)


@workspace.command(help="List existing destinations in a workspace.")
@click.pass_context
def destinations(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    workspace_id = ctx.obj["WORKSPACE_ID"]
    destinations = Destinations(api_client, workspace_id)
    click.echo(destinations)


@workspace.command(help="List existing connections in a workspace.")
@click.pass_context
def connections(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    workspace_id = ctx.obj["WORKSPACE_ID"]
    connections = Connections(api_client, workspace_id)
    click.echo(connections)


AVAILABLE_COMMANDS: List[click.Command] = [connectors, workspace]


def add_commands_to_list():
    for command in AVAILABLE_COMMANDS:
        _list.add_command(command)


add_commands_to_list()
