#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import _collections_abc
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, List, Mapping, Optional, Union

import dagger
import docker
import pytest
from airbyte_protocol.models import AirbyteMessage, ConfiguredAirbyteCatalog, OrchestratorType
from anyio import Path as AnyioPath
from pydantic import ValidationError

from live_tests.backends import BaseBackend


class UserDict(_collections_abc.MutableMapping):

    # Start by filling-out the abstract methods
    def __init__(self, dict=None, /, **kwargs):
        self.data = {}
        if dict is not None:
            self.update(dict)
        if kwargs:
            self.update(kwargs)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self.data[key] = item

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key):
        return key in self.data

    # Now, add the methods in dicts but not in MutableMapping
    def __repr__(self):
        return repr(self.data)

    def __or__(self, other):
        if isinstance(other, UserDict):
            return self.__class__(self.data | other.data)
        if isinstance(other, dict):
            return self.__class__(self.data | other)
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, UserDict):
            return self.__class__(other.data | self.data)
        if isinstance(other, dict):
            return self.__class__(other | self.data)
        return NotImplemented

    def __ior__(self, other):
        if isinstance(other, UserDict):
            self.data |= other.data
        else:
            self.data |= other
        return self

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"].copy()
        return inst

    def copy(self):
        if self.__class__ is UserDict:
            return UserDict(self.data.copy())
        import copy
        data = self.data
        try:
            self.data = {}
            c = copy.copy(self)
        finally:
            self.data = data
        c.update(self)
        return c

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d


