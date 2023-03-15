#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import pkgutil
from typing import Any, Iterator, List, Mapping, MutableMapping, Union

import yaml
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
)
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CheckStream as CheckStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import Spec as SpecModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.types import ConnectionDefinition
from airbyte_cdk.sources.streams.core import Stream
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate


class ManifestDeclarativeSource(DeclarativeSource):
    """Declarative source defined by a manifest of low-code components that define source connector behavior"""

    VALID_TOP_LEVEL_FIELDS = {"check", "definitions", "schemas", "spec", "streams", "type", "version"}

    def __init__(self, source_config: ConnectionDefinition, debug: bool = False, component_factory: ModelToComponentFactory = None):
        """
        :param source_config(Mapping[str, Any]): The manifest of low-code components that describe the source connector
        :param debug(bool): True if debug mode is enabled
        :param component_factory(ModelToComponentFactory): optional factory if ModelToComponentFactory's default behaviour needs to be tweaked
        """
        self.logger = logging.getLogger(f"airbyte.{self.name}")

        # For ease of use we don't require the type to be specified at the top level manifest, but it should be included during processing
        manifest = dict(source_config)
        if "type" not in manifest:
            manifest["type"] = "DeclarativeSource"

        resolved_source_config = ManifestReferenceResolver().preprocess_manifest(manifest)
        propagated_source_config = ManifestComponentTransformer().propagate_types_and_parameters("", resolved_source_config, {})
        self._source_config = propagated_source_config
        self._debug = debug
        self._constructor = component_factory if component_factory else ModelToComponentFactory()

        self._validate_source()

    @property
    def resolved_manifest(self) -> Mapping[str, Any]:
        return self._source_config

    @property
    def connection_checker(self) -> ConnectionChecker:
        check = self._source_config["check"]
        if "type" not in check:
            check["type"] = "CheckStream"
        check_stream = self._constructor.create_component(CheckStreamModel, check, dict())
        if isinstance(check_stream, ConnectionChecker):
            return check_stream
        else:
            raise ValueError(f"Expected to generate a ConnectionChecker component, but received {check_stream.__class__}")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        self._emit_manifest_debug_message(extra_args={"source_name": self.name, "parsed_config": json.dumps(self._source_config)})

        source_streams = [
            self._constructor.create_component(DeclarativeStreamModel, stream_config, config)
            for stream_config in self._stream_configs(self._source_config)
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
        self._emit_manifest_debug_message(extra_args={"source_name": self.name, "parsed_config": json.dumps(self._source_config)})

        spec = self._source_config.get("spec")
        if spec:
            if "type" not in spec:
                spec["type"] = "Spec"
            spec_component = self._constructor.create_component(SpecModel, spec, dict())
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
        """
        Validates the connector manifest against the declarative component schema
        """
        try:
            raw_component_schema = pkgutil.get_data("airbyte_cdk", "sources/declarative/declarative_component_schema.yaml")
            declarative_component_schema = yaml.load(raw_component_schema, Loader=yaml.SafeLoader)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Failed to read manifest component json schema required for validation: {e}")

        streams = self._source_config.get("streams")
        if not streams:
            raise ValidationError(f"A valid manifest should have at least one stream defined. Got {streams}")

        try:
            validate(self._source_config, declarative_component_schema)
        except ValidationError as e:
            raise ValidationError("Validation against json schema defined in declarative_component_schema.yaml schema failed") from e

    def _stream_configs(self, manifest: Mapping[str, Any]):
        # This has a warning flag for static, but after we finish part 4 we'll replace manifest with self._source_config
        stream_configs = manifest.get("streams", [])
        for s in stream_configs:
            if "type" not in s:
                s["type"] = "DeclarativeStream"
        return stream_configs

    def _emit_manifest_debug_message(self, extra_args: dict):
        self.logger.debug("declarative source created from manifest", extra=extra_args)
