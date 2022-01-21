#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

import click

from .connectors_definitions import DestinationConnectorsDefinitions, SourceConnectorsDefinitions


@click.group("list", help="List existing Airbyte resources.")
@click.pass_context
def _list(ctx: click.Context):  # pragma: no cover
    pass


@click.group("connectors", help="Latest information on supported sources and destinations connectors.")
@click.pass_context
def connectors(ctx: click.Context):  # pragma: no cover
    pass


@connectors.command(help="Latest information on supported sources.")
@click.pass_context
def sources(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    definitions = SourceConnectorsDefinitions(api_client)
    click.echo(definitions)


@connectors.command(help="Latest information on supported destinations.")
@click.pass_context
def destinations(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    definitions = DestinationConnectorsDefinitions(api_client)
    click.echo(definitions)


AVAILABLE_COMMANDS: List[click.Command] = [connectors]


def add_commands_to_list():
    for command in AVAILABLE_COMMANDS:
        _list.add_command(command)


add_commands_to_list()
