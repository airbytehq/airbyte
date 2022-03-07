#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from importlib import resources
from xml.sax import parseString

import click
import octavia_cli.generate.definitions as definitions

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


@generate.command(name="destination", help="Create YAML for a source")
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
@click.argument("source", type=click.STRING)
@click.argument("destination", type=click.STRING)
@click.argument("resource_name", type=click.STRING)
@click.pass_context
def connection(ctx: click.Context, source_file_path: str, destination_file_path: str, resource_name: str):
    source = definitions.factory("source", ctx.obj["API_CLIENT"], source_file_path)
    destination = definitions.factory("source", ctx.obj["API_CLIENT"], destination_file_path)
    if not (source.was_created and destination.was_created):
        raise resources.NonExistingResourceError("To create a connection both source and destination must be already created.")
    connection_renderer = ConnectionRenderer(resource_name, source.resource_id, destination.resource_id, source.streams)
    output_path = connection_renderer.write_yaml(project_path=".")
    message = f"✅ - Created the specification template for {resource_name} in {output_path}."
    click.echo(click.style(message, fg="green"))
