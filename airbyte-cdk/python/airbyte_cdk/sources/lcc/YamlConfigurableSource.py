#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping

from airbyte_cdk.sources.lcc.checks.check_stream import CheckStream
from airbyte_cdk.sources.lcc.configurable_source import ConfigurableSource
from airbyte_cdk.sources.lcc.parsers.factory import LowCodeComponentFactory
from airbyte_cdk.sources.lcc.parsers.yaml_parser import YamlParser
from airbyte_cdk.sources.streams import Stream


class YamlConfigurableSource(ConfigurableSource):
    def __init__(self, path_to_yaml):
        self._path_to_yaml = path_to_yaml
        self._factory = LowCodeComponentFactory()
        self._parser = YamlParser()

    @property
    def connection_checker(self):
        # FIXME: this is hardcoded :(
        return CheckStream(self)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        with open(self._path_to_yaml, "r") as f:
            config_content = f.read()
            source_config = self._parser.parse(config_content)
        print(source_config["streams"])
        streams_config = source_config["streams"]
        streams = []
        for stream_config in streams_config:
            stream = self._factory.create_component(stream_config, config)()
            streams.append(stream)
        return streams
