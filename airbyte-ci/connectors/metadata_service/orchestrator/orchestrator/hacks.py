#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

import pandas as pd
from dagster import OpExecutionContext
from metadata_service.constants import METADATA_FILE_NAME, METADATA_FOLDER
from metadata_service.models.generated.ConnectorRegistryDestinationDefinition import ConnectorRegistryDestinationDefinition
from metadata_service.models.generated.ConnectorRegistrySourceDefinition import ConnectorRegistrySourceDefinition


PolymorphicRegistryEntry = Union[ConnectorRegistrySourceDefinition, ConnectorRegistryDestinationDefinition]


def _get_version_specific_registry_entry_file_path(registry_entry, registry_name):
    """Get the file path for the version specific registry entry file."""
    docker_repository = registry_entry.dockerRepository
    docker_version = registry_entry.dockerImageTag

    assumed_metadata_file_path = f"{METADATA_FOLDER}/{docker_repository}/{docker_version}/{METADATA_FILE_NAME}"
    registry_entry_file_path = assumed_metadata_file_path.replace(METADATA_FILE_NAME, registry_name)
    return registry_entry_file_path


def _check_for_invalid_write_path(write_path: str):
    """Check if the write path is valid."""

    if "latest" in write_path:
        raise ValueError(
            "Cannot write to a path that contains 'latest'. That is reserved for the latest metadata file and its direct transformations"
        )


def construct_registry_entry_write_path(
    registry_entry: PolymorphicRegistryEntry,
    registry_name: str,
) -> str:
    """
    Construct a registry entry write path from its parts.

    Underlying issue:
        This is barely a hack.

        But it is related to a few imperfect design decisions that we have to work around.
        1. Metadata files and the registry entries are saved to the same top level folder.
        2. That save path is determined by the docker repository and version of the image
        3. A metadata file can include overrides for the docker repository and version of the image depending on the registry
        4. The platform looks up registry entries by docker repository and version of the image.
        5. The registry generation depends on what ever registry entry is written to a path ending in latest/{registry_name}.json

        This means that when a metadata file overrides the docker repository and version of the image,
        the registry entry needs to be written to a different path than the metadata file.

        *But only in the case that its a versioned path and NOT a latest path.*

        Example:
        If metadata file for source-posgres is at version 2.0.0 but there is a override for the cloud registry
        that changes the docker repository to source-postgres-strict-encrypt and the version to 1.0.0

        Then we will have a metadata file written to:
        gs://my-bucket/metadata/source-postgres/2.0.0/metadata.yaml

        and registry entries written to:
        gs://my-bucket/metadata/source-postgres/2.0.0/oss.json
        gs://my-bucket/metadata/source-postgres-strict-encrypt/1.0.0/cloud.json

        But if the metadata file is written to a latest path, then the registry entry will be written to the same path:
        gs://my-bucket/metadata/source-postgres/latest/oss.json
        gs://my-bucket/metadata/source-postgres/latest/cloud.json

        Future Solution:
        To resolve this properly we need to
        1. Separate the save paths for metadata files and registry entries
        2. Have the paths determined by definitionId and a metadata version
        3. Allow for references to other metadata files in the metadata file instead of overrides

    Args:
        registry_entry (PolymorphicRegistryEntry): The registry entry to write
        registry_name (str): The name of the registry entry (oss or cloud)

    Returns:
        str: The registry entry write path corresponding to the registry entry
    """
    overrode_registry_entry_version_write_path = _get_version_specific_registry_entry_file_path(registry_entry, registry_name)
    _check_for_invalid_write_path(overrode_registry_entry_version_write_path)
    return overrode_registry_entry_version_write_path


def sanitize_docker_repo_name_for_dependency_file(docker_repo_name: str) -> str:
    """
    Remove the "airbyte/" prefix from the docker repository name.

    e.g. airbyte/source-postgres -> source-postgres

    Problem:
        The dependency file paths are based on the docker repository name without the "airbyte/" prefix where as all other
        paths are based on the full docker repository name.

        e.g. https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/connector_dependencies/source-pokeapi/0.2.0/dependencies.json

    Long term solution:
        Move the dependency file paths to be based on the full docker repository name.

    Args:
        docker_repo_name (str): The docker repository name

    Returns:
        str: The docker repository name without the "airbyte/" prefix
    """

    return docker_repo_name.replace("airbyte/", "")


def get_airbyte_slack_users_from_graph(context: OpExecutionContext) -> Optional[pd.DataFrame]:
    """
    Get the airbyte slack users from the graph.

    Important: Directly relates to the airbyte_slack_users asset. Requires the asset to be materialized in the graph.

    Problem:
        I guess having dynamic partitioned assets that automatically materialize depending on another asset is a bit too much to ask for.

    Solution:
        Just get the asset from the graph, but dont declare it as a dependency.

    Context:
        https://airbytehq-team.slack.com/archives/C048P9GADFW/p1715276222825929
    """
    try:
        from orchestrator import defn

        airbyte_slack_users = defn.load_asset_value("airbyte_slack_users", instance=context.instance)
        context.log.info(f"Got airbyte slack users from graph: {airbyte_slack_users}")
        return airbyte_slack_users
    except Exception as e:
        context.log.error(f"Failed to get airbyte slack users from graph: {e}")
        return None
