# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import logging
import os
import re
import shutil
from pathlib import Path
from typing import Optional

import dagger
import docker  # type: ignore
import pytest
from mitmproxy import http, io  # type: ignore
from mitmproxy.addons.savehar import SaveHar  # type: ignore
from slugify import slugify


async def get_container_from_id(dagger_client: dagger.Client, container_id: str) -> dagger.Container:
    """Get a dagger container from its id.
    Please remind that container id are not persistent and can change between Dagger sessions.

    Args:
        dagger_client (dagger.Client): The dagger client to use to import the connector image
    """
    try:
        return await dagger_client.load_container_from_id(dagger.ContainerID(container_id))
    except dagger.DaggerError as e:
        pytest.exit(f"Failed to load connector container: {e}")


async def get_container_from_tarball_path(dagger_client: dagger.Client, tarball_path: Path) -> dagger.Container:
    if not tarball_path.exists():
        pytest.exit(f"Connector image tarball {tarball_path} does not exist")
    container_under_test_tar_file = (
        dagger_client.host().directory(str(tarball_path.parent), include=[tarball_path.name]).file(tarball_path.name)
    )
    try:
        return await dagger_client.container().import_(container_under_test_tar_file)
    except dagger.DaggerError as e:
        pytest.exit(f"Failed to import connector image from tarball: {e}")


async def get_container_from_local_image(dagger_client: dagger.Client, local_image_name: str) -> Optional[dagger.Container]:
    """Get a dagger container from a local image.
    It will use Docker python client to export the image to a tarball and then import it into dagger.

    Args:
        dagger_client (dagger.Client): The dagger client to use to import the connector image
        local_image_name (str): The name of the local image to import

    Returns:
        Optional[dagger.Container]: The dagger container for the local image or None if the image does not exist
    """
    docker_client = docker.from_env()

    try:
        image = docker_client.images.get(local_image_name)
    except docker.errors.ImageNotFound:
        return None

    image_digest = image.id.replace("sha256:", "")
    tarball_path = Path(f"/tmp/{image_digest}.tar")
    if not tarball_path.exists():
        logging.info(f"Exporting local connector image {local_image_name} to tarball {tarball_path}")
        with open(tarball_path, "wb") as f:
            for chunk in image.save(named=True):
                f.write(chunk)
    return await get_container_from_tarball_path(dagger_client, tarball_path)


async def get_container_from_dockerhub_image(dagger_client: dagger.Client, dockerhub_image_name: str) -> dagger.Container:
    """Get a dagger container from a dockerhub image.

    Args:
        dagger_client (dagger.Client): The dagger client to use to import the connector image
        dockerhub_image_name (str): The name of the dockerhub image to import

    Returns:
        dagger.Container: The dagger container for the dockerhub image
    """
    try:
        return await dagger_client.container().from_(dockerhub_image_name)
    except dagger.DaggerError as e:
        pytest.exit(f"Failed to import connector image from DockerHub: {e}")


async def get_connector_container(dagger_client: dagger.Client, image_name_with_tag: str) -> dagger.Container:
    """Get a dagger container for the connector image to test.

    Args:
        dagger_client (dagger.Client): The dagger client to use to import the connector image
        image_name_with_tag (str): The docker image name and tag of the connector image to test

    Returns:
        dagger.Container: The dagger container for the connector image to test
    """
    # If a container_id.txt file is available, we'll use it to load the connector container
    # We use a txt file as container ids can be too long to be passed as env vars
    # It's used for dagger-in-dagger use case with airbyte-ci, when the connector container is built via an upstream dagger operation
    container_id_path = Path(f"/tmp/{slugify(image_name_with_tag)}_container_id.txt")
    if container_id_path.exists():
        return await get_container_from_id(dagger_client, container_id_path.read_text())

    # If the CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH env var is set, we'll use it to import the connector image from the tarball
    if connector_image_tarball_path := os.environ.get("CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH"):
        tarball_path = Path(connector_image_tarball_path)
        return await get_container_from_tarball_path(dagger_client, tarball_path)

    # Let's try to load the connector container from a local image
    if connector_container := await get_container_from_local_image(dagger_client, image_name_with_tag):
        return connector_container

    # If we get here, we'll try to pull the connector image from DockerHub
    return await get_container_from_dockerhub_image(dagger_client, image_name_with_tag)


def sh_dash_c(lines: list[str]) -> list[str]:
    """Wrap sequence of commands in shell for safe usage of dagger Container's with_exec method."""
    return ["sh", "-c", " && ".join(["set -o xtrace"] + lines)]


def clean_up_artifacts(directory: Path, logger: logging.Logger) -> None:
    if directory.exists():
        shutil.rmtree(directory)
        logger.info(f"🧹 Test artifacts cleaned up from {directory}")


def get_http_flows_from_mitm_dump(mitm_dump_path: Path) -> list[http.HTTPFlow]:
    """Get http flows from a mitmproxy dump file.

    Args:
        mitm_dump_path (Path): Path to the mitmproxy dump file.

    Returns:
        List[http.HTTPFlow]: List of http flows.
    """
    with open(mitm_dump_path, "rb") as dump_file:
        return [f for f in io.FlowReader(dump_file).stream() if isinstance(f, http.HTTPFlow)]


def mitm_http_stream_to_har(mitm_http_stream_path: Path, har_file_path: Path) -> Path:
    """Converts a mitmproxy http stream file to a har file.

    Args:
        mitm_http_stream_path (Path): Path to the mitmproxy http stream file.
        har_file_path (Path): Path where the har file will be saved.

    Returns:
        Path: Path to the har file.
    """
    flows = get_http_flows_from_mitm_dump(mitm_http_stream_path)
    SaveHar().export_har(flows, str(har_file_path))
    return har_file_path


def extract_connection_id_from_url(url: str) -> str:
    pattern = r"/connections/([a-f0-9\-]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Could not extract connection id from url {url}")


def extract_workspace_id_from_url(url: str) -> str:
    pattern = r"/workspaces/([a-f0-9\-]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Could not extract workspace id from url {url}")


def build_connection_url(workspace_id: str | None, connection_id: str | None) -> str:
    if not workspace_id or not connection_id:
        raise ValueError("Both workspace_id and connection_id must be provided")
    return f"https://cloud.airbyte.com/workspaces/{workspace_id}/connections/{connection_id}"


def sort_dict_keys(d: dict) -> dict:
    if isinstance(d, dict):
        sorted_dict = {}
        for key in sorted(d.keys()):
            sorted_dict[key] = sort_dict_keys(d[key])
        return sorted_dict
    else:
        return d


def sanitize_stream_name(stream_name: str) -> str:
    return stream_name.replace("/", "_").replace(" ", "_").lower()
