#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
import os
import uuid
from pathlib import Path
from typing import List, Mapping, Optional, Union

import dagger
import docker
import pytest
import yaml
from airbyte_protocol.models import AirbyteMessage, ConfiguredAirbyteCatalog, OrchestratorType
from airbyte_protocol.models import Type as AirbyteMessageType
from anyio import Path as AnyioPath
from connector_acceptance_test.utils import SecretDict
from pydantic import ValidationError


class ConnectorRunner:
    IN_CONTAINER_CONFIG_PATH = "/data/config.json"
    IN_CONTAINER_CATALOG_PATH = "/data/catalog.json"
    IN_CONTAINER_STATE_PATH = "/data/state.json"
    IN_CONTAINER_OUTPUT_PATH = "/output.txt"

    def __init__(
        self,
        image_tag: str,
        dagger_client: dagger.Client,
        connector_configuration_path: Optional[Path] = None,
        custom_environment_variables: Optional[Mapping] = {},
        deployment_mode: Optional[str] = None,
    ):
        self._check_connector_under_test()
        self.image_tag = image_tag
        self.dagger_client = dagger_client
        self._connector_configuration_path = connector_configuration_path
        self._custom_environment_variables = custom_environment_variables
        self._deployment_mode = deployment_mode
        connector_image_tarball_path = self._get_connector_image_tarball_path()
        self._connector_under_test_container = self._get_connector_container(connector_image_tarball_path)

    async def load_container(self):
        """This is to pre-load the container following instantiation of the class.
        This is useful to make sure that when using the connector runner fixture the costly _import is already done.
        """
        await self._connector_under_test_container.with_exec(["spec"])

    async def call_spec(self, raise_container_error=False) -> List[AirbyteMessage]:
        return await self._run(["spec"], raise_container_error)

    async def call_check(self, config: SecretDict, raise_container_error: bool = False) -> List[AirbyteMessage]:
        return await self._run(["check", "--config", self.IN_CONTAINER_CONFIG_PATH], raise_container_error, config=config)

    async def call_discover(self, config: SecretDict, raise_container_error: bool = False) -> List[AirbyteMessage]:
        return await self._run(["discover", "--config", self.IN_CONTAINER_CONFIG_PATH], raise_container_error, config=config)

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

    def _get_connector_image_tarball_path(self) -> Optional[Path]:
        if "CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH" not in os.environ and not self.image_tag.endswith(":dev"):
            return None
        if "CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH" in os.environ:
            connector_under_test_image_tar_path = Path(os.environ["CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH"])
        elif self.image_tag.endswith(":dev"):
            connector_under_test_image_tar_path = self._export_local_connector_image_to_tarball(self.image_tag)
        assert connector_under_test_image_tar_path.exists(), "Connector image tarball does not exist"
        return connector_under_test_image_tar_path

    def _export_local_connector_image_to_tarball(self, local_image_name: str) -> Optional[Path]:
        tarball_path = Path("/tmp/connector_under_test_image.tar")

        docker_client = docker.from_env()
        try:
            image = docker_client.images.get(local_image_name)
            with open(tarball_path, "wb") as f:
                for chunk in image.save(named=True):
                    f.write(chunk)

        except docker.errors.ImageNotFound:
            pytest.fail(f"Image {local_image_name} not found, please make sure to build or pull it before running the tests")
        return tarball_path

    def _get_connector_container_from_tarball(self, tarball_path: Path) -> dagger.Container:
        container_under_test_tar_file = (
            self.dagger_client.host().directory(str(tarball_path.parent), include=tarball_path.name).file(tarball_path.name)
        )
        return self.dagger_client.container().import_(container_under_test_tar_file)

    def _get_connector_container(self, connector_image_tarball_path: Optional[Path]) -> dagger.Container:
        if connector_image_tarball_path is not None:
            container = self._get_connector_container_from_tarball(connector_image_tarball_path)
        else:
            # Try to pull the image from DockerHub
            container = self.dagger_client.container().from_(self.image_tag)
        # Client might pass a cachebuster env var to force recreation of the container
        # We pass this env var to the container to ensure the cache is busted
        if cachebuster_value := os.environ.get("CACHEBUSTER"):
            container = container.with_env_variable("CACHEBUSTER", cachebuster_value)
        for key, value in self._custom_environment_variables.items():
            container = container.with_env_variable(key, str(value))
        if self._deployment_mode:
            container = container.with_env_variable("DEPLOYMENT_MODE", self._deployment_mode.upper())
        return container

    async def _run(
        self,
        airbyte_command: List[str],
        raise_container_error: bool,
        config: SecretDict = None,
        catalog: dict = None,
        state: Union[dict, list] = None,
        enable_caching=True,
    ) -> List[AirbyteMessage]:
        """_summary_

        Args:
            airbyte_command (List[str]): The command to run in the connector container.
            raise_container_error (bool): Whether to raise an error if the container fails to run the command.
            config (SecretDict, optional): The config to mount to the container. Defaults to None.
            catalog (dict, optional): The catalog to mount to the container. Defaults to None.
            state (Union[dict, list], optional): The state to mount to the container. Defaults to None.
            enable_caching (bool, optional): Whether to enable command output caching. Defaults to True.

        Raises:
            e: _description_

        Returns:
            List[AirbyteMessage]: _description_
        """
        container = self._connector_under_test_container
        if not enable_caching:
            container = container.with_env_variable("CAT_CACHEBUSTER", str(uuid.uuid4()))
        if config:
            container = container.with_new_file(self.IN_CONTAINER_CONFIG_PATH, json.dumps(dict(config)))
        if state:
            container = container.with_new_file(self.IN_CONTAINER_STATE_PATH, json.dumps(state))
        if catalog:
            container = container.with_new_file(self.IN_CONTAINER_CATALOG_PATH, catalog.json())
        for key, value in self._custom_environment_variables.items():
            container = container.with_env_variable(key, str(value))
        try:
            output = await self._read_output_from_stdout(airbyte_command, container)
        except dagger.QueryError as e:
            output_too_big = bool([error for error in e.errors if error.message.startswith("file size")])
            if output_too_big:
                output = await self._read_output_from_file(airbyte_command, container)
            elif raise_container_error:
                raise e
            else:
                if isinstance(e, dagger.ExecError):
                    output = e.stdout + e.stderr
                else:
                    pytest.fail(f"Failed to run command {airbyte_command} in container {self.image_tag} with error: {e}")
        return self.parse_airbyte_messages_from_command_output(output)

    async def _read_output_from_stdout(self, airbyte_command: list, container: dagger.Container) -> str:
        return await container.with_exec(airbyte_command).stdout()

    async def _read_output_from_file(self, airbyte_command: list, container: dagger.Container) -> str:
        local_output_file_path = f"/tmp/{str(uuid.uuid4())}"
        entrypoint = await container.entrypoint()
        airbyte_command = entrypoint + airbyte_command
        container = container.with_exec(
            ["sh", "-c", " ".join(airbyte_command) + f" > {self.IN_CONTAINER_OUTPUT_PATH} 2>&1 | tee -a {self.IN_CONTAINER_OUTPUT_PATH}"],
            skip_entrypoint=True,
        )
        await container.file(self.IN_CONTAINER_OUTPUT_PATH).export(local_output_file_path)
        output = await AnyioPath(local_output_file_path).read_text()
        await AnyioPath(local_output_file_path).unlink()
        return output

    def parse_airbyte_messages_from_command_output(self, command_output: str) -> List[AirbyteMessage]:
        airbyte_messages = []
        for line in command_output.splitlines():
            try:
                airbyte_message = AirbyteMessage.parse_raw(line)
                if airbyte_message.type is AirbyteMessageType.CONTROL and airbyte_message.control.type is OrchestratorType.CONNECTOR_CONFIG:
                    self._persist_new_configuration(airbyte_message.control.connectorConfig.config, int(airbyte_message.control.emitted_at))
                airbyte_messages.append(airbyte_message)
            except ValidationError as exc:
                logging.warning("Unable to parse connector's output %s, error: %s", line, exc)
        return airbyte_messages

    def _persist_new_configuration(self, new_configuration: dict, configuration_emitted_at: int) -> Optional[Path]:
        """Store new configuration values to an updated_configurations subdir under the original configuration path.
        N.B. The new configuration will not be stored if no configuration path was passed to the ConnectorRunner.
        Args:
            new_configuration (dict): The updated configuration
            configuration_emitted_at (int): Timestamp at which the configuration was emitted (ms)

        Returns:
            Optional[Path]: The updated configuration path if it was persisted.
        """
        if self._connector_configuration_path is None:
            logging.warning("No configuration path was passed to the ConnectorRunner. The new configuration was not persisted")
            return None

        with open(self._connector_configuration_path) as old_configuration_file:
            old_configuration = json.load(old_configuration_file)

        if new_configuration != old_configuration:
            file_prefix = self._connector_configuration_path.stem.split("|")[0]
            if "/updated_configurations/" not in str(self._connector_configuration_path):
                Path(self._connector_configuration_path.parent / "updated_configurations").mkdir(exist_ok=True)
                new_configuration_file_path = Path(
                    f"{self._connector_configuration_path.parent}/updated_configurations/{file_prefix}|{configuration_emitted_at}{self._connector_configuration_path.suffix}"
                )
            else:
                new_configuration_file_path = Path(
                    f"{self._connector_configuration_path.parent}/{file_prefix}|{configuration_emitted_at}{self._connector_configuration_path.suffix}"
                )

            with open(new_configuration_file_path, "w") as new_configuration_file:
                json.dump(new_configuration, new_configuration_file)
            logging.info(f"Stored most recent configuration value to {new_configuration_file_path}")
            return new_configuration_file_path

    def _check_connector_under_test(self):
        """
        As a safety measure, we check that the connector under test matches the connector being tested by comparing the content of the metadata.yaml file to the CONNECTOR_UNDER_TEST_TECHNICAL_NAME environment varialbe.
        When running CAT from airbyte-ci we set this CONNECTOR_UNDER_TEST_TECHNICAL_NAME env var name,
        This is a safety check to ensure the correct test inputs are mounted to the CAT container.
        """
        if connector_under_test_technical_name := os.environ.get("CONNECTOR_UNDER_TEST_TECHNICAL_NAME"):
            metadata = yaml.safe_load(Path("/test_input/metadata.yaml").read_text())
            assert metadata["data"]["dockerRepository"] == f"airbyte/{connector_under_test_technical_name}", (
                f"Connector under test env var {connector_under_test_technical_name} does not match the connector "
                f"being tested {metadata['data']['dockerRepository']}"
            )
