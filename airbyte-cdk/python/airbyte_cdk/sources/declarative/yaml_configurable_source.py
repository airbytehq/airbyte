#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.parsers.factory import LowCodeComponentFactory
from airbyte_cdk.sources.declarative.parsers.yaml_parser import YamlParser
from airbyte_cdk.sources.streams import Stream


class YamldeclarativeSource(DeclarativeSource):
    def __init__(self, path_to_yaml):
        self._factory = LowCodeComponentFactory()
        self._parser = YamlParser()
        self._source_config = self._read_config(path_to_yaml)

    # FIXME: rename file
    @property
    def connection_checker(self):
        return self._factory.create_component(self._source_config["check"], dict())(source=self)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [self._factory.create_component(stream_config, config)() for stream_config in self._source_config["streams"]]

    def _read_config(self, path_to_yaml_file):
        with open(path_to_yaml_file, "r") as f:
            config_content = f.read()
            return self._parser.parse(config_content)
