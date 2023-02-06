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
from typing import Any, Iterator, List, Mapping, MutableMapping, Union

import yaml
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
)
from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.exceptions import InvalidConnectorDefinitionException
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CheckStream as CheckStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import Spec as SpecModel
from airbyte_cdk.sources.declarative.parsers.factory import DeclarativeComponentFactory
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.types import ConnectionDefinition
from airbyte_cdk.sources.streams.core import Stream
from dataclasses_jsonschema import JsonSchemaMixin
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate


@dataclass
class ConcreteDeclarativeSource(JsonSchemaMixin):
    version: str
    check: CheckStream
    streams: List[DeclarativeStream]


class ManifestDeclarativeSource(DeclarativeSource):
    """Declarative source defined by a manifest of low-code components that define source connector behavior"""

    VALID_TOP_LEVEL_FIELDS = {"check", "definitions", "schemas", "spec", "streams", "type", "version"}

    def __init__(
        self,
        source_config: ConnectionDefinition,
        debug: bool = False,
        component_factory: ModelToComponentFactory = None,
        construct_using_pydantic_models: bool = False,
    ):
        """
        :param source_config(Mapping[str, Any]): The manifest of low-code components that describe the source connector
        :param debug(bool): True if debug mode is enabled
        """
        self.logger = logging.getLogger(f"airbyte.{self.name}")

        # Controls whether we build components using the manual handwritten schema and Pydantic models or the legacy flow
        self.construct_using_pydantic_models = True

        # For ease of use we don't require the type to be specified at the top level manifest, but it should be included during processing
        manifest = dict(source_config)
        if "type" not in manifest:
            manifest["type"] = "DeclarativeSource"

        resolved_source_config = ManifestReferenceResolver().preprocess_manifest(manifest)
        propagated_source_config = ManifestComponentTransformer().propagate_types_and_options("", resolved_source_config, {})
        self._new_source_config = propagated_source_config
        self._legacy_source_config = resolved_source_config
        self._debug = debug
        self._legacy_factory = DeclarativeComponentFactory()  # Legacy factory used to instantiate declarative components from the manifest
        if component_factory:
            self._constructor = component_factory
        else:
            self._constructor = (
                ModelToComponentFactory()
            )  # New factory which converts the manifest to Pydantic models to construct components

        self._validate_source()

        # todo: The handwritten schema uses additionalProperties: false to validate, when we delete legacy path this can be removed
        # Stopgap to protect the top-level namespace until it's validated through the schema
        unknown_fields = [key for key in self._legacy_source_config.keys() if key not in self.VALID_TOP_LEVEL_FIELDS]
        if unknown_fields:
            raise InvalidConnectorDefinitionException(f"Found unknown top-level fields: {unknown_fields}")

    @property
    def resolved_manifest(self) -> Mapping[str, Any]:
        return self._new_source_config

    @property
    def connection_checker(self) -> ConnectionChecker:
        check = self._new_source_config["check"] if self.construct_using_pydantic_models else self._legacy_source_config["check"]
        if "type" not in check:
            check["type"] = "CheckStream"
        if self.construct_using_pydantic_models:
            check_stream = self._constructor.create_component(CheckStreamModel, check, dict())
            if isinstance(check_stream, ConnectionChecker):
                return check_stream
            else:
                raise ValueError(f"Expected to generate a ConnectionChecker component, but received {check_stream.__class__}")
        else:
            return self._legacy_factory.create_component(check, dict())(source=self)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        source_config = self._new_source_config if self.construct_using_pydantic_models else self._legacy_source_config
        self._emit_manifest_debug_message(extra_args={"source_name": self.name, "parsed_config": json.dumps(source_config)})

        if self.construct_using_pydantic_models:
            source_streams = [
                self._constructor.create_component(DeclarativeStreamModel, stream_config, config)
                for stream_config in self._stream_configs(source_config)
            ]
        else:
            source_streams = [
                self._legacy_factory.create_component(stream_config, config, True)()
                for stream_config in self._stream_configs(source_config)
            ]

        for stream in source_streams:
            # make sure the log level is always applied to the stream's logger
            self._apply_log_level_to_stream_logger(self.logger, stream)
        return source_streams

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        """
        Returns the connector specification (spec) as defined in the Airbyte Protocol. The spec is an object describing the possible
        configurations (e.g: username and password) which can be configured when running this connector. For low-code connectors, this
        will first attempt to load the spec from the manifest's spec block, otherwise it will load it from "spec.yaml" or "spec.json"
        in the project root.
        """
        self._configure_logger_level(logger)
        source_config = self._new_source_config if self.construct_using_pydantic_models else self._legacy_source_config
        self._emit_manifest_debug_message(extra_args={"source_name": self.name, "parsed_config": json.dumps(source_config)})

        spec = source_config.get("spec")
        if spec:
            if "type" not in spec:
                spec["type"] = "Spec"
            if self.construct_using_pydantic_models:
                spec_component = self._constructor.create_component(SpecModel, spec, dict())
            else:
                spec_component = self._legacy_factory.create_component(spec, dict())()
            return spec_component.generate_spec()
        else:
            return super().spec(logger)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        self._configure_logger_level(logger)
        return super().check(logger, config)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        self._configure_logger_level(logger)
        yield from super().read(logger, config, catalog, state)

    def _configure_logger_level(self, logger: logging.Logger):
        """
        Set the log level to logging.DEBUG if debug mode is enabled
        """
        if self._debug:
            logger.setLevel(logging.DEBUG)

    def _validate_source(self):
        # Validates the connector manifest against the schema auto-generated from the low-code backend
        full_config = {}
        if "version" in self._legacy_source_config:
            full_config["version"] = self._legacy_source_config["version"]
        full_config["check"] = self._legacy_source_config["check"]
        streams = [
            self._legacy_factory.create_component(stream_config, {}, False)()
            for stream_config in self._stream_configs(self._legacy_source_config)
        ]
        if len(streams) > 0:
            full_config["streams"] = streams
        declarative_source_schema = ConcreteDeclarativeSource.json_schema()

        try:
            validate(full_config, declarative_source_schema)
        except ValidationError as e:
            raise ValidationError("Validation against auto-generated schema failed") from e

        # Validates the connector manifest against the low-code component json schema
        try:
            raw_component_schema = pkgutil.get_data("airbyte_cdk", "sources/declarative/declarative_component_schema.yaml")
            declarative_component_schema = yaml.load(raw_component_schema, Loader=yaml.SafeLoader)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Failed to read manifest component json schema required for validation: {e}")

        try:
            validate(self._new_source_config, declarative_component_schema)
        except ValidationError as e:
            raise ValidationError("Validation against json schema defined in declarative_component_schema.yaml schema failed") from e

    def _stream_configs(self, manifest: Mapping[str, Any]):
        # This has a warning flag for static, but after we finish part 4 we'll replace manifest with self._source_config
        stream_configs = manifest.get("streams", [])
        for s in stream_configs:
            if "type" not in s:
                s["type"] = "DeclarativeStream"
        return stream_configs

    @staticmethod
    def generate_schema() -> str:
        expanded_source_manifest = ManifestDeclarativeSource.expand_schema_interfaces(ConcreteDeclarativeSource, {})
        expanded_schema = expanded_source_manifest.json_schema()
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
            next_classes.extend(ManifestDeclarativeSource._get_next_expand_classes(field.type))
        for next_class in next_classes:
            ManifestDeclarativeSource.expand_schema_interfaces(next_class, visited)
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
                next_classes.extend(ManifestDeclarativeSource._get_next_expand_classes(underlying_type))
            return next_classes
        return []

    def _emit_manifest_debug_message(self, extra_args: dict):
        self.logger.debug("declarative source created from manifest", extra=extra_args)


class SchemaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, property) or isinstance(obj, Enum):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
