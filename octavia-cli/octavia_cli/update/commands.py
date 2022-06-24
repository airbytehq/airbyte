#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

import click
from octavia_cli.base_commands import OctaviaCommand
from octavia_cli.generate import definitions
from octavia_cli.generate.commands import generate_source_or_destination
from octavia_cli.generate.renderers import ConnectorSpecificationRenderer
from octavia_cli.get.resources import Connection, Destination, Source
from octavia_cli.list.listings import Destinations, Sources


@click.group("update", help="Update configurations in a YAML spec for a source, destination or a connection.")
@click.pass_context
def update(ctx: click.Context):
    pass


def list_resource(resource_type, api_client, workspace_id):
    resources = resource_type(api_client, workspace_id)
    return {resource_id: resource_name for resource_name, _, resource_id in resources.get_listing()}


def get_resource_definition_id(resource_type, api_client, workspace_id, resource_id):
    resource = resource_type(api_client, workspace_id, resource_id)
    config = resource.get_config()
    return config[f"{resource_type.name}_definition_id"]


def update_resource(resource_type, api_client, workspace_id, resource_id):
    resource = resource_type(api_client, workspace_id, resource_id)
    definition_type = resource_type.name
    config = resource.get_config()
    definition_id = config[f"{resource_type.name}_definition_id"]
    # Schema varies across resources, e.g. pull "name" else default to "source_name"
    resource_name = config.get("name") or config[f"{resource_type.name}_name"]

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


@update.command(cls=OctaviaCommand, name="sources", help="Get YAML for a source")
@click.pass_context
def sources(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    workspace_id = ctx.obj["WORKSPACE_ID"]
    sources = list_resource(Sources, api_client, workspace_id)

    for source_id, source_name in sources.items():
        definition_id = get_resource_definition_id(Source, api_client, workspace_id, source_id)

        generate_source_or_destination("source", api_client, workspace_id, definition_id, source_name)

        update_resource(Source, api_client, workspace_id, source_id)


@update.command(cls=OctaviaCommand, name="destinations", help="Get YAML for a destination")
@click.pass_context
def destinations(ctx: click.Context):
    api_client = ctx.obj["API_CLIENT"]
    workspace_id = ctx.obj["WORKSPACE_ID"]
    destinations = list_resource(Destinations, api_client, workspace_id)

    for destination_id, destination_name in destinations.items():
        definition_id = get_resource_definition_id(Destination, api_client, workspace_id, destination_id)

        generate_source_or_destination("destination", api_client, workspace_id, definition_id, destination_name)

        update_resource(Destination, api_client, workspace_id, destination_id)


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
