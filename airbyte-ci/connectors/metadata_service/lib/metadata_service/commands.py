#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pathlib

import click
from metadata_service.gcs_upload import upload_metadata_to_gcs
from metadata_service.validators.metadata_validator import validate_metadata_file
from metadata_service.constants import METADATA_FILE_NAME
from pydantic import ValidationError


@click.group(help="Airbyte Metadata Service top-level command group.")
def metadata_service():
    pass


@metadata_service.command(help="Validate a given metadata YAML file.")
@click.argument("file_path", type=click.Path(exists=True, path_type=pathlib.Path))
def validate(file_path: pathlib.Path):
    file_path = file_path if not file_path.is_dir() else file_path / METADATA_FILE_NAME

    click.echo(f"Validating {file_path}...")

    is_valid, error = validate_metadata_file(file_path)
    if is_valid:
        click.echo(f"{file_path} is a valid ConnectorMetadataDefinitionV0 YAML file.")
    else:
        click.echo(f"{file_path} is not a valid ConnectorMetadataDefinitionV0 YAML file.")
        click.echo(str(error))
        exit(1)


@metadata_service.command(help="Upload a metadata YAML file to a GCS bucket.")
@click.argument("metadata-file-path", type=click.Path(exists=True, path_type=pathlib.Path))
@click.argument("bucket-name", type=click.STRING)
@click.option(
    "--service-account-file-path", "-sa", type=click.Path(exists=True, path_type=pathlib.Path), envvar="GOOGLE_APPLICATION_CREDENTIALS"
)
def upload(metadata_file_path: pathlib.Path, bucket_name: str, service_account_file_path: pathlib.Path):
    metadata_file_path = metadata_file_path if not metadata_file_path.is_dir() else metadata_file_path / METADATA_FILE_NAME
    try:
        uploaded, blob_id = upload_metadata_to_gcs(bucket_name, metadata_file_path, service_account_file_path)
    except (ValidationError, FileNotFoundError) as e:
        click.secho(f"The metadata file could not be uploaded: {str(e)}", color="red")
        exit(1)
    if uploaded:
        click.secho(f"The metadata file {metadata_file_path} was uploaded to {blob_id}.", color="green")
        exit(0)
    else:
        click.secho(f"The metadata file {metadata_file_path} was not uploaded.", color="yellow")
        exit(5)
