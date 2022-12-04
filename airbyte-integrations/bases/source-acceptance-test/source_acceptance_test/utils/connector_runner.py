#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import logging
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

import docker
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from docker.errors import ContainerError, NotFound
from docker.models.containers import Container
from pydantic import ValidationError


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
            **kwargs,
        )
        with open(self.output_folder / "raw", "wb+") as f:
            for line in self.read(container, command=cmd, with_ext=raise_container_error):
                f.write(line.encode())
                try:
                    yield AirbyteMessage.parse_raw(line)
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
            error = exit_status["Error"] or exception or line
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
