#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import click

from .definition_specification import (
    DestinationDefinitionSpecification,
    SourceDefinitionSpecification,
)
from .toml_renderer import Renderer


@click.command(name="create", help="Latest information on supported destinations.")
@click.argument("definition_type")
@click.argument("definition_id")
@click.pass_context
def create(ctx: click.Context, definition_type: str, definition_id: str):
    api_client = ctx.obj["API_CLIENT"]
    if definition_type == "source":
        definition_specification = SourceDefinitionSpecification(api_client, definition_id)
    elif definition_type == "destination":
        definition_specification = DestinationDefinitionSpecification(api_client, definition_id)
    renderer = Renderer(definition_specification)
    print(renderer.write_toml("/Users/augustin/Desktop/example.toml"))
