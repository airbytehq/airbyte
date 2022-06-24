#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

import click
from octavia_cli.base_commands import OctaviaCommand

from .resources import Connection, Destination, Source


@click.group("get", help="Get a YAML spec for a source, destination or a connection.")
@click.pass_context
def get(ctx: click.Context):
    pass


@get.command(cls=OctaviaCommand, name="source", help="Get YAML for a source")
@click.argument("resource_id", type=click.STRING)
@click.pass_context
def source(ctx: click.Context, resource_id: str):
    resource = Source(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], resource_id)
    click.echo(resource.get_config())


@get.command(cls=OctaviaCommand, name="destination", help="Get YAML for a destination")
@click.argument("resource_id", type=click.STRING)
@click.pass_context
def destination(ctx: click.Context, resource_id: str):
    resource = Destination(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], resource_id)
    click.echo(resource.get_config())


@get.command(cls=OctaviaCommand, name="connection", help="Get YAML for a connection")
@click.argument("resource_id", type=click.STRING)
@click.pass_context
def connection(ctx: click.Context, resource_id: str):
    resource = Connection(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], resource_id)
    click.echo(resource.get_config())


AVAILABLE_COMMANDS: List[click.Command] = [source, destination, connection]


def add_commands_to_list():
    for command in AVAILABLE_COMMANDS:
        get.add_command(command)


add_commands_to_list()
