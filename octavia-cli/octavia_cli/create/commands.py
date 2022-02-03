#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import click
from octavia_cli.check_context import ProjectNotInitizialiedError

from .definition_specification import (
    DestinationDefinitionSpecification,
    SourceDefinitionSpecification,
)
from .renderer import SpecRenderer


@click.command(name="create", help="Latest information on supported destinations.")
@click.argument("definition_type")
@click.argument("definition_id")
@click.argument("definition_name")
@click.pass_context
def create(ctx: click.Context, definition_type: str, definition_id: str, definition_name: str):
    if not ctx.obj["PROJECT_IS_INITIALIZED"]:
        raise ProjectNotInitizialiedError(
            "Your octavia project is not initialized, please run 'octavia init' before running 'octavia create'."
        )
    api_client = ctx.obj["API_CLIENT"]
    if definition_type == "source":
        definition_specification = SourceDefinitionSpecification(api_client, definition_id)
    elif definition_type == "destination":
        definition_specification = DestinationDefinitionSpecification(api_client, definition_id)
    renderer = SpecRenderer(
        definition_name,
        definition_specification.definition_type,
        definition_specification.id,
        definition_specification.definition.docker_repository,
        definition_specification.definition.docker_image_tag,
        definition_specification.definition.documentation_url,
        definition_specification.schema,
    )
    output_file = renderer.write_yaml(project_path=".")
