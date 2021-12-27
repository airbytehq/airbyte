import click

import openapi_client
from openapi_client.api import destination_definition_api
from openapi_client.model.destination_definition_read_list import DestinationDefinitionReadList
import scolp 

@click.group("list", help="List existing Airbyte resources.")
@click.pass_context
def _list(ctx):
    pass

@click.group("definitions", help="Latest information on supported sources and destinations.")
@click.pass_context
def definitions(ctx):
    pass

_list.add_command(definitions)

@definitions.command(name="destinations", help="Latest information on supported destinations.")
@click.pass_context
def destinations(ctx):
    api_client = ctx.obj["API_CLIENT"]
    api_instance = destination_definition_api.DestinationDefinitionApi(api_client)
    api_response = api_instance.list_latest_destination_definitions()
    defs = []
    scolper = scolp.Scolp()
    scolper.config.add_columns("name", "docker image", "version", "destination definition id")

    defs = [(definition.name, definition.docker_repository, definition.docker_image_tag, definition.destination_definition_id) for definition in api_response["destination_definitions"]]
    for definition in defs:
        scolper.print(*definition)
