#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

import docker
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, OrchestratorType
from airbyte_cdk.models import Type as AirbyteMessageType
from docker.errors import ContainerError, NotFound
from docker.models.containers import Container
from pydantic import ValidationError


class ConnectorRunner:
    def __init__(
        self,
        image_name: str,
        volume: Path,
        connector_configuration_path: Optional[Path] = None,
        custom_environment_variables: Optional[Mapping] = {},
    ):
        self._client = docker.from_env(timeout=120)
        try:
            self._image = self._client.images.get(image_name)
        except docker.errors.ImageNotFound:
            print("Pulling docker image", image_name)
            self._image = self._client.images.pull(image_name)
            print("Pulling completed")
        self._runs = 0
        self._volume_base = volume
        self._connector_configuration_path = connector_configuration_path
        self._custom_environment_variables = custom_environment_variables

    @property
    def output_folder(self) -> Path:
        return self._volume_base / f"run_{self._runs}" / "output"

    @property
    def input_folder(self) -> Path:
        return self._volume_base / f"run_{self._runs}" / "input"

    def _prepare_volumes(self, config: Optional[Mapping], state: Optional[Mapping], catalog: Optional[ConfiguredAirbyteCatalog]):
        self.input_folder.mkdir(parents=True)
        self.output_folder.mkdir(parents=True)

        # using "is not None" to allow falsey config objects like {} to still write
        if config is not None:
            with open(str(self.input_folder / "tap_config.json"), "w") as outfile:
                json.dump(dict(config), outfile)

        if state:
            with open(str(self.input_folder / "state.json"), "w") as outfile:
                if isinstance(state, List):
                    json.dump(state, outfile)
                else:
                    json.dump(dict(state), outfile)

        if catalog:
            with open(str(self.input_folder / "catalog.json"), "w") as outfile:
                outfile.write(catalog.json())

        volumes = {
            str(self.input_folder): {
                "bind": "/data",
                # "mode": "ro",
            },
            str(self.output_folder): {
                "bind": "/local",
                "mode": "rw",
            },
        }
        return volumes

    def call_spec(self, **kwargs) -> List[AirbyteMessage]:
        cmd = "spec"
        output = list(self.run(cmd=cmd, **kwargs))
        return output

    def call_check(self, config, **kwargs) -> List[AirbyteMessage]:
        cmd = "check --config /data/tap_config.json"
        output = list(self.run(cmd=cmd, config=config, **kwargs))
        return output

    def call_discover(self, config, **kwargs) -> List[AirbyteMessage]:
        cmd = "discover --config /data/tap_config.json"
        output = list(self.run(cmd=cmd, config=config, **kwargs))
        return output

    def call_read(self, config, catalog, **kwargs) -> List[AirbyteMessage]:
        cmd = "read --config /data/tap_config.json --catalog /data/catalog.json"
        output = list(self.run(cmd=cmd, config=config, catalog=catalog, **kwargs))
        return output

    def call_read_with_state(self, config, catalog, state, **kwargs) -> List[AirbyteMessage]:
        cmd = "read --config /data/tap_config.json --catalog /data/catalog.json --state /data/state.json"
        output = list(self.run(cmd=cmd, config=config, catalog=catalog, state=state, **kwargs))
        return output

    def run(self, cmd, config=None, state=None, catalog=None, raise_container_error: bool = True, **kwargs) -> Iterable[AirbyteMessage]:

        self._runs += 1
        volumes = self._prepare_volumes(config, state, catalog)
        logging.debug(f"Docker run {self._image}: \n{cmd}\n" f"input: {self.input_folder}\noutput: {self.output_folder}")

        container = self._client.containers.run(
            image=self._image,
            command=cmd,
            volumes=volumes,
            network_mode="host",
            detach=True,
            environment=self._custom_environment_variables,
            **kwargs,
        )
        with open(self.output_folder / "raw", "wb+") as f:
            for line in self.read(container, command=cmd, with_ext=raise_container_error):
                f.write(line.encode())
                try:
                    airbyte_message = AirbyteMessage.parse_raw(line)
                    if (
                        airbyte_message.type is AirbyteMessageType.CONTROL
                        and airbyte_message.control.type is OrchestratorType.CONNECTOR_CONFIG
                    ):
                        self._persist_new_configuration(
                            airbyte_message.control.connectorConfig.config, int(airbyte_message.control.emitted_at)
                        )
                    yield airbyte_message
                except ValidationError as exc:
                    logging.warning("Unable to parse connector's output %s, error: %s", line, exc)

    @classmethod
    def read(cls, container: Container, command: str = None, with_ext: bool = True) -> Iterable[str]:
        """Reads connector's logs per line"""
        buffer = b""
        exception = ""
        line = ""
        for chunk in container.logs(stdout=True, stderr=True, stream=True, follow=True):

            buffer += chunk
            while True:
                # every chunk can include several lines
                found = buffer.find(b"\n")
                if found <= -1:
                    break

                line = buffer[: found + 1].decode("utf-8")
                if len(exception) > 0 or line.startswith("Traceback (most recent call last)"):
                    exception += line
                else:
                    yield line
                buffer = buffer[found + 1 :]

        if buffer:
            # send the latest chunk if exists
            line = buffer.decode("utf-8")
            if exception:
                exception += line
            else:
                yield line
        try:
            exit_status = container.wait()
            container.remove()
        except NotFound as err:
            logging.error(f"Waiting error: {err}, logs: {exception or line}")
            raise
        if exit_status["StatusCode"]:
            error = exit_status.get("Error") or exception or line
            logging.error(f"Docker container failed, " f'code {exit_status["StatusCode"]}, error:\n{error}')
            if with_ext:
                raise ContainerError(
                    container=container,
                    exit_status=exit_status["StatusCode"],
                    command=command,
                    image=container.image,
                    stderr=error,
                )

    @property
    def env_variables(self):
        env_vars = self._image.attrs["Config"]["Env"]
        return {env.split("=", 1)[0]: env.split("=", 1)[1] for env in env_vars}

    @property
    def entry_point(self):
        return self._image.attrs["Config"]["Entrypoint"]

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
