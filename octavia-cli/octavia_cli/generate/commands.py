#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import click
import octavia_cli.generate.definitions as definitions
from octavia_cli.check_context import requires_init

from .renderer import ConnectionSpecificationRenderer


@click.command(name="generate", help="Generate a YAML template for a source or a destination.")
@click.argument("definition_type", type=click.Choice(["source", "destination"]))
@click.argument("definition_id", type=click.STRING)
@click.argument("resource_name", type=click.STRING)
@click.pass_context
@requires_init
def generate(ctx: click.Context, definition_type: str, definition_id: str, resource_name: str):
    definition = definitions.factory(definition_type, ctx.obj["API_CLIENT"], definition_id)
    renderer = ConnectionSpecificationRenderer(resource_name, definition)
    output_path = renderer.write_yaml(project_path=".")
    message = f"✅ - Created the specification template for {resource_name} in {output_path}."
    click.echo(click.style(message, fg="green"))
