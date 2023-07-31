#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pathlib

import click
from metadata_service.gcs_upload import upload_metadata_to_gcs, MetadataUploadInfo
from metadata_service.validators.metadata_validator import PRE_UPLOAD_VALIDATORS, validate_and_load
from metadata_service.constants import METADATA_FILE_NAME
from pydantic import ValidationError


def log_metadata_upload_info(metadata_upload_info: MetadataUploadInfo):
    if metadata_upload_info.version_uploaded:
        click.secho(
            f"The metadata file {metadata_upload_info.metadata_file_path} was uploaded to {metadata_upload_info.version_blob_id}.",
            color="green",
        )
    if metadata_upload_info.latest_uploaded:
        click.secho(
            f"The metadata file {metadata_upload_info.metadata_file_path} was uploaded to {metadata_upload_info.latest_blob_id}.",
            color="green",
        )
    if metadata_upload_info.icon_uploaded:
        click.secho(
            f"The icon file {metadata_upload_info.metadata_file_path} was uploaded to {metadata_upload_info.icon_blob_id}.", color="green"
        )


@click.group(help="Airbyte Metadata Service top-level command group.")
def metadata_service():
    pass


@metadata_service.command(help="Validate a given metadata YAML file.")
@click.argument("file_path", type=click.Path(exists=True, path_type=pathlib.Path))
def validate(file_path: pathlib.Path):
    file_path = file_path if not file_path.is_dir() else file_path / METADATA_FILE_NAME

    click.echo(f"Validating {file_path}...")

    metadata, error = validate_and_load(file_path, PRE_UPLOAD_VALIDATORS)
    if metadata:
        click.echo(f"{file_path} is a valid ConnectorMetadataDefinitionV0 YAML file.")
    else:
        click.echo(f"{file_path} is not a valid ConnectorMetadataDefinitionV0 YAML file.")
        click.echo(str(error))
        exit(1)


@metadata_service.command(help="Upload a metadata YAML file to a GCS bucket.")
@click.argument("metadata-file-path", type=click.Path(exists=True, path_type=pathlib.Path))
@click.argument("bucket-name", type=click.STRING)
@click.option("--prerelease", type=click.STRING, required=False, default=None, help="The prerelease tag of the connector.")
def upload(metadata_file_path: pathlib.Path, bucket_name: str, prerelease: str):
    metadata_file_path = metadata_file_path if not metadata_file_path.is_dir() else metadata_file_path / METADATA_FILE_NAME

    try:
        upload_info = upload_metadata_to_gcs(bucket_name, metadata_file_path, prerelease)
        log_metadata_upload_info(upload_info)
    except (ValidationError, FileNotFoundError) as e:
        click.secho(f"The metadata file could not be uploaded: {str(e)}", color="red")
        exit(1)
    if upload_info.uploaded:
        exit(0)
    else:
        click.secho(f"The metadata file {metadata_file_path} was not uploaded.", color="yellow")
        exit(5)
