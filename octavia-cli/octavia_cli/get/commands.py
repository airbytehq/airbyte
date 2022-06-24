#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import uuid
from typing import List

import click
from octavia_cli.base_commands import OctaviaCommand

from .resources import Connection, Destination, Source

COMMON_HELP_MESSAGE_PREFIX = "Get a JSON representation of a remote"


def build_help_message(resource_type):
    return f"Get a JSON representation of a remote {resource_type}."


def get_resource_id_or_name(resource):
    resource_id, resource_name = None, None
    try:
        uuid.UUID(resource)
        resource_id = resource
    except ValueError:
        resource_name = resource
    return resource_id, resource_name


def get_json_representation(api_client, workspace_id, ResourceCls, resource_to_get):
    resource_id, resource_name = get_resource_id_or_name(resource_to_get)
    resource = ResourceCls(api_client, workspace_id, resource_id=resource_id, resource_name=resource_name)
    return resource.to_json()


@click.group(
    "get",
    help=f'{build_help_message("source, destination or connection")} ID or name can be used as argument. Example: \'octavia get source "My Pokemon source"\' or \'octavia get source cb5413b2-4159-46a2-910a-dc282a439d2d\'',
)
@click.pass_context
def get(ctx: click.Context):  # pragma: no cover
    pass


@get.command(cls=OctaviaCommand, name="source", help=build_help_message("source"))
@click.argument("resource", type=click.STRING)
@click.pass_context
def source(ctx: click.Context, resource: str):
    click.echo(get_json_representation(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], Source, resource))


@get.command(cls=OctaviaCommand, name="destination", help=build_help_message("destination"))
@click.argument("resource", type=click.STRING)
@click.pass_context
def destination(ctx: click.Context, resource: str):
    click.echo(get_json_representation(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], Destination, resource))


@get.command(cls=OctaviaCommand, name="connection", help=build_help_message("connection"))
@click.argument("resource", type=click.STRING)
@click.pass_context
def connection(ctx: click.Context, resource: str):
    click.echo(get_json_representation(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], Connection, resource))


AVAILABLE_COMMANDS: List[click.Command] = [source, destination, connection]


def add_commands_to_list():
    for command in AVAILABLE_COMMANDS:
        get.add_command(command)


add_commands_to_list()
