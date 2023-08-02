from dagster import get_dagster_logger
from dagster_gcp.gcs.file_manager import GCSFileManager, GCSFileHandle

from orchestrator.models.metadata import LatestMetadataEntry
from metadata_service.constants import METADATA_FILE_NAME
from metadata_service.gcs_upload import get_metadata_remote_file_path
from metadata_service.models.generated.ConnectorRegistrySourceDefinition import ConnectorRegistrySourceDefinition
from metadata_service.models.generated.ConnectorRegistryDestinationDefinition import ConnectorRegistryDestinationDefinition

from typing import Union

PolymorphicRegistryEntry = Union[ConnectorRegistrySourceDefinition, ConnectorRegistryDestinationDefinition]

def _is_docker_repository_overridden(metadata_entry: LatestMetadataEntry, registry_entry: PolymorphicRegistryEntry,) -> bool:
    """Check if the docker repository is overridden in the registry entry."""
    registry_entry_docker_repository = registry_entry.dockerRepository
    metadata_docker_repository = metadata_entry.metadata_definition.data.dockerRepository
    return registry_entry_docker_repository != metadata_docker_repository

def _get_version_specific_registry_entry_file_path(registry_entry, registry_name):
    """Get the file path for the version specific registry entry file."""
    docker_reposiory = registry_entry.dockerRepository
    docker_version = registry_entry.dockerImageTag

    assumed_metadata_file_path = get_metadata_remote_file_path(docker_reposiory, docker_version)
    registry_entry_file_path = assumed_metadata_file_path.replace(METADATA_FILE_NAME, registry_name)
    return registry_entry_file_path

def _check_for_invalid_write_path(write_path: str):
    """Check if the write path is valid."""

    if "latest" in write_path:
        raise ValueError("Cannot write to a path that contains 'latest'. That is reserved for the latest metadata file and its direct transformations")

def write_registry_to_overrode_file_paths(
    registry_entry: PolymorphicRegistryEntry,
    registry_name: str,
    metadata_entry: LatestMetadataEntry,
    registry_directory_manager: GCSFileManager,
) -> GCSFileHandle:
    """
    Write the registry entry to the docker repository and version specific file paths
    in the event that the docker repository is overridden.

    Underlying issue:
        The registry entry files (oss.json and cloud.json) are traditionally written to
        the same path as the metadata.yaml file that created them. This is fine for the
        most cases, but when the docker repository is overridden, the registry entry
        files need to be written to a different path.

        For example if source-postgres:dev.123 is overridden to source-postgres-strict-encrypt:dev.123
        then the oss.json file needs to be written to the path that would be assumed
        by the platform when looking for a specific registry entry. In this case, for cloud, it would be
        gs://my-bucket/metadata/source-postgres-strict-encrypt/dev.123/cloud.json

        Ideally we would not have to do this, but the combination of prereleases and common overrides
        make this nessesary.

    Args:
        registry_entry (PolymorphicRegistryEntry): The registry entry to write
        registry_name (str): The name of the registry entry (oss or cloud)
        metadata_entry (LatestMetadataEntry): The metadata entry that created the registry entry
        registry_directory_manager (GCSFileManager): The file manager to use to write the registry entry

    Returns:
        GCSFileHandle: The file handle of the written registry entry
    """
    if not _is_docker_repository_overridden(metadata_entry, registry_entry):
        return None
    logger = get_dagster_logger()
    registry_entry_json = registry_entry.json(exclude_none=True)
    overrode_registry_entry_version_write_path = _get_version_specific_registry_entry_file_path(registry_entry, registry_name)
    _check_for_invalid_write_path(overrode_registry_entry_version_write_path)
    logger.info(f"Writing registry entry to {overrode_registry_entry_version_write_path}")
    file_handle = registry_directory_manager.write_data(registry_entry_json.encode("utf-8"), ext="json", key=overrode_registry_entry_version_write_path)
    logger.info(f"Successfully wrote registry entry to {file_handle.public_url}")
    return file_handle

