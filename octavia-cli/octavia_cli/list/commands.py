#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from enum import Enum

import click

from .definitions import DefinitionType, DestinationDefinitions, SourceDefinitions


@click.group("list", help="List existing Airbyte resources.")
@click.pass_context
def _list(ctx: click.Context):
    pass


@click.group("connectors", help="Latest information on supported sources and destinations connectors.")
@click.pass_context
def connectors(ctx: click.Context):
    pass


_list.add_command(connectors)


@connectors.command(help="Latest information on supported sources.")
@click.pass_context
def sources(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    definitions = SourceDefinitions(api_client)
    click.echo(definitions)


@connectors.command(help="Latest information on supported destinations.")
@click.pass_context
def destinations(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    definitions = DestinationDefinitions(api_client)
    click.echo(definitions)