class SecretDict(UserDict):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(******)"

    def __repr__(self) -> str:
        return str(self)


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
    BASE_IN_CONTAINER_OUTPUT_DIRECTORY = "/tmp"
    IN_CONTAINER_OUTPUT_PATH = f"{BASE_IN_CONTAINER_OUTPUT_DIRECTORY}/raw_output.txt"
    RELATIVE_ERRORS_PATH = "errors.txt"

    def __init__(
        self,
        connector_container: dagger.Container,
        backend: BaseBackend,
        output_directory: str,
        custom_environment_variables: Optional[Mapping] = None,
        deployment_mode: Optional[str] = None,
    ):
        custom_environment_variables = custom_environment_variables or {}
        env_vars = (
            custom_environment_variables
            if deployment_mode is None
            else {**custom_environment_variables, "DEPLOYMENT_MODE": deployment_mode.upper()}
        )
        self._connector_under_test_container = self.set_env_vars(connector_container, env_vars)
        self._backend = backend
        os.makedirs(self.BASE_IN_CONTAINER_OUTPUT_DIRECTORY, exist_ok=True)
        os.makedirs(output_directory, exist_ok=True)
        self._output_directory = output_directory

    def set_env_vars(self, container: dagger.Container, env_vars: Mapping[str, Any]) -> dagger.Container:
        """Set environment variables on a dagger container.

        Args:
            container (dagger.Container): The dagger container to set the environment variables on.
            env_vars (Mapping[str, str]): The environment variables to set.

        Returns:
            dagger.Container: The dagger container with the environment variables set.
        """
        for k, v in env_vars.items():
            container = container.with_env_variable(k, str(v))
        return container

    async def call_spec(self, raise_container_error=False) -> List[AirbyteMessage]:
        return await self._run(["spec"], raise_container_error)

    async def call_check(self, config: SecretDict, raise_container_error: bool = False) -> List[AirbyteMessage]:
        return await self._run(
            ["check", "--config", self.IN_CONTAINER_CONFIG_PATH],
            raise_container_error,
            config=config,
        )

    async def call_discover(self, config: SecretDict, raise_container_error: bool = False) -> List[AirbyteMessage]:
        return await self._run(
            ["discover", "--config", self.IN_CONTAINER_CONFIG_PATH],
            raise_container_error,
            config=config,
        )

    async def call_read(
        self, config: SecretDict, catalog: ConfiguredAirbyteCatalog, raise_container_error: bool = False, enable_caching: bool = True
    ) -> List[AirbyteMessage]:
        return await self._run(
            ["read", "--config", self.IN_CONTAINER_CONFIG_PATH, "--catalog", self.IN_CONTAINER_CATALOG_PATH],
            raise_container_error,
            config=config,
            catalog=catalog,
            enable_caching=enable_caching,
        )

    async def call_read_with_state(
        self,
        config: SecretDict,
        catalog: ConfiguredAirbyteCatalog,
        state: dict,
        raise_container_error: bool = False,
        enable_caching: bool = True,
    ) -> List[AirbyteMessage]:
        return await self._run(
            [
                "read",
                "--config",
                self.IN_CONTAINER_CONFIG_PATH,
                "--catalog",
                self.IN_CONTAINER_CATALOG_PATH,
                "--state",
                self.IN_CONTAINER_STATE_PATH,
            ],
            raise_container_error,
            config=config,
            catalog=catalog,
            state=state,
            enable_caching=enable_caching,
        )

    async def get_container_env_variable_value(self, name: str) -> str:
        return await self._connector_under_test_container.env_variable(name)

    async def get_container_label(self, label: str):
        return await self._connector_under_test_container.label(label)

    async def get_container_entrypoint(self):
        entrypoint = await self._connector_under_test_container.entrypoint()
        return " ".join(entrypoint)

    async def _run(
        self,
        airbyte_command: List[str],
        raise_container_error: bool,
        config: SecretDict = None,
        catalog: dict = None,
        state: Union[dict, list] = None,
        enable_caching=True,
    ) -> List[AirbyteMessage]:
        """Run a command in the connector container and return the list of AirbyteMessages emitted by the connector.

        Args:
            airbyte_command (List[str]): The command to run in the connector container.
            raise_container_error (bool): Whether to raise an error if the container fails to run the command.
            config (SecretDict, optional): The config to mount to the container. Defaults to None.
            catalog (dict, optional): The catalog to mount to the container. Defaults to None.
            state (Union[dict, list], optional): The state to mount to the container. Defaults to None.
            enable_caching (bool, optional): Whether to enable command output caching. Defaults to True.

        Returns:
            List[AirbyteMessage]: The list of AirbyteMessages emitted by the connector.
        """
        container = self._connector_under_test_container
        if not enable_caching:
            container = container.with_env_variable("CAT_CACHEBUSTER", str(uuid.uuid4()))
        if config:
            container = container.with_new_file(self.IN_CONTAINER_CONFIG_PATH, contents=json.dumps(dict(config)))
        if state:
            container = container.with_new_file(self.IN_CONTAINER_STATE_PATH, contents=json.dumps(state))
        if catalog:
            container = container.with_new_file(self.IN_CONTAINER_CATALOG_PATH, contents=catalog.json())

        await self._write_output(airbyte_command, container)

    async def _write_output(self, airbyte_command: list, container: dagger.Container):
        filename = f"raw_output.txt"
        local_output_file_path = f"{self._output_directory}/{filename}"

        entrypoint = await container.entrypoint()
        airbyte_command = entrypoint + airbyte_command
        container = container.with_exec(
            ["sh", "-c", " ".join(airbyte_command) + f" > {self.IN_CONTAINER_OUTPUT_PATH} 2>&1 | tee -a {self.IN_CONTAINER_OUTPUT_PATH}"],
            skip_entrypoint=True,
        )
        await container.file(self.IN_CONTAINER_OUTPUT_PATH).export(local_output_file_path)
        await self._write_comparable_records_and_state(local_output_file_path)

    async def _write_comparable_records_and_state(self, filepath: str):
        raw_output = await AnyioPath(filepath).read_text()
        await self._backend.write(self._raw_output_iter(raw_output))

    def _raw_output_iter(self, raw_output):
        with open(f"{self._output_directory}/{self.RELATIVE_ERRORS_PATH}", "w") as errors:
            for line in raw_output.splitlines():
                try:
                    yield AirbyteMessage.parse_raw(line)
                except ValidationError as exc:
                    errors.write(f"Unable to parse connector's output {line}, error: {exc}\n")
