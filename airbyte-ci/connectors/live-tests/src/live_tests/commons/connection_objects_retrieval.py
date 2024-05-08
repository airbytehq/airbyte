# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Set

import rich
from connection_retriever import ConnectionObject, retrieve_objects  # type: ignore
from connection_retriever.errors import NotPermittedError  # type: ignore

from .models import AirbyteCatalog, Command, ConfiguredAirbyteCatalog, ConnectionObjects, SecretDict

LOGGER = logging.getLogger(__name__)
console = rich.get_console()


def parse_config(config: dict | str | None) -> Optional[SecretDict]:
    if not config:
        return None
    if isinstance(config, str):
        return SecretDict(json.loads(config))
    else:
        return SecretDict(config)


def parse_catalog(catalog: dict | str | None) -> Optional[AirbyteCatalog]:
    if not catalog:
        return None
    if isinstance(catalog, str):
        return AirbyteCatalog.parse_obj(json.loads(catalog))
    else:
        return AirbyteCatalog.parse_obj(catalog)


def parse_configured_catalog(
    configured_catalog: dict | str | None, selected_streams: set[str] | None = None
) -> Optional[ConfiguredAirbyteCatalog]:
    if not configured_catalog:
        return None
    if isinstance(configured_catalog, str):
        catalog = ConfiguredAirbyteCatalog.parse_obj(json.loads(configured_catalog))
    else:
        catalog = ConfiguredAirbyteCatalog.parse_obj(configured_catalog)
    if selected_streams:
        return ConfiguredAirbyteCatalog(streams=[stream for stream in catalog.streams if stream.stream.name in selected_streams])
    return catalog


def parse_state(state: dict | str | None) -> Optional[dict]:
    if not state:
        return None
    if isinstance(state, str):
        return json.loads(state)
    else:
        return state


def get_connector_config_from_path(config_path: Path) -> Optional[SecretDict]:
    return parse_config(config_path.read_text())


def get_state_from_path(state_path: Path) -> Optional[dict]:
    return parse_state(state_path.read_text())


