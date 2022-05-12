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
    # FIXME: this whole class is yuck :(
    def __init__(self, path_to_spec):
        if not os.path.exists(path_to_spec):
            # Small hack until i figure out the docker issue
            path_to_spec = f"/airbyte/integration_code/{path_to_spec[1:]}"
        self._path_to_spec = path_to_spec
        self._factory = LowCodeComponentFactory()
        self._config = self._load_config()
        self._source_config = self._config["source"]
        self._options = self._source_config["options"]
        self._vars = self._source_config.get("vars", {})
        self._top_level_vars = self._config.get("vars", {})
        self._all_vars = self._merge_dicts(self._vars, self._top_level_vars)

    def _load_config(self):
        # TODO is it better to do package loading?
        with open(self._path_to_spec, "r") as f:
            return yaml.load(f.read(), Loader=yaml.SafeLoader)

    def get_spec_obj(self):
        return self._config["spec"]

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        connection_check_config = self._source_config["options"]["check"]
        connection_checker: ConnectionChecker = self._factory.create_component(connection_check_config, self._all_vars, config)
        return connection_checker.check_connection(logger, config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams_config = self._source_config["options"]["streams"]

        streams = [
            LowCodeComponentFactory().create_component(stream_config, self._vars, config) for stream_config in streams_config.values()
        ]
        return streams

    def _merge_dicts(self, d1, d2):
        return {**d1, **d2}
