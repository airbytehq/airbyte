#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.parsers.factory import DeclarativeComponentFactory
from airbyte_cdk.sources.declarative.parsers.yaml_parser import YamlParser
from airbyte_cdk.sources.streams import Stream
from jsonschema import validate


class ConcreteDeclarativeSource(JsonSchemaMixin):
    def __init__(self, check: ConnectionChecker, streams: List[DeclarativeStream]):
        self._check = check
        self._streams = streams


class YamlDeclarativeSource(DeclarativeSource):
    def __init__(self, path_to_yaml):
        self._factory = DeclarativeComponentFactory()
        self._source_config = self._read_and_parse_yaml_file(path_to_yaml)
        self._validate_definition()

    def _validate_definition(self):
        # run validation
        expanded_streams = [self._factory.create_component(stream_config, {}, False)() for stream_config in self._stream_configs()]
        config_to_validate = {"check": self._source_config["check"], "streams": expanded_streams}
        validate(config_to_validate, ConcreteDeclarativeSource.json_schema())

    def _stream_configs(self):
        stream_configs = self._source_config["streams"]
        for s in stream_configs:
            if "class_name" not in s:
                s["class_name"] = "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream"
        return stream_configs

    @property
    def connection_checker(self) -> ConnectionChecker:
        check = self._source_config["check"]
        if "class_name" not in check:
            check["class_name"] = "airbyte_cdk.sources.declarative.checks.check_stream.CheckStream"
        return self._factory.create_component(check, dict(), True)(source=self)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_configs = self._source_config["streams"]
        for s in stream_configs:
            if "class_name" not in s:
                s["class_name"] = "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream"

        return [self._factory.create_component(stream_config, config, True)() for stream_config in self._source_config["streams"]]

    def _read_and_parse_yaml_file(self, path_to_yaml_file):
        with open(path_to_yaml_file, "r") as f:
            config_content = f.read()
            return YamlParser().parse(config_content)
