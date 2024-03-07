#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import hashlib
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import dagger
import docker  # type: ignore
import pytest
from airbyte_protocol.models import ConfiguredAirbyteCatalog  # type: ignore
from live_tests.commons.models import Command, ConnectorUnderTest, ExecutionResult, SecretDict


async def get_container_from_id(dagger_client: dagger.Client, container_id: str) -> dagger.Container:
    """Get a dagger container from its id.
    Please remind that container id are not persistent and can change between Dagger sessions.

    Args:
        dagger_client (dagger.Client): The dagger client to use to import the connector image
    """
    try:
        return await dagger_client.container(id=dagger.ContainerID(container_id))
    except dagger.DaggerError as e:
        pytest.exit(f"Failed to load connector container: {e}")


async def get_container_from_tarball_path(dagger_client: dagger.Client, tarball_path: Path):
    if not tarball_path.exists():
        pytest.exit(f"Connector image tarball {tarball_path} does not exist")
    container_under_test_tar_file = (
        dagger_client.host().directory(str(tarball_path.parent), include=tarball_path.name).file(tarball_path.name)
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
    connector_container_id_path = Path("/tmp/container_id.txt")
    if connector_container_id_path.exists():
        # If the CONNECTOR_CONTAINER_ID env var is set, we'll use it to load the connector container
        return await get_container_from_id(dagger_client, connector_container_id_path.read_text())

    # If the CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH env var is set, we'll use it to import the connector image from the tarball
    if connector_image_tarball_path := os.environ.get("CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH"):
        tarball_path = Path(connector_image_tarball_path)
        return await get_container_from_tarball_path(dagger_client, tarball_path)

    # Let's try to load the connector container from a local image
    if connector_container := await get_container_from_local_image(dagger_client, image_name_with_tag):
        return connector_container

    # If we get here, we'll try to pull the connector image from DockerHub
    return await get_container_from_dockerhub_image(dagger_client, image_name_with_tag)


class ConnectorRunner:
    IN_CONTAINER_CONFIG_PATH = "/data/config.json"
    IN_CONTAINER_CATALOG_PATH = "/data/catalog.json"
    IN_CONTAINER_STATE_PATH = "/data/state.json"
    MITMPROXY_IMAGE = "mitmproxy/mitmproxy:9.0.1"
    HTTP_DUMP_FILE_NAME = "http_dump.mitm"

    def __init__(
        self,
        dagger_client: dagger.Client,
        connector_under_test: ConnectorUnderTest,
        command: Command,
        config: Optional[SecretDict] = None,
        catalog: Optional[ConfiguredAirbyteCatalog] = None,
        state: Optional[Dict] = None,
        environment_variables: Optional[Dict] = None,
        enable_http_cache: bool = True,
    ):
        self.dagger_client = dagger_client
        self.connector_under_test = connector_under_test
        self.command = command
        self.config = config
        self.catalog = catalog
        self.state = state
        self.environment_variables = environment_variables if environment_variables else {}
        self.enable_http_cache = enable_http_cache
        self.full_command: List[str] = self._get_full_command(command)

    @property
    def _connector_under_test_container(self) -> dagger.Container:
        return self.connector_under_test.container

    def _get_full_command(self, command: Command):
        if command is Command.SPEC:
            return ["spec"]
        elif command is Command.CHECK:
            return ["check", "--config", self.IN_CONTAINER_CONFIG_PATH]
        elif command is Command.DISCOVER:
            return ["discover", "--config", self.IN_CONTAINER_CONFIG_PATH]
        elif command is Command.READ:
            return [
                "read",
                "--config",
                self.IN_CONTAINER_CONFIG_PATH,
                "--catalog",
                self.IN_CONTAINER_CATALOG_PATH,
            ]
        elif command is Command.READ_WITH_STATE:
            return [
                "read",
                "--config",
                self.IN_CONTAINER_CONFIG_PATH,
                "--catalog",
                self.IN_CONTAINER_CATALOG_PATH,
                "--state",
                self.IN_CONTAINER_STATE_PATH,
            ]
        else:
            raise NotImplementedError(f"The connector runner does not support the {command} command")

    async def get_container_env_variable_value(self, name: str) -> Optional[str]:
        return await self._connector_under_test_container.env_variable(name)

    async def get_container_label(self, label: str):
        return await self._connector_under_test_container.label(label)

    async def get_container_entrypoint(self):
        entrypoint = await self._connector_under_test_container.entrypoint()
        return " ".join(entrypoint)

    async def run(
        self,
        raise_on_container_error: bool = True,
    ) -> ExecutionResult:
        container = self._connector_under_test_container
        # Do not cache downstream dagger layers
        container = container.with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
        for env_var_name, env_var_value in self.environment_variables.items():
            container = container.with_env_variable(env_var_name, env_var_value)
        if self.config:
            container = container.with_new_file(self.IN_CONTAINER_CONFIG_PATH, contents=json.dumps(dict(self.config)))
        if self.state:
            container = container.with_new_file(self.IN_CONTAINER_STATE_PATH, contents=json.dumps(self.state))
        if self.catalog:
            container = container.with_new_file(self.IN_CONTAINER_CATALOG_PATH, contents=self.catalog.json())
        if self.enable_http_cache:
            container = await self._bind_connector_container_to_proxy(container)
        executed_container = await container.with_exec(self.full_command).sync()

        return ExecutionResult(
            stdout=await executed_container.stdout(),
            stderr=await executed_container.stderr(),
            executed_container=executed_container,
            http_dump=await self._retrieve_http_dump() if self.enable_http_cache else None,
        )

    def _get_http_dumps_cache_volume(self) -> dagger.CacheVolume:
        config_data = self.config.data if self.config else None
        proxy_cache_key = hashlib.md5((self.connector_under_test.name + str(config_data)).encode("utf-8")).hexdigest()
        return self.dagger_client.cache_volume(f"{self.MITMPROXY_IMAGE}{proxy_cache_key}")

    def _get_mitmproxy_dir_cache(self) -> dagger.CacheVolume:
        return self.dagger_client.cache_volume(self.MITMPROXY_IMAGE)

    async def _get_proxy_container(
        self,
    ) -> dagger.Container:
        proxy_container = (
            self.dagger_client.container()
            .from_(self.MITMPROXY_IMAGE)
            .with_exec(["mkdir", "-p", "/home/mitmproxy/.mitmproxy"], skip_entrypoint=True)
            .with_mounted_cache("/dumps", self._get_http_dumps_cache_volume())
            .with_mounted_cache("/home/mitmproxy/.mitmproxy", self._get_mitmproxy_dir_cache())
        )
        previous_dump_files = (
            await proxy_container.with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_exec(["ls", "/dumps"], skip_entrypoint=True)
            .stdout()
        ).splitlines()
        if self.HTTP_DUMP_FILE_NAME in previous_dump_files:
            command = [
                "mitmweb",
                "--server-replay",
                f"/dumps/{self.HTTP_DUMP_FILE_NAME}",
            ]
        else:
            command = [
                "mitmweb",
                "--save-stream-file",
                f"/dumps/{self.HTTP_DUMP_FILE_NAME}",
            ]

        return proxy_container.with_exec(command)

    async def _bind_connector_container_to_proxy(self, container: dagger.Container):
        proxy_srv = await self._get_proxy_container()
        proxy_host, proxy_port = "proxy_server", 8080
        cert_path_in_volume = "/mitmproxy_dir/mitmproxy-ca.pem"
        requests_cert_path = "/usr/local/lib/python3.9/site-packages/certifi/cacert.pem"
        ca_certificate_path = "/usr/local/share/ca-certificates/mitmproxy.crt"

        return (
            container.with_service_binding(proxy_host, proxy_srv.with_exposed_port(proxy_port).as_service())
            .with_mounted_cache("/mitmproxy_dir", self._get_mitmproxy_dir_cache())
            .with_exec(["cp", cert_path_in_volume, requests_cert_path], skip_entrypoint=True)
            .with_exec(["cp", cert_path_in_volume, ca_certificate_path], skip_entrypoint=True)
            .with_env_variable("REQUESTS_CA_BUNDLE", requests_cert_path)
            .with_exec(["update-ca-certificates"], skip_entrypoint=True)
            .with_env_variable("http_proxy", f"{proxy_host}:{proxy_port}")
            .with_env_variable("https_proxy", f"{proxy_host}:{proxy_port}")
        )

    async def _retrieve_http_dump(self) -> dagger.File:
        return await (
            self.dagger_client.container()
            .from_("alpine:latest")
            .with_mounted_cache("/dumps", self._get_http_dumps_cache_volume())
            .with_exec(["mkdir", "/to_export"])
            .with_exec(
                [
                    "cp",
                    "-r",
                    f"/dumps/{self.HTTP_DUMP_FILE_NAME}",
                    f"/to_export/{self.HTTP_DUMP_FILE_NAME}",
                ]
            )
            .file(f"/to_export/{self.HTTP_DUMP_FILE_NAME}")
        )