def get_configured_catalog_from_path(path: Path, selected_streams: Optional[set[str]] = None) -> Optional[ConfiguredAirbyteCatalog]:
    return parse_configured_catalog(path.read_text(), selected_streams)


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
    requested_objects: set[ConnectionObject],
    connection_id: Optional[str],
    custom_config_path: Optional[Path],
    custom_configured_catalog_path: Optional[Path],
    custom_state_path: Optional[Path],
    retrieval_reason: Optional[str],
    fail_if_missing_objects: bool = True,
    connector_image: Optional[str] = None,
    auto_select_connection: bool = False,
    selected_streams: Optional[set[str]] = None,
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
        auto_select_connection (bool, optional): Whether to automatically select a connection if no connection id is passed. Defaults to False.
        selected_streams (Optional[Set[str]]): The set of selected streams to use when auto selecting a connection.
    Raises:
        click.UsageError: If a required object is missing for the command.
        click.UsageError: If a retrieval reason is missing when passing a connection id.
    Returns:
        ConnectionObjects: The connection objects values.
    """
    if connection_id and auto_select_connection:
        raise ValueError("Cannot set both `connection_id` and `auto_select_connection`.")
    if auto_select_connection and not connector_image:
        raise ValueError("A connector image must be provided when using auto_select_connection.")

    custom_config = get_connector_config_from_path(custom_config_path) if custom_config_path else None
    custom_configured_catalog = (
        get_configured_catalog_from_path(custom_configured_catalog_path, selected_streams) if custom_configured_catalog_path else None
    )
    custom_state = get_state_from_path(custom_state_path) if custom_state_path else None
    is_ci = os.getenv("CI", False)

    if connection_id:
        if not retrieval_reason:
            raise ValueError("A retrieval reason is required to access the connection objects when passing a connection id.")

        connection_object = _get_connection_objects_from_retrieved_objects(
            requested_objects,
            retrieval_reason=retrieval_reason,
            source_docker_repository=connector_image,
            prompt_for_connection_selection=False,
            selected_streams=selected_streams,
            connection_id=connection_id,
            custom_config=custom_config,
            custom_configured_catalog=custom_configured_catalog,
            custom_state=custom_state,
        )

    else:
        if auto_select_connection:
            connection_object = _get_connection_objects_from_retrieved_objects(
                requested_objects,
                retrieval_reason=retrieval_reason,
                source_docker_repository=connector_image,
                prompt_for_connection_selection=not is_ci,
                selected_streams=selected_streams,
                custom_config=custom_config,
                custom_configured_catalog=custom_configured_catalog,
                custom_state=custom_state,
            )

        else:
            # We don't make any requests to the connection-retriever; it is expected that config/catalog/state have been provided if needed for the commands being run.
            connection_object = ConnectionObjects(
                source_config=custom_config,
                destination_config=custom_config,
                catalog=None,
                configured_catalog=custom_configured_catalog,
                state=custom_state,
                workspace_id=None,
                source_id=None,
                destination_id=None,
                connection_id=None,
                source_docker_image=None,
            )

    if fail_if_missing_objects:
        if not connection_object.source_config and ConnectionObject.SOURCE_CONFIG in requested_objects:
            raise ValueError("A source config is required to run the command.")
        if not connection_object.catalog and ConnectionObject.CONFIGURED_CATALOG in requested_objects:
            raise ValueError("A catalog is required to run the command.")
        if not connection_object.state and ConnectionObject.STATE in requested_objects:
            raise ValueError("A state is required to run the command.")
    return connection_object


def _get_connection_objects_from_retrieved_objects(
    requested_objects: Set[ConnectionObject],
    retrieval_reason: str,
    source_docker_repository: str,
    prompt_for_connection_selection: bool,
    selected_streams: Optional[Set[str]],
    connection_id: Optional[str] = None,
    custom_config: Optional[Dict] = None,
    custom_configured_catalog: Optional[ConfiguredAirbyteCatalog] = None,
    custom_state: Optional[Dict] = None,
):
    LOGGER.info("Retrieving connection objects from the database...")
    connection_id, retrieved_objects = retrieve_objects(
        requested_objects,
        retrieval_reason=retrieval_reason,
        source_docker_repository=source_docker_repository,
        prompt_for_connection_selection=prompt_for_connection_selection,
        with_streams=selected_streams,
        connection_id=connection_id,
    )

    retrieved_source_config = parse_config(retrieved_objects.get(ConnectionObject.SOURCE_CONFIG))
    retrieved_destination_config = parse_config(retrieved_objects.get(ConnectionObject.DESTINATION_CONFIG))
    retrieved_catalog = parse_catalog(retrieved_objects.get(ConnectionObject.CATALOG))
    retrieved_configured_catalog = parse_configured_catalog(retrieved_objects.get(ConnectionObject.CONFIGURED_CATALOG), selected_streams)
    retrieved_state = parse_state(retrieved_objects.get(ConnectionObject.STATE))

    retrieved_source_docker_image = retrieved_objects.get(ConnectionObject.SOURCE_DOCKER_IMAGE)
    if retrieved_source_docker_image is None:
        raise ValueError(f"A docker image was not found for connection ID {connection_id}.")
    elif retrieved_source_docker_image.split(":")[0] != source_docker_repository:
        raise NotPermittedError(
            f"The provided docker image ({source_docker_repository}) does not match the image for connection ID {connection_id}."
        )

    return ConnectionObjects(
        source_config=custom_config if custom_config else retrieved_source_config,
        destination_config=custom_config if custom_config else retrieved_destination_config,
        catalog=retrieved_catalog,
        configured_catalog=custom_configured_catalog if custom_configured_catalog else retrieved_configured_catalog,
        state=custom_state if custom_state else retrieved_state,
        workspace_id=retrieved_objects.get(ConnectionObject.WORKSPACE_ID),
        source_id=retrieved_objects.get(ConnectionObject.SOURCE_ID),
        destination_id=retrieved_objects.get(ConnectionObject.DESTINATION_ID),
        source_docker_image=retrieved_source_docker_image,
        connection_id=connection_id,
    )
