# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
import logging
import pkgutil
from copy import deepcopy
from dataclasses import dataclass, field
from queue import Queue
from types import ModuleType
from typing import (
    Any,
    ClassVar,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
)

import orjson
import yaml
from airbyte_protocol_dataclasses.models import AirbyteStreamStatus, Level, StreamDescriptor
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.connector_builder.models import (
    LogMessage as ConnectorBuilderLogMessage,
)
from airbyte_cdk.manifest_migrations.migration_handler import (
    ManifestMigrationHandler,
)
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    FailureType,
    Status,
)
from airbyte_cdk.models.airbyte_protocol_serializers import AirbyteMessageSerializer
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.declarative.checks import COMPONENTS_CHECKER_TYPE_MAPPING
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.concurrency_level import ConcurrencyLevel
from airbyte_cdk.sources.declarative.interpolation import InterpolatedBoolean
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConcurrencyLevel as ConcurrencyLevelModel,
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
from airbyte_cdk.sources.declarative.types import Config, ConnectionDefinition
from airbyte_cdk.sources.message.concurrent_repository import ConcurrentMessageRepository
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partitions.types import QueueItem
from airbyte_cdk.sources.utils.slice_logger import (
    AlwaysLogSliceLogger,
    DebugSliceLogger,
    SliceLogger,
)
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


@dataclass
class TestLimits:
    __test__: ClassVar[bool] = False  # Tell Pytest this is not a Pytest class, despite its name

    DEFAULT_MAX_PAGES_PER_SLICE: ClassVar[int] = 5
    DEFAULT_MAX_SLICES: ClassVar[int] = 5
    DEFAULT_MAX_RECORDS: ClassVar[int] = 100
    DEFAULT_MAX_STREAMS: ClassVar[int] = 100

    max_records: int = field(default=DEFAULT_MAX_RECORDS)
    max_pages_per_slice: int = field(default=DEFAULT_MAX_PAGES_PER_SLICE)
    max_slices: int = field(default=DEFAULT_MAX_SLICES)
    max_streams: int = field(default=DEFAULT_MAX_STREAMS)


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


