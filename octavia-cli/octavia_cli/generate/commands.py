#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import click
import octavia_cli.generate.connection as connection
import octavia_cli.generate.definitions as definitions
from octavia_cli.check_context import ProjectNotInitializedError

from .renderer import ConnectionSpecificationRenderer


@click.command(name="generate", help="Generate a YAML template for a source or a destination.")
@click.argument("definition_type", type=click.Choice(["source", "destination"]))
@click.argument("definition_id", type=click.STRING)
@click.argument("resource_name", type=click.STRING)
@click.pass_context
def generate(ctx: click.Context, definition_type: str, definition_id: str, resource_name: str):
    if not ctx.obj["PROJECT_IS_INITIALIZED"]:
        raise ProjectNotInitializedError(
            "Your octavia project is not initialized, please run 'octavia init' before running 'octavia generate'."
        )

    definition = definitions.factory(definition_type, ctx.obj["API_CLIENT"], definition_id)
    renderer = ConnectionSpecificationRenderer(resource_name, definition)
    output_path = renderer.write_yaml(project_path=".")
    message = f"✅ - Created the specification template for {resource_name} in {output_path}."
    click.echo(click.style(message, fg="green"))


@click.command(name="generate_connection", help="Generate a YAML template for a connection.")
# @click.argument("definition_type", type=click.Choice(["connection"]))
@click.argument("source_id", type=click.STRING)
@click.argument("destination_id", type=click.STRING)
@click.argument("resource_name", type=click.STRING)
@click.pass_context
def generate_connection(ctx: click.Context, source_id: str, destination_id: str, resource_name: str):
    # if not ctx.obj["PROJECT_IS_INITIALIZED"]:
    #     raise ProjectNotInitializedError(
    #         "Your octavia project is not initialized, please run 'octavia init' before running 'octavia generate'."
    #     )

    connection.Connection(ctx.obj["API_CLIENT"], source_id, destination_id, resource_name).generate()
    # renderer = Connection2SpecificationRenderer(conn)
    # output_path = renderer.write_yaml(project_path=".")
    # message = f"✅ - Created the specification template for {resource_name} in {output_path}."
    message = "ohoy"
    click.echo(click.style(message, fg="green"))
