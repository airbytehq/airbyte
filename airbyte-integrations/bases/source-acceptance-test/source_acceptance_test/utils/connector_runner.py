#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import logging
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

import docker
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from docker.errors import ContainerError
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
        logging.info("Docker run: \n%s\ninput: %s\noutput: %s", cmd, self.input_folder, self.output_folder)
        try:
            logs = self._client.containers.run(
                image=self._image, command=cmd, working_dir="/data", volumes=volumes, network="host", stdout=True, stderr=True, **kwargs
            )
        except ContainerError as err:
            # beautify error from container
            patched_error = ContainerError(
                container=err.container, exit_status=err.exit_status, command=err.command, image=err.image, stderr=err.stderr.decode()
            )
            raise patched_error from None  # get rid of any previous exception stack

        with open(str(self.output_folder / "raw"), "wb+") as f:
            f.write(logs)

        for line in logs.decode("utf-8").splitlines():
            try:
                yield AirbyteMessage.parse_raw(line)
            except ValidationError as exc:
                logging.warning("Unable to parse connector's output %s", exc)

    @property
    def env_variables(self):
        env_vars = self._image.attrs["Config"]["Env"]
        return {env.split("=", 1)[0]: env.split("=", 1)[1] for env in env_vars}

    @property
    def entry_point(self):
        return self._image.attrs["Config"]["Entrypoint"]
