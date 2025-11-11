#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import logging
import pkgutil
from copy import deepcopy
from importlib import metadata
from types import ModuleType
from typing import Any, Dict, Iterator, List, Mapping, Optional, Set, Union

import orjson
import yaml
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from packaging.version import InvalidVersion, Version

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.connector_builder.models import (
    LogMessage as ConnectorBuilderLogMessage,
)
from airbyte_cdk.legacy.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.manifest_migrations.migration_handler import (
    ManifestMigrationHandler,
)
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    FailureType,
)
from airbyte_cdk.models.airbyte_protocol_serializers import AirbyteMessageSerializer
from airbyte_cdk.sources.declarative.checks import COMPONENTS_CHECKER_TYPE_MAPPING
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.interpolation import InterpolatedBoolean
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConditionalStreams as ConditionalStreamsModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DeclarativeStream as DeclarativeStreamModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    Spec as SpecModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    StateDelegatingStream as StateDelegatingStreamModel,
)
from airbyte_cdk.sources.declarative.parsers.custom_code_compiler import (
    get_registered_components_module,
)
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import (
    ManifestComponentTransformer,
)
from airbyte_cdk.sources.declarative.parsers.manifest_normalizer import (
    ManifestNormalizer,
)
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import (
    ManifestReferenceResolver,
)
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import (
    ModelToComponentFactory,
)
from airbyte_cdk.sources.declarative.resolvers import COMPONENTS_RESOLVER_TYPE_MAPPING
from airbyte_cdk.sources.declarative.spec.spec import Spec
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.types import Config, ConnectionDefinition
from airbyte_cdk.sources.utils.slice_logger import (
    AlwaysLogSliceLogger,
    DebugSliceLogger,
    SliceLogger,
)
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def _get_declarative_component_schema() -> Dict[str, Any]:
    try:
        raw_component_schema = pkgutil.get_data(
            "airbyte_cdk", "sources/declarative/declarative_component_schema.yaml"
        )
        if raw_component_schema is not None:
            declarative_component_schema = yaml.load(raw_component_schema, Loader=yaml.SafeLoader)
            return declarative_component_schema  # type: ignore
        else:
            raise RuntimeError(
                "Failed to read manifest component json schema required for deduplication"
            )
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Failed to read manifest component json schema required for deduplication: {e}"
        )


