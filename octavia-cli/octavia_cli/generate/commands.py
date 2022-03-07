#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from xml.sax import parseString

import click
import octavia_cli.generate.definitions as definitions

from .catalog import Catalog
from .renderer import ConnectionRenderer, ConnectionSpecificationRenderer


@click.group("generate", help="Generate a YAML template for a source, destination or a connection.")
@click.pass_context
def generate(ctx: click.Context):  # pragma: no cover
    parseString


@generate.command(name="source", help="Create YAML for a source")
@click.argument("definition_id", type=click.STRING)
@click.argument("resource_name", type=click.STRING)
@click.pass_context
def source(ctx: click.Context, definition_id: str, resource_name: str):
    definition = definitions.factory("source", ctx.obj["API_CLIENT"], definition_id)
    renderer = ConnectionSpecificationRenderer(resource_name, definition)
    output_path = renderer.write_yaml(project_path=".")
    message = f"✅ - Created the specification template for {resource_name} in {output_path}."
    click.echo(click.style(message, fg="green"))


@generate.command(name="destination", help="Create YAML for a destination")
@click.argument("definition_id", type=click.STRING)
@click.argument("resource_name", type=click.STRING)
@click.pass_context
def destination(ctx: click.Context, definition_id: str, resource_name: str):
    definition = definitions.factory("destination", ctx.obj["API_CLIENT"], definition_id)
    renderer = ConnectionSpecificationRenderer(resource_name, definition)
    output_path = renderer.write_yaml(project_path=".")
    message = f"✅ - Created the specification template for {resource_name} in {output_path}."
    click.echo(click.style(message, fg="green"))


@generate.command(name="connection", help="Generate a YAML template for a connection.")
@click.argument("source_id", type=click.STRING)
@click.argument("destination_id", type=click.STRING)
@click.argument("resource_name", type=click.STRING)
@click.pass_context
def connection(ctx: click.Context, source_id: str, destination_id: str, resource_name: str):
    source_streams = Catalog(ctx.obj["API_CLIENT"], source_id=source_id).get_streams()
    connection_renderer = ConnectionRenderer(resource_name, source_id, destination_id, source_streams)
    output_path = connection_renderer.write_yaml(project_path=".")
    message = f"✅ - Created the specification template for {resource_name} in {output_path}."
    click.echo(click.style(message, fg="green"))
