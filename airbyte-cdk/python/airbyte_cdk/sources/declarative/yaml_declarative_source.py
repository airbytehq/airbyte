#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import inspect
import json
import logging
import pkgutil
import typing
from dataclasses import dataclass, fields
from enum import Enum, EnumMeta
from typing import Any, List, Mapping, Union

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
        package = self.__class__.__module__.split(".")[0]

        yaml_config = pkgutil.get_data(package, path_to_yaml_file)
        decoded_yaml = yaml_config.decode()
        return YamlParser().parse(decoded_yaml)

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

    @staticmethod
    def generate_schema() -> str:
        expanded_source_definition = YamlDeclarativeSource.expand_schema_interfaces(ConcreteDeclarativeSource, {})
        expanded_schema = expanded_source_definition.json_schema()
        return json.dumps(expanded_schema, cls=SchemaEncoder)

    @staticmethod
    def expand_schema_interfaces(expand_class: type, visited: dict) -> type:
        """
        Recursive function that takes in class type that will have its interface fields unpacked and expended and then recursively
        attempt the same expansion on all the class' underlying fields that are declarative component. It also performs expansion
        with respect to interfaces that are contained within generic data types.
        :param expand_class: The declarative component class that will have its interface fields expanded
        :param visited: cache used to store a record of already visited declarative classes that have already been seen
        :return: The expanded declarative component
        """

        # Recursive base case to stop recursion if we have already expanded an interface in case of cyclical components
        # like CompositeErrorHandler
        if expand_class.__name__ in visited:
            return visited[expand_class.__name__]
        visited[expand_class.__name__] = expand_class

        next_classes = []
        class_fields = fields(expand_class)
        for field in class_fields:
            unpacked_field_types = DeclarativeComponentFactory.unpack(field.type)
            expand_class.__annotations__[field.name] = unpacked_field_types
            next_classes.extend(YamlDeclarativeSource._get_next_expand_classes(field.type))
        for next_class in next_classes:
            YamlDeclarativeSource.expand_schema_interfaces(next_class, visited)
        return expand_class

    @staticmethod
    def _get_next_expand_classes(field_type) -> list[type]:
        """
        Parses through a given field type and assembles a list of all underlying declarative components. For a concrete declarative class
        it will return itself. For a declarative interface it will return its subclasses. For declarative components in a generic type
        it will return the unpacked classes. Any non-declarative types will be skipped.
        :param field_type: A field type that
        :return:
        """
        generic_type = typing.get_origin(field_type)
        if generic_type is None:
            # We can only continue parsing declarative that inherit from the JsonSchemaMixin class because it is used
            # to generate the final json schema
            if inspect.isclass(field_type) and issubclass(field_type, JsonSchemaMixin) and not isinstance(field_type, EnumMeta):
                subclasses = field_type.__subclasses__()
                if subclasses:
                    return subclasses
                else:
                    return [field_type]
        elif generic_type == list or generic_type == Union:
            next_classes = []
            for underlying_type in typing.get_args(field_type):
                next_classes.extend(YamlDeclarativeSource._get_next_expand_classes(underlying_type))
            return next_classes
        return []


class SchemaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, property) or isinstance(obj, Enum):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