class ConcurrentDeclarativeSource(Source):
    # By default, we defer to a value of 2. A value lower than could cause a PartitionEnqueuer to be stuck in a state of deadlock
    # because it has hit the limit of futures but not partition reader is consuming them.
    _LOWEST_SAFE_CONCURRENCY_LEVEL = 2

    def __init__(
        self,
        catalog: Optional[ConfiguredAirbyteCatalog] = None,
        config: Optional[Mapping[str, Any]] = None,
        state: Optional[List[AirbyteStateMessage]] = None,
        *,
        source_config: ConnectionDefinition,
        debug: bool = False,
        emit_connector_builder_messages: bool = False,
        migrate_manifest: bool = False,
        normalize_manifest: bool = False,
        limits: Optional[TestLimits] = None,
        config_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.logger = logging.getLogger(f"airbyte.{self.name}")

        self._limits = limits

        # todo: We could remove state from initialization. Now that streams are grouped during the read(), a source
        #  no longer needs to store the original incoming state. But maybe there's an edge case?
        self._connector_state_manager = ConnectorStateManager(state=state)  # type: ignore  # state is always in the form of List[AirbyteStateMessage]. The ConnectorStateManager should use generics, but this can be done later

        # We set a maxsize to for the main thread to process record items when the queue size grows. This assumes that there are less
        # threads generating partitions that than are max number of workers. If it weren't the case, we could have threads only generating
        # partitions which would fill the queue. This number is arbitrarily set to 10_000 but will probably need to be changed given more
        # information and might even need to be configurable depending on the source
        queue: Queue[QueueItem] = Queue(maxsize=10_000)
        message_repository = InMemoryMessageRepository(
            Level.DEBUG if emit_connector_builder_messages else Level.INFO
        )

        # To reduce the complexity of the concurrent framework, we are not enabling RFR with synthetic
        # cursors. We do this by no longer automatically instantiating RFR cursors when converting
        # the declarative models into runtime components. Concurrent sources will continue to checkpoint
        # incremental streams running in full refresh.
        component_factory = ModelToComponentFactory(
            emit_connector_builder_messages=emit_connector_builder_messages,
            message_repository=ConcurrentMessageRepository(queue, message_repository),
            configured_catalog=catalog,
            connector_state_manager=self._connector_state_manager,
            max_concurrent_async_job_count=source_config.get("max_concurrent_async_job_count"),
            limit_pages_fetched_per_slice=limits.max_pages_per_slice if limits else None,
            limit_slices_fetched=limits.max_slices if limits else None,
            disable_retries=True if limits else False,
            disable_cache=True if limits else False,
        )

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

        concurrency_level_from_manifest = self._source_config.get("concurrency_level")
        if concurrency_level_from_manifest:
            concurrency_level_component = self._constructor.create_component(
                model_type=ConcurrencyLevelModel,
                component_definition=concurrency_level_from_manifest,
                config=config or {},
            )
            if not isinstance(concurrency_level_component, ConcurrencyLevel):
                raise ValueError(
                    f"Expected to generate a ConcurrencyLevel component, but received {concurrency_level_component.__class__}"
                )

            concurrency_level = concurrency_level_component.get_concurrency_level()
            initial_number_of_partitions_to_generate = max(
                concurrency_level // 2, 1
            )  # Partition_generation iterates using range based on this value. If this is floored to zero we end up in a dead lock during start up
        else:
            concurrency_level = self._LOWEST_SAFE_CONCURRENCY_LEVEL
            initial_number_of_partitions_to_generate = self._LOWEST_SAFE_CONCURRENCY_LEVEL // 2

        self._concurrent_source = ConcurrentSource.create(
            num_workers=concurrency_level,
            initial_number_of_partitions_to_generate=initial_number_of_partitions_to_generate,
            logger=self.logger,
            slice_logger=self._slice_logger,
            queue=queue,
            message_repository=self._message_repository,
        )

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

    def _fix_source_type(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix the source type in the manifest. This is necessary because the source type is not always set in the manifest.
        """
        if "type" not in manifest:
            manifest["type"] = "DeclarativeSource"

        return manifest

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
            control_message = create_connector_config_control_message(mutable_config)
            print(orjson.dumps(AirbyteMessageSerializer.dump(control_message)).decode())
        self._spec_component.transform_config(mutable_config)
        return mutable_config

    def configure(self, config: Mapping[str, Any], temp_dir: str) -> Mapping[str, Any]:
        config = self._config or config
        return super().configure(config, temp_dir)

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

    def deprecation_warnings(self) -> List[ConnectorBuilderLogMessage]:
        return self._constructor.get_model_deprecations()

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[List[AirbyteStateMessage]] = None,
    ) -> Iterator[AirbyteMessage]:
        selected_concurrent_streams = self._select_streams(
            streams=self.streams(config=self._config),  # type: ignore  # We are migrating away from the DeclarativeStream implementation and streams() only returns the concurrent-compatible AbstractStream. To preserve compatibility, we retain the existing method interface
            configured_catalog=catalog,
        )

        # It would appear that passing in an empty set of streams causes an infinite loop in ConcurrentReadProcessor.
        # This is also evident in concurrent_source_adapter.py so I'll leave this out of scope to fix for now
        if len(selected_concurrent_streams) > 0:
            yield from self._concurrent_source.read(selected_concurrent_streams)

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        return AirbyteCatalog(
            streams=[stream.as_airbyte_stream() for stream in self.streams(config=self._config)]
        )

    # todo: add PR comment about whether we can change the signature to List[AbstractStream]
    def streams(self, config: Mapping[str, Any]) -> List[AbstractStream]:  # type: ignore  # we are migrating away from the AbstractSource and are expecting that this will only be called by ConcurrentDeclarativeSource or the Connector Builder
        """
        The `streams` method is used as part of the AbstractSource in the following cases:
        * ConcurrentDeclarativeSource.check -> ManifestDeclarativeSource.check -> AbstractSource.check -> DeclarativeSource.check_connection -> CheckStream.check_connection -> streams
        * ConcurrentDeclarativeSource.read -> AbstractSource.read -> streams (note that we filter for a specific catalog which excludes concurrent streams so not all streams actually read from all the streams returned by `streams`)
        Note that `super.streams(config)` is also called when splitting the streams between concurrent or not in `_group_streams`.

        In both case, we will assume that calling the DeclarativeStream is perfectly fine as the result for these is the same regardless of if it is a DeclarativeStream or a DefaultStream (concurrent). This should simply be removed once we have moved away from the mentioned code paths above.
        """

        if self._spec_component:
            self._spec_component.validate_config(self._config)

        stream_configs = self._stream_configs(self._source_config) + self.dynamic_streams

        api_budget_model = self._source_config.get("api_budget")
        if api_budget_model:
            self._constructor.set_api_budget(api_budget_model, self._config)

        source_streams = [
            self._constructor.create_component(
                (
                    StateDelegatingStreamModel
                    if stream_config.get("type") == StateDelegatingStreamModel.__name__
                    else DeclarativeStreamModel
                ),
                stream_config,
                self._config,
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
        return (
            self._spec_component.generate_spec() if self._spec_component else super().spec(logger)
        )

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        check = self._source_config.get("check")
        if not check:
            raise ValueError(f"Missing 'check' component definition within the manifest.")

        if "type" not in check:
            check["type"] = "CheckStream"
        connection_checker = self._constructor.create_component(
            COMPONENTS_CHECKER_TYPE_MAPPING[check["type"]],
            check,
            dict(),
            emit_connector_builder_messages=self._emit_connector_builder_messages,
        )
        if not isinstance(connection_checker, ConnectionChecker):
            raise ValueError(
                f"Expected to generate a ConnectionChecker component, but received {connection_checker.__class__}"
            )

        check_succeeded, error = connection_checker.check_connection(self, logger, self._config)
        if not check_succeeded:
            return AirbyteConnectionStatus(status=Status.FAILED, message=repr(error))
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    @property
    def dynamic_streams(self) -> List[Dict[str, Any]]:
        return self._dynamic_stream_configs(
            manifest=self._source_config,
            with_dynamic_stream_name=True,
        )

    def _stream_configs(self, manifest: Mapping[str, Any]) -> List[Dict[str, Any]]:
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

                if interpolated_boolean.eval(config=self._config):
                    stream_configs.extend(current_stream_config.get("streams", []))
            else:
                if "type" not in current_stream_config:
                    current_stream_config["type"] = "DeclarativeStream"
                stream_configs.append(current_stream_config)
        return stream_configs

    def _dynamic_stream_configs(
        self,
        manifest: Mapping[str, Any],
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
                    config=self._config,
                    stream_name=dynamic_definition.get("name"),
                )
            else:
                components_resolver = self._constructor.create_component(
                    model_type=COMPONENTS_RESOLVER_TYPE_MAPPING[resolver_type],
                    component_definition=components_resolver_config,
                    config=self._config,
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

    def _select_streams(
        self, streams: List[AbstractStream], configured_catalog: ConfiguredAirbyteCatalog
    ) -> List[AbstractStream]:
        stream_name_to_instance: Mapping[str, AbstractStream] = {s.name: s for s in streams}
        abstract_streams: List[AbstractStream] = []
        for configured_stream in configured_catalog.streams:
            stream_instance = stream_name_to_instance.get(configured_stream.stream.name)
            if stream_instance:
                abstract_streams.append(stream_instance)
            else:
                # Previous behavior in the legacy synchronous CDK was to also raise an error TRACE message if
                # the source was configured with raise_exception_on_missing_stream=True. This was used on very
                # few sources like facebook-marketing and google-ads. We decided not to port this feature over,
                # but we can do so if we feel it necessary. With the current behavior,we should still result
                # in a partial failure since missing streams will be marked as INCOMPLETE.
                self._message_repository.emit_message(
                    as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.INCOMPLETE)
                )
        return abstract_streams
