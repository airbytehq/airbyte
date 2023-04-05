import click
import pathlib

from metadata_service.validators.metadata_validator import validate_metadata_file


@click.group(help="Airbyte Metadata Service top-level command group.")
def metadata_service():
    pass


@metadata_service.command(help="Validate a given metadata YAML file.")
@click.argument("file_path", type=click.Path(exists=True, path_type=pathlib.Path))
def validate(file_path: pathlib.Path):
    file_path = file_path if not file_path.is_dir() else file_path / "metadata.yml"

    click.echo(f"Validating {file_path}...")

    is_valid, error = validate_metadata_file(file_path)
    if is_valid:
        click.echo(f"{file_path} is a valid ConnectorMetadataDefinitionV1 YAML file.")
    else:
        click.echo(f"{file_path} is not a valid ConnectorMetadataDefinitionV1 YAML file.")
        click.echo(str(error))
        exit(1)
