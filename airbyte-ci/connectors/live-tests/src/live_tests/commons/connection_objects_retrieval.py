# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import rich
from connection_retriever import ConnectionObject, retrieve_objects  # type: ignore
from connection_retriever.retrieval import TestingCandidate, retrieve_testing_candidates
from pydantic import ValidationError

from live_tests.commons import hacks
from live_tests.commons.models import ConnectionSubset
from live_tests.commons.utils import build_connection_url

from .models import AirbyteCatalog, Command, ConfiguredAirbyteCatalog, ConnectionObjects, SecretDict

console = rich.get_console()


class InvalidConnectionError(Exception):
    pass


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
        configured_catalog = json.loads(configured_catalog)
    patched_catalog = hacks.patch_configured_catalog(configured_catalog)
    catalog = ConfiguredAirbyteCatalog.parse_obj(patched_catalog)
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
    connector_image: Optional[str] = None,
    connector_version: Optional[str] = None,
    auto_select_connections: bool = False,
    selected_streams: Optional[set[str]] = None,
    connection_subset: ConnectionSubset = ConnectionSubset.SANDBOXES,
    max_connections: Optional[int] = None,
) -> List[ConnectionObjects]:
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
        connector_version (Optional[str]): The version for the connector under test.
        auto_select_connections (bool, optional): Whether to automatically select connections if no connection id is passed. Defaults to False.
        selected_streams (Optional[Set[str]]): The set of selected streams to use when auto selecting a connection.
        connection_subset (ConnectionSubset): The subset of connections to select from.
        max_connections (Optional[int]): The maximum number of connections to retrieve.
    Raises:
        click.UsageError: If a required object is missing for the command.
        click.UsageError: If a retrieval reason is missing when passing a connection id.
    Returns:
        List[ConnectionObjects]: List of connection objects.
    """
    if connection_id and auto_select_connections:
        raise ValueError("Cannot set both `connection_id` and `auto_select_connections`.")
    if auto_select_connections and not connector_image:
        raise ValueError("A connector image must be provided when using auto_select_connections.")

    custom_config = get_connector_config_from_path(custom_config_path) if custom_config_path else None
    custom_configured_catalog = (
        get_configured_catalog_from_path(custom_configured_catalog_path, selected_streams) if custom_configured_catalog_path else None
    )
    custom_state = get_state_from_path(custom_state_path) if custom_state_path else None
    is_ci = os.getenv("CI", False)

    if connection_id:
        if not retrieval_reason:
            raise ValueError("A retrieval reason is required to access the connection objects when passing a connection id.")

        connection_objects = _get_connection_objects_from_retrieved_objects(
            requested_objects,
            retrieval_reason=retrieval_reason,
            source_docker_repository=connector_image,
            source_docker_image_tag=connector_version,
            selected_streams=selected_streams,
            connection_id=connection_id,
            custom_config=custom_config,
            custom_configured_catalog=custom_configured_catalog,
            custom_state=custom_state,
            connection_subset=connection_subset,
            max_connections=max_connections,
        )

    else:
        if auto_select_connections:
            connection_objects = _get_connection_objects_from_retrieved_objects(
                requested_objects,
                retrieval_reason=retrieval_reason,
                source_docker_repository=connector_image,
                source_docker_image_tag=connector_version,
                selected_streams=selected_streams,
                custom_config=custom_config,
                custom_configured_catalog=custom_configured_catalog,
                custom_state=custom_state,
                connection_subset=connection_subset,
                max_connections=max_connections,
            )

        else:
            # We don't make any requests to the connection-retriever; it is expected that config/catalog/state have been provided if needed for the commands being run.
            connection_objects = [
                ConnectionObjects(
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
            ]
    if not connection_objects:
        raise ValueError("No connection objects could be fetched.")

    all_connection_ids = [connection_object.connection_id for connection_object in connection_objects]
    assert len(set(all_connection_ids)) == len(all_connection_ids), "Connection IDs must be unique."
    return connection_objects


def _find_best_candidates_subset(candidates: List[TestingCandidate]) -> List[Tuple[TestingCandidate, List[str]]]:
    """
    This function reduces the list of candidates to the best subset of candidates.
    The best subset is the one which maximizes the number of streams tested and minimizes the number of candidates.
    """
    candidates_sorted_by_duration = sorted(candidates, key=lambda x: x.last_attempt_duration_in_microseconds)

    tested_streams = set()
    candidates_and_streams_to_test = []

    for candidate in candidates_sorted_by_duration:
        candidate_streams_to_test = []
        for stream in candidate.streams_with_data:
            # The candidate is selected if one of its streams has not been tested yet
            if stream not in tested_streams:
                candidate_streams_to_test.append(stream)
                tested_streams.add(stream)
        if candidate_streams_to_test:
            candidates_and_streams_to_test.append((candidate, candidate_streams_to_test))
    return candidates_and_streams_to_test


def _get_connection_objects_from_retrieved_objects(
    requested_objects: Set[ConnectionObject],
    retrieval_reason: str,
    source_docker_repository: str,
    source_docker_image_tag: str,
    selected_streams: Optional[Set[str]],
    connection_id: Optional[str] = None,
    custom_config: Optional[Dict] = None,
    custom_configured_catalog: Optional[ConfiguredAirbyteCatalog] = None,
    custom_state: Optional[Dict] = None,
    connection_subset: ConnectionSubset = ConnectionSubset.SANDBOXES,
    max_connections: Optional[int] = None,
):
    console.log(
        textwrap.dedent(
            """
        Retrieving connection objects from the database. 
        We will build a subset of candidates to test. 
        This subset should minimize the number of candidates and sync duration while maximizing the number of streams tested. 
        We patch configured catalogs to only test streams once.
        If the max_connections parameter is set, we will only keep the top connections with the most streams to test.
        """
        )
    )
    try:
        candidates = retrieve_testing_candidates(
            source_docker_repository=source_docker_repository,
            source_docker_image_tag=source_docker_image_tag,
            with_streams=selected_streams,
            connection_subset=connection_subset,
        )
    except IndexError:
        raise InvalidConnectionError(
            f"No candidates were found for the provided source docker image ({source_docker_repository}:{source_docker_image_tag})."
        )
    # If the connection_id is provided, we filter the candidates to only keep the ones with the same connection_id
    if connection_id:
        candidates = [candidate for candidate in candidates if candidate.connection_id == connection_id]

    candidates_and_streams_to_test = _find_best_candidates_subset(candidates)
    candidates_and_streams_to_test = sorted(candidates_and_streams_to_test, key=lambda x: len(x[1]), reverse=True)
    if max_connections:
        candidates_and_streams_to_test = candidates_and_streams_to_test[:max_connections]

    number_of_streams_tested = sum([len(streams_to_test) for _, streams_to_test in candidates_and_streams_to_test])
    console.log(f"Selected {len(candidates_and_streams_to_test)} candidates to test {number_of_streams_tested} streams.")

    all_connection_objects = []
    for candidate, streams_to_test in candidates_and_streams_to_test:
        retrieved_objects = retrieve_objects(
            requested_objects,
            retrieval_reason=retrieval_reason,
            source_docker_repository=source_docker_repository,
            source_docker_image_tag=source_docker_image_tag,
            connection_id=candidate.connection_id,
            connection_subset=connection_subset,
        )
        retrieved_objects = retrieved_objects[0]
        retrieved_source_config = parse_config(retrieved_objects.source_config)
        retrieved_destination_config = parse_config(retrieved_objects.destination_config)
        retrieved_catalog = parse_catalog(retrieved_objects.catalog)
        retrieved_configured_catalog = parse_configured_catalog(retrieved_objects.configured_catalog, streams_to_test)
        retrieved_state = parse_state(retrieved_objects.state)

        retrieved_source_docker_image = retrieved_objects.source_docker_image
        connection_url = build_connection_url(retrieved_objects.workspace_id, retrieved_objects.connection_id)
        if retrieved_source_docker_image is None:
            raise InvalidConnectionError(
                f"No docker image was found for connection ID {retrieved_objects.connection_id}. Please double check that the latest job run used version {source_docker_image_tag}. Connection URL: {connection_url}"
            )
        elif retrieved_source_docker_image.split(":")[0] != source_docker_repository:
            raise InvalidConnectionError(
                f"The provided docker image ({source_docker_repository}) does not match the image for connection ID {retrieved_objects.connection_id}. Please double check that this connection is using the correct image. Connection URL: {connection_url}"
            )
        elif retrieved_source_docker_image.split(":")[1] != source_docker_image_tag:
            raise InvalidConnectionError(
                f"The provided docker image tag ({source_docker_image_tag}) does not match the image tag for connection ID {retrieved_objects.connection_id}. Please double check that this connection is using the correct image tag and the latest job ran using this version. Connection URL: {connection_url}"
            )

        all_connection_objects.append(
            ConnectionObjects(
                source_config=custom_config if custom_config else retrieved_source_config,
                destination_config=custom_config if custom_config else retrieved_destination_config,
                catalog=retrieved_catalog,
                configured_catalog=custom_configured_catalog if custom_configured_catalog else retrieved_configured_catalog,
                state=custom_state if custom_state else retrieved_state,
                workspace_id=retrieved_objects.workspace_id,
                source_id=retrieved_objects.source_id,
                destination_id=retrieved_objects.destination_id,
                source_docker_image=retrieved_source_docker_image,
                connection_id=retrieved_objects.connection_id,
            )
        )
    return all_connection_objects
