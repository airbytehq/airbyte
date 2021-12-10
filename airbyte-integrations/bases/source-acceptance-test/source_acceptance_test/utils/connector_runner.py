#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import docker
import json
import logging
import re
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Type
from docker.errors import ContainerError
from pathlib import Path
from pydantic import ValidationError
from typing import Iterable, List, Mapping, Optional

CONTAINER_PREFIX = "airbyte_tests_"


class ConnectorRunner:
    def __init__(self, image_name: str, volume: Path):
        self._client = docker.from_env()
        try:
            self._image = self._client.images.get(image_name)
        except docker.errors.ImageNotFound:
            print("Pulling docker image", image_name)
            self._image = self._client.images.pull(image_name)
            print("Pulling completed")
        self._runs = 0
        self._volume_base = volume

    @property
    def output_folder(self) -> Path:
        return self._volume_base / f"run_{self._runs}" / "output"

    @property
    def input_folder(self) -> Path:
        return self._volume_base / f"run_{self._runs}" / "input"

    def _prepare_volumes(self, config: Optional[Mapping], state: Optional[Mapping],
                         catalog: Optional[ConfiguredAirbyteCatalog]):
        self.input_folder.mkdir(parents=True)
        self.output_folder.mkdir(parents=True)

        if config:
            with open(str(self.input_folder / "tap_config.json"), "w") as outfile:
                json.dump(dict(config), outfile)

        if state:
            with open(str(self.input_folder / "state.json"), "w") as outfile:
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
        cmd = "check --config tap_config.json"
        output = list(self.run(cmd=cmd, config=config, **kwargs))
        return output

    def call_discover(self, config, **kwargs) -> List[AirbyteMessage]:
        cmd = "discover --config tap_config.json"
        output = list(self.run(cmd=cmd, config=config, **kwargs))
        return output

    def call_read(self, config, catalog, **kwargs) -> List[AirbyteMessage]:
        cmd = "read --config tap_config.json --catalog catalog.json"
        output = list(self.run(cmd=cmd, config=config, catalog=catalog, **kwargs))
        return output

    def call_read_with_state(self, config, catalog, state, **kwargs) -> List[AirbyteMessage]:
        cmd = "read --config tap_config.json --catalog catalog.json --state state.json"
        output = list(self.run(cmd=cmd, config=config, catalog=catalog, state=state, **kwargs))
        return output

    def run(self, cmd, config=None, state=None, catalog=None, **kwargs) -> Iterable[AirbyteMessage]:
        self._runs += 1
        volumes = self._prepare_volumes(config, state, catalog)

        logging.info(f"Docker run: \n{cmd}\n"
                     f"input: {self.input_folder}\noutput: {self.output_folder}")

        container = self._client.containers.create(
            image=self._image, command=cmd,
            working_dir="/data",
            auto_remove=True, detach=True,
            **kwargs
        )

        for line in container.restart(
                stdout=True, stderr=True,
                stream=True, logs=True,
                remove=True,
        ):
            line = line.strip().decode()
            try:
                message = AirbyteMessage.parse_raw(line)
            except ValidationError as exc:
                logging.warning("Unable to parse connector's output %s, error: %s", line, exc)
                continue

            if message.type == Type.LOG and "Traceback (most recent call last)" in message.log.message:
                logging.error(message.log.message.replace("\\\\n", "\n"))
            else:
                yield message

        exit_status = container.wait()
        if exit_status["StatusCode"]:
            logging.error(f"Docker container was failed with cmd: {cmd}, "
                          f'code {exit_status["StatusCode"]}, error: {exit_status["Error"]}')
            raise ContainerError(
                container=container,
                exit_status=exit_status["StatusCode"],
                command=cmd,
                image=self._image,
                stderr=exit_status["Error"],
            )

    @property
    def env_variables(self):
        env_vars = self._image.attrs["Config"]["Env"]
        return {env.split("=", 1)[0]: env.split("=", 1)[1] for env in env_vars}

    @property
    def entry_point(self):
        return self._image.attrs["Config"]["Entrypoint"]
