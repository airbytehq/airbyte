import click
import yaml
from pydantic import ValidationError
from metadata_service.models.generated.ConnectorMetadataDefinitionV1 import ConnectorMetadataDefinitionV1


@click.command()
# @click.argument("file_path")
def validate_metadata_file():
    """
    Validates a metadata YAML file against a metadata Pydantic model.
    """
    print("WTF!!!")
    file_path = "airbyte-integrations/connectors/source-sentry/FAKE.yml"
    print('Validating metadata file: {}'.format(file_path))
    return "Hi"
    # with open(file_path, "r") as f:
    #     try:
    #         metadata = yaml.safe_load(f)
    #         ConnectorMetadataDefinitionV1.parse_obj(metadata)
    #         click.echo(f"{file_path} is a valid ConnectorMetadataDefinitionV1 YAML file.")
    #     except Exception as e:
    #         click.echo(f"{file_path} is not a valid ConnectorMetadataDefinitionV1 YAML file.")
    #         click.echo(str(e))
    #         exit(1)
