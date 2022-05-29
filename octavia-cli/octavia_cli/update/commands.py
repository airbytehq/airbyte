#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

import click
from octavia_cli.base_commands import OctaviaCommand
from octavia_cli.generate import definitions
from octavia_cli.generate.renderers import ConnectorSpecificationRenderer
from octavia_cli.get.resources import Connection, Destination, Source


@click.group("update", help="Update configurations in a YAML spec for a source, destination or a connection.")
@click.pass_context
def update(ctx: click.Context):
    pass


def update_resource(resource_type, api_client, workspace_id, resource_id):
    resource = resource_type(api_client, workspace_id, resource_id)
    definition_type = resource_type.name
    config = resource.get_config()
    definition_id = config[f"{resource_type.name}_definition_id"]
    resource_name = config[f"{resource_type.name}_name"]

    definition = definitions.factory(definition_type, api_client, workspace_id, definition_id)
    renderer = ConnectorSpecificationRenderer(resource_name, definition)

    output_path = renderer.update_configuration(project_path=".", configuration=config["connection_configuration"])
    message = f"✅ - Updated the {resource_type.name} template for {resource_name} in {output_path}."
    click.echo(click.style(message, fg="green"))


@update.command(cls=OctaviaCommand, name="source", help="Get YAML for a source")
@click.argument("resource_id", type=click.STRING)
@click.pass_context
def source(ctx: click.Context, resource_id: str):
    update_resource(Source, ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], resource_id)


@update.command(cls=OctaviaCommand, name="destination", help="Get YAML for a destination")
@click.argument("resource_id", type=click.STRING)
@click.pass_context
def destination(ctx: click.Context, resource_id: str):
    update_resource(Destination, ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], resource_id)


@update.command(cls=OctaviaCommand, name="connection", help="Get YAML for a connection")
@click.argument("resource_id", type=click.STRING)
@click.pass_context
def connection(ctx: click.Context, resource_id: str):
    update_resource(Connection, ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], resource_id)


AVAILABLE_COMMANDS: List[click.Command] = [source, destination, connection]


def add_commands_to_list():
    for command in AVAILABLE_COMMANDS:
        update.add_command(command)


add_commands_to_list()