class ManifestDeclarativeSource(DeclarativeSource):
    """Declarative source defined by a manifest of low-code components that define source connector behavior"""

    def __init__(
        self,
        source_config: ConnectionDefinition,
        *,
        config: Mapping[str, Any] | None = None,
        debug: bool = False,
        emit_connector_builder_messages: bool = False,
        component_factory: Optional[ModelToComponentFactory] = None,
        migrate_manifest: Optional[bool] = False,
        normalize_manifest: Optional[bool] = False,
        config_path: Optional[str] = None,
    ) -> None:
        """
        Args:
            config: The provided config dict.
            source_config: The manifest of low-code components that describe the source connector.
            debug: True if debug mode is enabled.
            emit_connector_builder_messages: True if messages should be emitted to the connector builder.
            component_factory: optional factory if ModelToComponentFactory's default behavior needs to be tweaked.
            normalize_manifest: Optional flag to indicate if the manifest should be normalized.
            config_path: Optional path to the config file.
        """
        self.logger = logging.getLogger(f"airbyte.{self.name}")
        self._should_normalize = normalize_manifest
        self._should_migrate = migrate_manifest
        self._declarative_component_schema = _get_declarative_component_schema()
        # If custom components are needed, locate and/or register them.
        self.components_module: ModuleType | None = get_registered_components_module(config=config)
        # set additional attributes
        self._debug = debug
        self._emit_connector_builder_messages = emit_connector_builder_messages
        self._constructor = (
            component_factory
            if component_factory
            else ModelToComponentFactory(
                emit_connector_builder_messages=emit_connector_builder_messages,
                max_concurrent_async_job_count=source_config.get("max_concurrent_async_job_count"),
            )
        )
        self._message_repository = self._constructor.get_message_repository()
        self._slice_logger: SliceLogger = (
            AlwaysLogSliceLogger() if emit_connector_builder_messages else DebugSliceLogger()
        )

        # resolve all components in the manifest
        self._source_config = self._pre_process_manifest(dict(source_config))
        # validate resolved manifest against the declarative component schema
        self._validate_source()
        # apply additional post-processing to the manifest
        self._post_process_manifest()

        spec: Optional[Mapping[str, Any]] = self._source_config.get("spec")
        self._spec_component: Optional[Spec] = (
            self._constructor.create_component(SpecModel, spec, dict()) if spec else None
        )
        self._config = self._migrate_and_transform_config(config_path, config) or {}

    @property
    def resolved_manifest(self) -> Mapping[str, Any]:
        """
        Returns the resolved manifest configuration for the source.

        This property provides access to the internal source configuration as a mapping,
        which contains all settings and parameters required to define the source's behavior.

        Returns:
            Mapping[str, Any]: The resolved source configuration manifest.
        """
        return self._source_config

    def _pre_process_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocesses the provided manifest dictionary by resolving any manifest references.

        This method modifies the input manifest in place, resolving references using the
        ManifestReferenceResolver to ensure all references within the manifest are properly handled.

        Args:
            manifest (Dict[str, Any]): The manifest dictionary to preprocess and resolve references in.

        Returns:
            None
        """
        # For ease of use we don't require the type to be specified at the top level manifest, but it should be included during processing
        manifest = self._fix_source_type(manifest)
        # Resolve references in the manifest
        resolved_manifest = ManifestReferenceResolver().preprocess_manifest(manifest)
        # Propagate types and parameters throughout the manifest
        propagated_manifest = ManifestComponentTransformer().propagate_types_and_parameters(
            "", resolved_manifest, {}
        )

        return propagated_manifest

    def _post_process_manifest(self) -> None:
        """
        Post-processes the manifest after validation.
        This method is responsible for any additional modifications or transformations needed
        after the manifest has been validated and before it is used in the source.
        """
        # apply manifest migration, if required
        self._migrate_manifest()
        # apply manifest normalization, if required
        self._normalize_manifest()

    def _normalize_manifest(self) -> None:
        """
        This method is used to normalize the manifest. It should be called after the manifest has been validated.

        Connector Builder UI rendering requires the manifest to be in a specific format.
         - references have been resolved
         - the commonly used definitions are extracted to the `definitions.linked.*`
        """
        if self._should_normalize:
            normalizer = ManifestNormalizer(self._source_config, self._declarative_component_schema)
            self._source_config = normalizer.normalize()

    def _migrate_and_transform_config(
        self,
        config_path: Optional[str],
        config: Optional[Config],
    ) -> Optional[Config]:
        if not config:
            return None
        if not self._spec_component:
            return config
        mutable_config = dict(config)
        self._spec_component.migrate_config(mutable_config)
        if mutable_config != config:
            if config_path:
                with open(config_path, "w") as f:
                    json.dump(mutable_config, f)
            self.message_repository.emit_message(
                create_connector_config_control_message(mutable_config)
            )
            # We have no mechanism for consuming the queue, so we print the messages to stdout
            for message in self.message_repository.consume_queue():
                print(orjson.dumps(AirbyteMessageSerializer.dump(message)).decode())
        self._spec_component.transform_config(mutable_config)
        return mutable_config

    def configure(self, config: Mapping[str, Any], temp_dir: str) -> Mapping[str, Any]:
        config = self._config or config
        return super().configure(config, temp_dir)

    def _migrate_manifest(self) -> None:
        """
        This method is used to migrate the manifest. It should be called after the manifest has been validated.
        The migration is done in place, so the original manifest is modified.

        The original manifest is returned if any error occurs during migration.
        """
        if self._should_migrate:
            manifest_migrator = ManifestMigrationHandler(self._source_config)
            self._source_config = manifest_migrator.apply_migrations()
            # validate migrated manifest against the declarative component schema
            self._validate_source()

    def _fix_source_type(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix the source type in the manifest. This is necessary because the source type is not always set in the manifest.
        """
        if "type" not in manifest:
            manifest["type"] = "DeclarativeSource"

        return manifest

    @property
    def message_repository(self) -> MessageRepository:
        return self._message_repository

    @property
    def dynamic_streams(self) -> List[Dict[str, Any]]:
        return self._dynamic_stream_configs(
            manifest=self._source_config,
            config=self._config,
            with_dynamic_stream_name=True,
        )

    def deprecation_warnings(self) -> List[ConnectorBuilderLogMessage]:
        return self._constructor.get_model_deprecations()

    @property
    def connection_checker(self) -> ConnectionChecker:
        check = self._source_config["check"]
        if "type" not in check:
            check["type"] = "CheckStream"
        check_stream = self._constructor.create_component(
            COMPONENTS_CHECKER_TYPE_MAPPING[check["type"]],
            check,
            dict(),
            emit_connector_builder_messages=self._emit_connector_builder_messages,
        )
        if isinstance(check_stream, ConnectionChecker):
            return check_stream
        else:
            raise ValueError(
                f"Expected to generate a ConnectionChecker component, but received {check_stream.__class__}"
            )

    def streams(self, config: Mapping[str, Any]) -> List[Union[Stream, AbstractStream]]:  # type: ignore  # we are migrating away from the AbstractSource and are expecting that this will only be called by ConcurrentDeclarativeSource or the Connector Builder
        """
        As a migration step, this method will return both legacy stream (Stream) and concurrent stream (AbstractStream).
        Once the migration is done, we can probably have this method throw "not implemented" as we figure out how to
        fully decouple this from the AbstractSource.
        """
        if self._spec_component:
            self._spec_component.validate_config(config)

        self._emit_manifest_debug_message(
            extra_args={
                "source_name": self.name,
                "parsed_config": json.dumps(self._source_config),
            }
        )

        stream_configs = (
            self._stream_configs(self._source_config, config=config) + self.dynamic_streams
        )

        api_budget_model = self._source_config.get("api_budget")
        if api_budget_model:
            self._constructor.set_api_budget(api_budget_model, config)

        source_streams = [
            self._constructor.create_component(
                (
                    StateDelegatingStreamModel
                    if stream_config.get("type") == StateDelegatingStreamModel.__name__
                    else DeclarativeStreamModel
                ),
                stream_config,
                config,
                emit_connector_builder_messages=self._emit_connector_builder_messages,
            )
            for stream_config in self._initialize_cache_for_parent_streams(deepcopy(stream_configs))
        ]
        return source_streams

    @staticmethod
    def _initialize_cache_for_parent_streams(
        stream_configs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        parent_streams = set()

        def update_with_cache_parent_configs(
            parent_configs: list[dict[str, Any]],
        ) -> None:
            for parent_config in parent_configs:
                parent_streams.add(parent_config["stream"]["name"])
                if parent_config["stream"]["type"] == "StateDelegatingStream":
                    parent_config["stream"]["full_refresh_stream"]["retriever"]["requester"][
                        "use_cache"
                    ] = True
                    parent_config["stream"]["incremental_stream"]["retriever"]["requester"][
                        "use_cache"
                    ] = True
                else:
                    parent_config["stream"]["retriever"]["requester"]["use_cache"] = True

        for stream_config in stream_configs:
            if stream_config.get("incremental_sync", {}).get("parent_stream"):
                parent_streams.add(stream_config["incremental_sync"]["parent_stream"]["name"])
                stream_config["incremental_sync"]["parent_stream"]["retriever"]["requester"][
                    "use_cache"
                ] = True

            elif stream_config.get("retriever", {}).get("partition_router", {}):
                partition_router = stream_config["retriever"]["partition_router"]

                if isinstance(partition_router, dict) and partition_router.get(
                    "parent_stream_configs"
                ):
                    update_with_cache_parent_configs(partition_router["parent_stream_configs"])
                elif isinstance(partition_router, list):
                    for router in partition_router:
                        if router.get("parent_stream_configs"):
                            update_with_cache_parent_configs(router["parent_stream_configs"])

        for stream_config in stream_configs:
            if stream_config["name"] in parent_streams:
                if stream_config["type"] == "StateDelegatingStream":
                    stream_config["full_refresh_stream"]["retriever"]["requester"]["use_cache"] = (
                        True
                    )
                    stream_config["incremental_stream"]["retriever"]["requester"]["use_cache"] = (
                        True
                    )
                else:
                    stream_config["retriever"]["requester"]["use_cache"] = True
        return stream_configs

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        """
        Returns the connector specification (spec) as defined in the Airbyte Protocol. The spec is an object describing the possible
        configurations (e.g: username and password) which can be configured when running this connector. For low-code connectors, this
        will first attempt to load the spec from the manifest's spec block, otherwise it will load it from "spec.yaml" or "spec.json"
        in the project root.
        """
        self._configure_logger_level(logger)
        self._emit_manifest_debug_message(
            extra_args={
                "source_name": self.name,
                "parsed_config": json.dumps(self._source_config),
            }
        )

        return (
            self._spec_component.generate_spec() if self._spec_component else super().spec(logger)
        )

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        self._configure_logger_level(logger)
        return super().check(logger, config)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[List[AirbyteStateMessage]] = None,
    ) -> Iterator[AirbyteMessage]:
        self._configure_logger_level(logger)
        yield from super().read(logger, config, catalog, state)

    def _configure_logger_level(self, logger: logging.Logger) -> None:
        """
        Set the log level to logging.DEBUG if debug mode is enabled
        """
        if self._debug:
            logger.setLevel(logging.DEBUG)

    def _validate_source(self) -> None:
        """
        Validates the connector manifest against the declarative component schema
        """

        try:
            validate(self._source_config, self._declarative_component_schema)
        except ValidationError as e:
            raise ValidationError(
                "Validation against json schema defined in declarative_component_schema.yaml schema failed"
            ) from e

        cdk_version_str = metadata.version("airbyte_cdk")
        cdk_version = self._parse_version(cdk_version_str, "airbyte-cdk")
        manifest_version_str = self._source_config.get("version")
        if manifest_version_str is None:
            raise RuntimeError(
                "Manifest version is not defined in the manifest. This is unexpected since it should be a required field. Please contact support."
            )
        manifest_version = self._parse_version(manifest_version_str, "manifest")

        if (cdk_version.major, cdk_version.minor, cdk_version.micro) == (0, 0, 0):
            # Skipping version compatibility check on unreleased dev branch
            pass
        elif (cdk_version.major, cdk_version.minor) < (
            manifest_version.major,
            manifest_version.minor,
        ):
            raise ValidationError(
                f"The manifest version {manifest_version!s} is greater than the airbyte-cdk package version ({cdk_version!s}). Your "
                f"manifest may contain features that are not in the current CDK version."
            )
        elif (manifest_version.major, manifest_version.minor) < (0, 29):
            raise ValidationError(
                f"The low-code framework was promoted to Beta in airbyte-cdk version 0.29.0 and contains many breaking changes to the "
                f"language. The manifest version {manifest_version!s} is incompatible with the airbyte-cdk package version "
                f"{cdk_version!s} which contains these breaking changes."
            )

    @staticmethod
    def _parse_version(
        version: str,
        version_type: str,
    ) -> Version:
        """Takes a semantic version represented as a string and splits it into a tuple.

        The fourth part (prerelease) is not returned in the tuple.

        Returns:
            Version: the parsed version object
        """
        try:
            parsed_version = Version(version)
        except InvalidVersion as ex:
            raise ValidationError(
                f"The {version_type} version '{version}' is not a valid version format."
            ) from ex
        else:
            # No exception
            return parsed_version

    def _stream_configs(
        self, manifest: Mapping[str, Any], config: Mapping[str, Any]
    ) -> List[Dict[str, Any]]:
        # This has a warning flag for static, but after we finish part 4 we'll replace manifest with self._source_config
        stream_configs = []
        for current_stream_config in manifest.get("streams", []):
            if (
                "type" in current_stream_config
                and current_stream_config["type"] == "ConditionalStreams"
            ):
                interpolated_boolean = InterpolatedBoolean(
                    condition=current_stream_config.get("condition"),
                    parameters={},
                )

                if interpolated_boolean.eval(config=config):
                    stream_configs.extend(current_stream_config.get("streams", []))
            else:
                if "type" not in current_stream_config:
                    current_stream_config["type"] = "DeclarativeStream"
                stream_configs.append(current_stream_config)
        return stream_configs

    def _dynamic_stream_configs(
        self,
        manifest: Mapping[str, Any],
        config: Mapping[str, Any],
        with_dynamic_stream_name: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        dynamic_stream_definitions: List[Dict[str, Any]] = manifest.get("dynamic_streams", [])
        dynamic_stream_configs: List[Dict[str, Any]] = []
        seen_dynamic_streams: Set[str] = set()

        for dynamic_definition_index, dynamic_definition in enumerate(dynamic_stream_definitions):
            components_resolver_config = dynamic_definition["components_resolver"]

            if not components_resolver_config:
                raise ValueError(
                    f"Missing 'components_resolver' in dynamic definition: {dynamic_definition}"
                )

            resolver_type = components_resolver_config.get("type")
            if not resolver_type:
                raise ValueError(
                    f"Missing 'type' in components resolver configuration: {components_resolver_config}"
                )

            if resolver_type not in COMPONENTS_RESOLVER_TYPE_MAPPING:
                raise ValueError(
                    f"Invalid components resolver type '{resolver_type}'. "
                    f"Expected one of {list(COMPONENTS_RESOLVER_TYPE_MAPPING.keys())}."
                )

            if "retriever" in components_resolver_config:
                components_resolver_config["retriever"]["requester"]["use_cache"] = True

            # Create a resolver for dynamic components based on type
            if resolver_type == "HttpComponentsResolver":
                components_resolver = self._constructor.create_component(
                    model_type=COMPONENTS_RESOLVER_TYPE_MAPPING[resolver_type],
                    component_definition=components_resolver_config,
                    config=config,
                    stream_name=dynamic_definition.get("name"),
                )
            else:
                components_resolver = self._constructor.create_component(
                    model_type=COMPONENTS_RESOLVER_TYPE_MAPPING[resolver_type],
                    component_definition=components_resolver_config,
                    config=config,
                )

            stream_template_config = dynamic_definition["stream_template"]

            for dynamic_stream in components_resolver.resolve_components(
                stream_template_config=stream_template_config
            ):
                # Get the use_parent_parameters configuration from the dynamic definition
                # Default to True for backward compatibility, since connectors were already using it by default when this param was added
                use_parent_parameters = dynamic_definition.get("use_parent_parameters", True)

                dynamic_stream = {
                    **ManifestComponentTransformer().propagate_types_and_parameters(
                        "", dynamic_stream, {}, use_parent_parameters=use_parent_parameters
                    )
                }

                if "type" not in dynamic_stream:
                    dynamic_stream["type"] = "DeclarativeStream"

                # Ensure that each stream is created with a unique name
                name = dynamic_stream.get("name")

                if with_dynamic_stream_name:
                    dynamic_stream["dynamic_stream_name"] = dynamic_definition.get(
                        "name", f"dynamic_stream_{dynamic_definition_index}"
                    )

                if not isinstance(name, str):
                    raise ValueError(
                        f"Expected stream name {name} to be a string, got {type(name)}."
                    )

                if name in seen_dynamic_streams:
                    error_message = f"Dynamic streams list contains a duplicate name: {name}. Please contact Airbyte Support."
                    failure_type = FailureType.system_error

                    if resolver_type == "ConfigComponentsResolver":
                        error_message = f"Dynamic streams list contains a duplicate name: {name}. Please check your configuration."
                        failure_type = FailureType.config_error

                    raise AirbyteTracedException(
                        message=error_message,
                        internal_message=error_message,
                        failure_type=failure_type,
                    )

                seen_dynamic_streams.add(name)
                dynamic_stream_configs.append(dynamic_stream)

        return dynamic_stream_configs

    def _emit_manifest_debug_message(self, extra_args: dict[str, Any]) -> None:
        self.logger.debug("declarative source created from manifest", extra=extra_args)
