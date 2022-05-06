#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping, Tuple

import yaml
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.cac.factory import LowCodeComponentFactory
from airbyte_cdk.sources.streams.core import Stream


class ConfigurableSource(AbstractSource):
    def __init__(self, path_to_spec):
        self._path_to_spec = path_to_spec
        self._factory = LowCodeComponentFactory()
        self._spec = self._load_spec()
        self._source_config = self._spec["source"]
        self._vars = self._source_config.get("vars", {})
        self._top_level_vars = self._spec.get("vars", {})

    def _load_spec(self):
        # TODO is it better to do package loading?
        with open(self._path_to_spec, "r") as f:
            return yaml.load(f.read(), Loader=yaml.SafeLoader)

    def get_spec_obj(self):
        return self._spec

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        connection_check_config = self._source_config["options"]["check"]
        connection_checker = self._factory.build(connection_check_config, self._merge_dicts(self._vars, self._top_level_vars), config)
        return connection_checker.check_connection(config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        pass

    def _merge_dicts(self, d1, d2):
        return {**d1, **d2}
