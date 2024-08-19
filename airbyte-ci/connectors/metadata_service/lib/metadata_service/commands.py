#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pathlib

import click
from metadata_service.constants import METADATA_FILE_NAME
from metadata_service.gcs_upload import MetadataUploadInfo, upload_metadata_to_gcs
from metadata_service.validators.metadata_validator import PRE_UPLOAD_VALIDATORS, ValidatorOptions, validate_and_load
from pydantic import ValidationError


def log_metadata_upload_info(metadata_upload_info: MetadataUploadInfo):
    for file in metadata_upload_info.uploaded_files:
        if file.uploaded:
            click.secho(
                f"The {file.description} file for {metadata_upload_info.metadata_file_path} was uploaded to {file.blob_id}.", fg="green"
            )
        else:
            click.secho(
                f"The {file.description} file for {metadata_upload_info.metadata_file_path} was not uploaded. Reason: {file.blob_id}",
                fg="yellow",
            )


@click.group(help="Airbyte Metadata Service top-level command group.")
def metadata_service():
    pass


@metadata_service.command(help="Validate a given metadata YAML file.")
@click.argument("metadata_file_path", type=click.Path(exists=True, path_type=pathlib.Path), required=True)
@click.argument("docs_path", type=click.Path(exists=True, path_type=pathlib.Path), required=True)
def validate(metadata_file_path: pathlib.Path, docs_path: pathlib.Path):
    metadata_file_path = metadata_file_path if not metadata_file_path.is_dir() else metadata_file_path / METADATA_FILE_NAME

    click.echo(f"Validating {metadata_file_path}...")
    metadata, error = validate_and_load(metadata_file_path, PRE_UPLOAD_VALIDATORS, ValidatorOptions(docs_path=str(docs_path)))
    if metadata:
        click.echo(f"{metadata_file_path} is a valid ConnectorMetadataDefinitionV0 YAML file.")
    else:
        click.echo(f"{metadata_file_path} is not a valid ConnectorMetadataDefinitionV0 YAML file.")
        click.echo(str(error))
        exit(1)


@metadata_service.command(help="Upload a metadata YAML file to a GCS bucket.")
@click.argument("metadata-file-path", type=click.Path(exists=True, path_type=pathlib.Path), required=True)
@click.argument("docs-path", type=click.Path(exists=True, path_type=pathlib.Path), required=True)
@click.argument("bucket-name", type=click.STRING, required=True)
@click.option("--prerelease", type=click.STRING, required=False, default=None, help="The prerelease tag of the connector.")
def upload(metadata_file_path: pathlib.Path, docs_path: pathlib.Path, bucket_name: str, prerelease: str):
    metadata_file_path = metadata_file_path if not metadata_file_path.is_dir() else metadata_file_path / METADATA_FILE_NAME
    validator_opts = ValidatorOptions(docs_path=str(docs_path), prerelease_tag=prerelease)
    try:
        upload_info = upload_metadata_to_gcs(bucket_name, metadata_file_path, validator_opts)
        log_metadata_upload_info(upload_info)
    except (ValidationError, FileNotFoundError) as e:
        click.secho(f"The metadata file could not be uploaded: {str(e)}", fg="red")
        exit(1)
    if upload_info.metadata_uploaded:
        exit(0)
    else:
        exit(5)
