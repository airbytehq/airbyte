#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import pathlib

import click
import sentry_sdk
from pydantic import ValidationError

from metadata_service.constants import METADATA_FILE_NAME, VALID_REGISTRIES
from metadata_service.gcs_upload import (
    MetadataDeleteInfo,
    MetadataUploadInfo,
    delete_release_candidate_from_gcs,
    promote_release_candidate_in_gcs,
    upload_metadata_to_gcs,
)
from metadata_service.registry import generate_and_persist_connector_registry
from metadata_service.sentry import setup_sentry
from metadata_service.specs_secrets_mask import generate_and_persist_specs_secrets_mask
from metadata_service.stale_metadata_report import generate_and_publish_stale_metadata_report
from metadata_service.validators.metadata_validator import PRE_UPLOAD_VALIDATORS, ValidatorOptions, validate_and_load


def setup_logging(debug: bool = False):
    """Configure logging for the CLI."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()],
    )
    # Suppress logging from the following libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("slack_sdk.web.base_client").setLevel(logging.WARNING)
    logging.getLogger("google.resumable_media").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


def log_metadata_upload_info(metadata_upload_info: MetadataUploadInfo):
    """Log the results of the metadata upload."""
    for file in metadata_upload_info.uploaded_files:
        if file.uploaded:
            click.secho(f"File:{file.id} for {metadata_upload_info.metadata_file_path} was uploaded to {file.blob_id}.", fg="green")
        else:
            click.secho(
                f"File:{file.id} for {metadata_upload_info.metadata_file_path} was not uploaded.",
                fg="yellow",
            )


def log_metadata_deletion_info(metadata_deletion_info: MetadataDeleteInfo):
    """Log the results of the metadata deletion."""
    for remote_file in metadata_deletion_info.deleted_files:
        if remote_file.deleted:
            click.secho(f"The {remote_file.description} was deleted ({remote_file.blob_id}).", fg="green")
        else:
            click.secho(
                f"The {remote_file.description} was not deleted ({remote_file.blob_id}).",
                fg="red",
            )


@click.group(help="Airbyte Metadata Service top-level command group.")
@click.option("--debug", is_flag=True, help="Enable debug logging", default=False)
def metadata_service(debug: bool):
    """Top-level command group with logging configuration."""
    setup_sentry()
    setup_logging(debug)


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
@click.option("--disable-dockerhub-checks", is_flag=True, help="Disable 'image exists on DockerHub' validations.", default=False)
def upload(metadata_file_path: pathlib.Path, docs_path: pathlib.Path, bucket_name: str, prerelease: str, disable_dockerhub_checks: bool):
    metadata_file_path = metadata_file_path if not metadata_file_path.is_dir() else metadata_file_path / METADATA_FILE_NAME
    validator_opts = ValidatorOptions(
        docs_path=str(docs_path), prerelease_tag=prerelease, disable_dockerhub_checks=disable_dockerhub_checks
    )
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


@metadata_service.command(help="Generate and publish a stale metadata report to Slack.")
@click.argument("bucket-name", type=click.STRING, required=True)
def publish_stale_metadata_report(bucket_name: str):
    click.echo(f"Starting stale metadata report for bucket: {bucket_name}")
    logger.debug("Starting stale metadata report generation and publishing process")
    try:
        report_published, error_message = generate_and_publish_stale_metadata_report(bucket_name)
        if not report_published:
            logger.warning(f"Failed to publish the report to Slack: '{error_message}'.")
            click.secho(f"WARNING: The stale metadata report could not be published: '{error_message}'", fg="red")
            exit(1)
        else:
            click.secho(f"Stale metadata report for bucket: {bucket_name} completed successfully", fg="green")
        logger.debug("Stale metadata report generation and publishing process completed.")
    except Exception as e:
        logger.error(f"A fatal error occurred when generating and publishing the stale metadata report: '{e}'")
        click.secho(f"FATAL ERROR: The stale metadata report could not be published: '{e}'", fg="red")
        exit(1)


@metadata_service.command(help="Rollback a release candidate by deleting its metadata files from a GCS bucket.")
@click.argument("connector-docker-repository", type=click.STRING)
@click.argument("connector-version", type=click.STRING)
@click.argument("bucket-name", type=click.STRING)
def rollback_release_candidate(connector_docker_repository: str, connector_version: str, bucket_name: str):
    try:
        deletion_info = delete_release_candidate_from_gcs(bucket_name, connector_docker_repository, connector_version)
        log_metadata_deletion_info(deletion_info)
    except (FileNotFoundError, ValueError) as e:
        click.secho(f"The release candidate could not be deleted: {str(e)}", fg="red")
        exit(1)


@metadata_service.command(help="Promote a release candidate by moving its metadata files to the main release folder in a GCS bucket.")
@click.argument("connector-docker-repository", type=click.STRING)
@click.argument("connector-version", type=click.STRING)
@click.argument("bucket-name", type=click.STRING)
def promote_release_candidate(connector_docker_repository: str, connector_version: str, bucket_name: str):
    try:
        upload_info, deletion_info = promote_release_candidate_in_gcs(bucket_name, connector_docker_repository, connector_version)
        log_metadata_upload_info(upload_info)
        log_metadata_deletion_info(deletion_info)
    except (FileNotFoundError, ValueError) as e:
        click.secho(f"The release candidate could not be promoted: {str(e)}", fg="red")
        exit(1)


@metadata_service.command(help="Generate the cloud registry and persist it to GCS.")
@click.argument("bucket-name", type=click.STRING, required=True)
@click.argument("registry-type", type=click.Choice(VALID_REGISTRIES), required=True)
@sentry_sdk.trace
def generate_connector_registry(bucket_name: str, registry_type: str):
    # Set Sentry context for the generate_registry command
    sentry_sdk.set_tag("command", "generate_registry")
    sentry_sdk.set_tag("bucket_name", bucket_name)
    sentry_sdk.set_tag("registry_type", registry_type)

    logger.info(f"Starting {registry_type} registry generation and upload process.")
    try:
        generate_and_persist_connector_registry(bucket_name, registry_type)
        logger.info(f"SUCCESS: {registry_type} registry generation and upload process completed successfully.")
        sentry_sdk.set_tag("operation_success", True)
    except Exception as e:
        sentry_sdk.set_tag("operation_success", False)
        sentry_sdk.capture_exception(e)
        logger.error(f"FATAL ERROR: An error occurred when generating and persisting the {registry_type} registry: {str(e)}")
        exit(1)


@metadata_service.command(help="Generate the specs secrets mask and persist it to GCS.")
@click.argument("bucket-name", type=click.STRING, required=True)
@sentry_sdk.trace
def generate_specs_secrets_mask(bucket_name: str):
    # Set Sentry context for the generate_specs_secrets_mask command
    sentry_sdk.set_tag("command", "generate_specs_secrets_mask")
    sentry_sdk.set_tag("bucket_name", bucket_name)

    logger.info("Starting specs secrets mask generation and upload process.")
    try:
        generate_and_persist_specs_secrets_mask(bucket_name)
        sentry_sdk.set_tag("operation_success", True)
        logger.info("Specs secrets mask generation and upload process completed successfully.")
    except Exception as e:
        sentry_sdk.set_tag("operation_success", False)
        sentry_sdk.capture_exception(e)
        logger.error(f"FATAL ERROR: An error occurred when generating and persisting the specs secrets mask: {str(e)}")
        exit(1)
