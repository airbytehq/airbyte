# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Set

from connection_retriever import ConnectionObject, retrieve_objects  # type: ignore
from connection_retriever.errors import NotPermittedError  # type: ignore

from .models import AirbyteCatalog, Command, ConfiguredAirbyteCatalog, ConnectionObjects, SecretDict

LOGGER = logging.getLogger(__name__)


def parse_config(config: Dict | str | None) -> Optional[SecretDict]:
    if not config:
        return None
    if isinstance(config, str):
        return SecretDict(json.loads(config))
    else:
        return SecretDict(config)


def parse_catalog(catalog: Dict | str | None) -> Optional[AirbyteCatalog]:
    if not catalog:
        return None
    if isinstance(catalog, str):
        return AirbyteCatalog.parse_obj(json.loads(catalog))
    else:
        return AirbyteCatalog.parse_obj(catalog)


def parse_configured_catalog(
    configured_catalog: Dict | str | None,
) -> Optional[ConfiguredAirbyteCatalog]:
    if not configured_catalog:
        return None
    if isinstance(configured_catalog, str):
        return ConfiguredAirbyteCatalog.parse_obj(json.loads(configured_catalog))
    else:
        return ConfiguredAirbyteCatalog.parse_obj(configured_catalog)


def parse_state(state: Dict | str | None) -> Optional[Dict]:
    if not state:
        return None
    if isinstance(state, str):
        return json.loads(state)
    else:
        return state


def get_connector_config_from_path(config_path: Path) -> Optional[SecretDict]:
    return parse_config(config_path.read_text())


def get_state_from_path(state_path: Path) -> Optional[Dict]:
    return parse_state(state_path.read_text())


def get_configured_catalog_from_path(path: Path) -> Optional[ConfiguredAirbyteCatalog]:
    return parse_configured_catalog(path.read_text())


COMMAND_TO_REQUIRED_OBJECT_TYPES = {
    Command.SPEC: set(),
    Command.CHECK: {ConnectionObject.SOURCE_CONFIG},
    Command.DISCOVER: {ConnectionObject.SOURCE_CONFIG},
    Command.READ: {ConnectionObject.SOURCE_CONFIG, ConnectionObject.CONFIGURED_CATALOG},
    Command.READ_WITH_STATE: {
        ConnectionObject.SOURCE_CONFIG,
        ConnectionObject.CONFIGURED_CATALOG,
        ConnectionObject.STATE,
    },
}


def get_connection_objects(
    requested_objects: Set[ConnectionObject],
    connection_id: Optional[str],
    custom_config_path: Optional[Path],
    custom_configured_catalog_path: Optional[Path],
    custom_state_path: Optional[Path],
    retrieval_reason: Optional[str],
    fail_if_missing_objects: bool = True,
    connector_image: Optional[str] = None,
) -> ConnectionObjects:
    """This function retrieves the connection objects values.
    It checks that the required objects are available and raises a UsageError if they are not.
    If a connection_id is provided, it retrieves the connection objects from the connection.
    If custom objects are provided, it overrides the retrieved objects with them.

    Args:
        requested_objects (Set[ConnectionObject]): The set of requested connection objects.
        connection_id (Optional[str]): The connection id to retrieve the connection objects for.
        custom_config_path (Optional[Path]): The local path to the custom config to use.
        custom_configured_catalog_path (Optional[Path]): The local path to the custom catalog to use.
        custom_state_path (Optional[Path]): The local path to the custom state to use.
        retrieval_reason (Optional[str]): The reason to access the connection objects.
        fail_if_missing_objects (bool, optional): Whether to raise a ValueError if a required object is missing. Defaults to True.
        connector_image (Optional[str]): The image name for the connector under test.
    Raises:
        click.UsageError: If a required object is missing for the command.
        click.UsageError: If a retrieval reason is missing when passing a connection id.
    Returns:
        ConnectionObjects: The connection objects values.
    """

    custom_config = get_connector_config_from_path(custom_config_path) if custom_config_path else None
    custom_configured_catalog = get_configured_catalog_from_path(custom_configured_catalog_path) if custom_configured_catalog_path else None
    custom_state = get_state_from_path(custom_state_path) if custom_state_path else None

    if not connection_id:
        connection_object = ConnectionObjects(
            source_config=custom_config,
            destination_config=custom_config,
            catalog=None,
            configured_catalog=custom_configured_catalog,
            state=custom_state,
            workspace_id=None,
            source_id=None,
            destination_id=None,
        )
    else:
        if not retrieval_reason:
            raise ValueError("A retrieval reason is required to access the connection objects when passing a connection id.")
        retrieved_objects = retrieve_objects(connection_id, requested_objects, retrieval_reason=retrieval_reason)
        retrieved_source_config = parse_config(retrieved_objects.get(ConnectionObject.SOURCE_CONFIG))
        rerieved_destination_config = parse_config(retrieved_objects.get(ConnectionObject.DESTINATION_CONFIG))
        retrieved_catalog = parse_catalog(retrieved_objects.get(ConnectionObject.CATALOG))
        retrieved_configured_catalog = parse_configured_catalog(retrieved_objects.get(ConnectionObject.CONFIGURED_CATALOG))
        retrieved_state = parse_state(retrieved_objects.get(ConnectionObject.STATE))

        retrieved_source_docker_image = retrieved_objects.get(ConnectionObject.SOURCE_DOCKER_IMAGE)
        if retrieved_source_docker_image is None:
            raise ValueError(f"A docker image was not found for connection ID {connection_id}.")
        elif retrieved_source_docker_image.split(":")[0] != connector_image:
            raise NotPermittedError(
                f"The provided docker image ({connector_image}) does not match the image for connection ID {connection_id}."
            )

        connection_object = ConnectionObjects(
            source_config=custom_config if custom_config else retrieved_source_config,
            destination_config=custom_config if custom_config else rerieved_destination_config,
            catalog=retrieved_catalog,
            configured_catalog=custom_configured_catalog if custom_configured_catalog else retrieved_configured_catalog,
            state=custom_state if custom_state else retrieved_state,
            workspace_id=retrieved_objects.get(ConnectionObject.WORKSPACE_ID),
            source_id=retrieved_objects.get(ConnectionObject.SOURCE_ID),
            destination_id=retrieved_objects.get(ConnectionObject.DESTINATION_ID),
        )
    if fail_if_missing_objects:
        if not connection_object.source_config and ConnectionObject.SOURCE_CONFIG in requested_objects:
            raise ValueError("A source config is required to run the command.")
        if not connection_object.catalog and ConnectionObject.CONFIGURED_CATALOG in requested_objects:
            raise ValueError("A catalog is required to run the command.")
        if not connection_object.state and ConnectionObject.STATE in requested_objects:
            raise ValueError("A state is required to run the command.")
    return connection_object
