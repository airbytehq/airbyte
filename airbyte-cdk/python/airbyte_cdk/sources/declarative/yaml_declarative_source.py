#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
import typing
from dataclasses import dataclass, fields
from enum import EnumMeta
from typing import Any, List, Mapping, Union

from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.exceptions import InvalidConnectorDefinitionException
from airbyte_cdk.sources.declarative.parsers.factory import DeclarativeComponentFactory
from airbyte_cdk.sources.declarative.parsers.yaml_parser import YamlParser
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.streams.core import Stream
from dataclasses_jsonschema import JsonSchemaMixin
from jsonschema.validators import validate


@dataclass
class ConcreteDeclarativeSource(JsonSchemaMixin):
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

        stream_configs = self._source_config["streams"]
        for s in stream_configs:
            if "class_name" not in s:
                s["class_name"] = "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream"
        return [self._factory.create_component(stream_config, config)() for stream_config in self._source_config["streams"]]

    def _read_and_parse_yaml_file(self, path_to_yaml_file):
        with open(path_to_yaml_file, "r") as f:
            config_content = f.read()
            # Add schema validation entry point here using the factory
            parsed_config = YamlParser().parse(config_content)

            self._validate_source(parsed_config)
            return parsed_config

    def _validate_source(self, parsed_config):
        concrete_source = ConcreteDeclarativeSource(
            checker=self._source_config["check"],
            streams=[self._factory.create_component(stream_config, {})() for stream_config in self._source_config["streams"]],
        )
        declarative_source_schema = ConcreteDeclarativeSource.json_schema()
        validate(concrete_source, declarative_source_schema)

    @classmethod
    def generate_schema(cls) -> str:
        expanded_source_definition = cls.expand_schema_interfaces(ConcreteDeclarativeSource, {})
        expanded_schema = expanded_source_definition.json_schema()
        return json.dumps(expanded_schema, cls=SchemaEncoder)

    # Seriously me right now
    # https://i.kym-cdn.com/entries/icons/original/000/022/524/tumblr_o16n2kBlpX1ta3qyvo1_1280.jpg
    @classmethod
    def expand_schema_interfaces(cls, expand_class: type, cache: dict) -> type:
        if expand_class.__name__ in cache:
            return expand_class

        # We don't need to expand enums
        if isinstance(expand_class, EnumMeta):
            return expand_class

        # We can't parse CDK constructs past the declarative level
        if expand_class.__name__ == "Stream" or expand_class.__name__ == "HttpStream":
            return expand_class

        cache[expand_class.__name__] = expand_class

        copy_cls = type(expand_class.__name__, expand_class.__bases__, dict(expand_class.__dict__))
        class_fields = fields(copy_cls)
        for field in class_fields:
            unpacked_types = cls.unpack(field.type)
            for field_type in unpacked_types:
                module = field_type.__module__
                if module != "builtins" and module != "typing" and module != "pendulum.datetime":
                    # Also need to traverse down each objects fields
                    if field_type not in cache:
                        cls.expand_schema_interfaces(field_type, cache)

                    subclasses = field_type.__subclasses__()
                    for subclass in subclasses:
                        cls.expand_schema_interfaces(subclass, cache)
                    if subclasses:
                        copy_cls.__annotations__[field.name] = Union[tuple(subclasses)]
        return copy_cls

    # For components that are stored behind generics like List, Union, Optional, etc, we need to unpack the underlying type
    @classmethod
    def unpack(cls, field_type) -> typing.Tuple:
        origin = typing.get_origin(field_type)
        if origin == list or origin == Union:
            return typing.get_args(field_type)
        return (field_type,)


class SchemaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, property):
            return str(obj)
        elif isinstance(obj, HttpMethod):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
