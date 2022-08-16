#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import dataclass
from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.exceptions import InvalidConnectorDefinitionException
from airbyte_cdk.sources.declarative.parsers.factory import DeclarativeComponentFactory
from airbyte_cdk.sources.declarative.parsers.yaml_parser import YamlParser
from airbyte_cdk.sources.streams.core import Stream
from dataclasses_jsonschema import JsonSchemaMixin
from jsonschema.validators import validate


@dataclass
class ConcreteDeclarativeSource(JsonSchemaMixin):
    version: str
    checker: CheckStream
    streams: List[DeclarativeStream]


class YamlDeclarativeSource(DeclarativeSource):
    """Declarative source defined by a yaml file"""

    VALID_TOP_LEVEL_FIELDS = {"definitions", "streams", "check", "version"}

    def __init__(self, path_to_yaml):
        """
        :param path_to_yaml: Path to the yaml file describing the source
        """
        self.logger = logging.getLogger(f"airbyte.{self.name}")
        self._factory = DeclarativeComponentFactory()
        self._path_to_yaml = path_to_yaml
        self._source_config = self._read_and_parse_yaml_file(path_to_yaml)

        self._validate_source()

        # Stopgap to protect the top-level namespace until it's validated through the schema
        unknown_fields = [key for key in self._source_config.keys() if key not in self.VALID_TOP_LEVEL_FIELDS]
        if unknown_fields:
            raise InvalidConnectorDefinitionException(f"Found unknown top-level fields: {unknown_fields}")

    @property
    def connection_checker(self) -> ConnectionChecker:
        check = self._source_config["check"]
        if "class_name" not in check:
            check["class_name"] = "airbyte_cdk.sources.declarative.checks.check_stream.CheckStream"
        return self._factory.create_component(check, dict())(source=self)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        self.logger.debug(
            "parsed YAML into declarative source",
            extra={"path_to_yaml_file": self._path_to_yaml, "source_name": self.name, "parsed_config": json.dumps(self._source_config)},
        )
        return [self._factory.create_component(stream_config, config, True)() for stream_config in self._stream_configs()]

    def _read_and_parse_yaml_file(self, path_to_yaml_file):
        with open(path_to_yaml_file, "r") as f:
            config_content = f.read()
            return YamlParser().parse(config_content)

    def _validate_source(self):
        full_config = {}
        if "version" in self._source_config:
            full_config["version"] = self._source_config["version"]
        if "check" in self._source_config:
            full_config["checker"] = self._source_config["check"]
        streams = [self._factory.create_component(stream_config, {}, False)() for stream_config in self._stream_configs()]
        if len(streams) > 0:
            full_config["streams"] = streams
        declarative_source_schema = ConcreteDeclarativeSource.json_schema()
        validate(full_config, declarative_source_schema)

    def _stream_configs(self):
        stream_configs = self._source_config.get("streams", [])
        for s in stream_configs:
            if "class_name" not in s:
                s["class_name"] = "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream"
        return stream_configs
