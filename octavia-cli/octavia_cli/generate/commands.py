#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import click
import octavia_cli.generate.definitions as definitions
from octavia_cli.apply import resources
from octavia_cli.base_commands import OctaviaCommand
from octavia_cli.check_context import requires_init

from .renderers import ConnectionRenderer, ConnectorSpecificationRenderer


@click.group("generate", help="Generate a YAML template for a source, destination or a connection.")
@click.pass_context
@requires_init
def generate(ctx: click.Context):
    pass


def generate_source_or_destination(definition_type, api_client, workspace_id, definition_id, resource_name):
    definition = definitions.factory(definition_type, api_client, workspace_id, definition_id)
    renderer = ConnectorSpecificationRenderer(resource_name, definition)
    output_path = renderer.write_yaml(project_path=".")
    message = f"✅ - Created the {definition_type} template for {resource_name} in {output_path}."
    click.echo(click.style(message, fg="green"))


@generate.command(cls=OctaviaCommand, name="source", help="Create YAML for a source")
@click.argument("definition_id", type=click.STRING)
@click.argument("resource_name", type=click.STRING)
@click.pass_context
def source(ctx: click.Context, definition_id: str, resource_name: str):
    generate_source_or_destination("source", ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], definition_id, resource_name)


@generate.command(cls=OctaviaCommand, name="destination", help="Create YAML for a destination")
@click.argument("definition_id", type=click.STRING)
@click.argument("resource_name", type=click.STRING)
@click.pass_context
def destination(ctx: click.Context, definition_id: str, resource_name: str):
    generate_source_or_destination("destination", ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], definition_id, resource_name)


@generate.command(cls=OctaviaCommand, name="connection", help="Generate a YAML template for a connection.")
@click.argument("connection_name", type=click.STRING)
@click.option(
    "--source",
    "source_path",
    type=click.Path(exists=True, readable=True),
    required=True,
    help="Path to the YAML fine defining your source configuration.",
)
@click.option(
    "--destination",
    "destination_path",
    type=click.Path(exists=True, readable=True),
    required=True,
    help="Path to the YAML fine defining your destination configuration.",
)
@click.pass_context
def connection(ctx: click.Context, connection_name: str, source_path: str, destination_path: str):
    source = resources.factory(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], source_path)
    if not source.was_created:
        raise resources.NonExistingResourceError(
            f"The source defined at {source_path} does not exists. Please run octavia apply before creating this connection."
        )

    destination = resources.factory(ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"], destination_path)
    if not destination.was_created:
        raise resources.NonExistingResourceError(
            f"The destination defined at {destination_path} does not exists. Please run octavia apply before creating this connection."
        )

    connection_renderer = ConnectionRenderer(connection_name, source, destination)
    output_path = connection_renderer.write_yaml(project_path=".")
    message = f"✅ - Created the connection template for {connection_name} in {output_path}."
    click.echo(click.style(message, fg="green"))
