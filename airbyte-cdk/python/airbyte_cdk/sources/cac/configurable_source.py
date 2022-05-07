#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os
from typing import Any, List, Mapping, Tuple

import yaml
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.cac.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.cac.factory import LowCodeComponentFactory
from airbyte_cdk.sources.streams.core import Stream


class ConfigurableSource(AbstractSource):
    def __init__(self, path_to_spec):
        if not os.path.exists(path_to_spec):
            # Small hack until i figure out the docker issue
            path_to_spec = f"/airbyte/integration_code/{path_to_spec[1:]}"
        self._path_to_spec = path_to_spec
        self._factory = LowCodeComponentFactory()
        self._spec = self._load_spec()
        self._source_config = self._spec["source"]
        self._options = self._source_config["options"]
        self._vars = self._source_config.get("vars", {})
        self._top_level_vars = self._spec.get("vars", {})
        self._all_vars = self._merge_dicts(self._vars, self._top_level_vars)

    def _load_spec(self):
        # TODO is it better to do package loading?
        print(f"path: {self._path_to_spec}")
        print(f"path: {os.path}")
        print(f"os.listdir: {os.listdir()}")
        with open(self._path_to_spec, "r") as f:
            return yaml.load(f.read(), Loader=yaml.SafeLoader)

    def get_spec_obj(self):
        return self._spec

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        print("entering check_connection")
        connection_check_config = self._source_config["options"]["check"]
        connection_checker: ConnectionChecker = self._factory.create_component(connection_check_config, self._all_vars, config)
        print("about to call connection_checker")
        return connection_checker.check_connection(logger, config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        print(f"source_config: {self._source_config}")
        print(f"config: {config}")
        streams_config = self._source_config["options"]["streams"]

        streams = [
            LowCodeComponentFactory().create_component(stream_config, self._vars, config) for stream_config in streams_config.values()
        ]
        print(f"streams: {streams}")
        return streams

    #   streams_config = self._options["streams"]

    # for stream_name, stream_config in streams_config.items():
    #     print(stream_config)
    #     stream = LowCodeComponentFactory().build(stream_config, self._stream_config.get("vars", {}), config)

    def _merge_dicts(self, d1, d2):
        return {**d1, **d2}
