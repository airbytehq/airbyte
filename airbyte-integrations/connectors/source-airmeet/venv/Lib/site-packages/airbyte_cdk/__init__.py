# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
"""
# Welcome to the Airbyte Python CDK!

The Airbyte Python CDK is a Python library that provides a set of tools to help you build
connectors for the Airbyte platform.

## Building Source Connectors

To build a source connector, you will want to refer to
the following classes and modules:

- `airbyte_cdk.sources`
- `airbyte_cdk.sources.concurrent_source`
- `airbyte_cdk.sources.config`
- `airbyte_cdk.sources.file_based`
- `airbyte_cdk.sources.streams`

## Building Destination Connectors

To build a destination connector, you will want to refer to
the following classes and modules:

- `airbyte_cdk.destinations`
- `airbyte_cdk.destinations.Destination`
- `airbyte_cdk.destinations.vector_db_based`

## Working with Airbyte Protocol Models

The Airbyte CDK provides a set of classes that help you work with the Airbyte protocol models:

- `airbyte_cdk.models.airbyte_protocol`
- `airbyte_cdk.models.airbyte_protocol_serializers`

## Using the CLI (`airbyte_cdk.cli`)

The Airbyte CDK provides two command-line interfaces (CLIs) for interacting with the framework.

- `airbyte-cdk`: This is the main CLI for the Airbyte CDK. It provides commands for building
  and testing connectors, as well as other utilities. See the `airbyte_cdk.cli.airbyte_cdk` module
  for more details.
- `source-declarative-manifest`: This command allows you to run declarative manifests directly.
  See the `airbyte_cdk.cli.source_declarative_manifest` module for more details.

---

API Reference

---

"""

# Warning: The below imports are not stable and will cause circular
# dependencies if auto-sorted with isort. Please keep them in the same order.
# TODO: Submodules should import from lower-level modules, rather than importing from here.
# Imports should also be placed in `if TYPE_CHECKING` blocks if they are only used as type
# hints - again, to avoid circular dependencies.
# Once those issues are resolved, the below can be sorted with isort.
import dunamai as _dunamai

from .config_observation import (
    create_connector_config_control_message,
    emit_configuration_as_airbyte_control_message,
)
from .connector import BaseConnector, Connector
from .destinations import Destination
from .entrypoint import AirbyteEntrypoint, launch
from .legacy.sources.declarative.declarative_stream import DeclarativeStream
from .legacy.sources.declarative.incremental import DatetimeBasedCursor
from .logger import AirbyteLogFormatter, init_logger
from .models import (
    AdvancedAuth,
    AirbyteConnectionStatus,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    FailureType,
    Level,
    OAuthConfigSpecification,
    OrchestratorType,
    Status,
    SyncMode,
    Type,
)
from .sources import AbstractSource, Source
from .sources.concurrent_source.concurrent_source import ConcurrentSource
from .sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from .sources.config import BaseConfig
from .sources.connector_state_manager import ConnectorStateManager
from .sources.declarative.auth import DeclarativeOauth2Authenticator
from .sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
from .sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from .sources.declarative.auth.token import (
    ApiKeyAuthenticator,
    BasicHttpAuthenticator,
    BearerAuthenticator,
)
from .sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from .sources.declarative.decoders import Decoder, JsonDecoder
from .sources.declarative.exceptions import ReadException
from .sources.declarative.extractors import DpathExtractor, RecordSelector
from .sources.declarative.extractors.record_extractor import RecordExtractor
from .sources.declarative.extractors.record_filter import RecordFilter
from .sources.declarative.interpolation import InterpolatedBoolean, InterpolatedString
from .sources.declarative.migrations.legacy_to_per_partition_state_migration import (
    LegacyToPerPartitionStateMigration,
)
from .sources.declarative.partition_routers import (
    CartesianProductStreamSlicer,
    SinglePartitionRouter,
    SubstreamPartitionRouter,
)
from .sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from .sources.declarative.requesters import HttpRequester, Requester
from .sources.declarative.requesters.error_handlers import BackoffStrategy
from .sources.declarative.requesters.paginators import DefaultPaginator, PaginationStrategy
from .sources.declarative.requesters.paginators.strategies import (
    CursorPaginationStrategy,
    OffsetIncrement,
    PageIncrement,
    StopConditionPaginationStrategyDecorator,
)
from .sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from .sources.declarative.requesters.request_options.default_request_options_provider import (
    DefaultRequestOptionsProvider,
)
from .sources.declarative.requesters.request_options.interpolated_request_input_provider import (
    InterpolatedRequestInputProvider,
)
from .sources.declarative.requesters.requester import HttpMethod
from .sources.declarative.retrievers import SimpleRetriever
from .sources.declarative.schema import JsonFileSchemaLoader
from .sources.declarative.transformations.add_fields import AddedFieldDefinition, AddFields
from .sources.declarative.transformations.transformation import RecordTransformation
from .sources.declarative.types import FieldPointer
from .sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from .sources.message import InMemoryMessageRepository, MessageRepository
from .sources.source import TState
from .sources.streams.availability_strategy import AvailabilityStrategy
from .sources.streams.call_rate import (
    AbstractAPIBudget,
    CachedLimiterSession,
    HttpAPIBudget,
    HttpRequestMatcher,
    LimiterSession,
    MovingWindowCallRatePolicy,
    Rate,
)
from .sources.streams.checkpoint import Cursor as LegacyCursor
from .sources.streams.checkpoint import ResumableFullRefreshCursor
from .sources.streams.concurrent.adapters import StreamFacade
from .sources.streams.concurrent.cursor import (
    ConcurrentCursor,
    Cursor,
    CursorField,
    FinalStateCursor,
)
from .sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    EpochValueConcurrentStreamStateConverter,
    IsoMillisConcurrentStreamStateConverter,
)
from .sources.streams.core import IncrementalMixin, Stream, package_name_from_class
from .sources.streams.http import HttpStream, HttpSubStream
from .sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from .sources.streams.http.exceptions import (
    BaseBackoffException,
    DefaultBackoffException,
    UserDefinedBackoffException,
)
from .sources.streams.http.rate_limiting import default_backoff_handler
from .sources.streams.http.requests_native_auth import (
    Oauth2Authenticator,
    SingleUseRefreshTokenOauth2Authenticator,
    TokenAuthenticator,
)
from .sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from .sources.types import Config, Record, StreamSlice
from .sources.utils import casing
from .sources.utils.schema_helpers import (
    InternalConfig,
    ResourceSchemaLoader,
    check_config_against_spec_or_exit,
    expand_refs,
    split_config,
)
from .sources.utils.transform import TransformConfig, TypeTransformer
from .utils import AirbyteTracedException, is_cloud_environment
from .utils.constants import ENV_REQUEST_CACHE_PATH
from .utils.event_timing import create_timer
from .utils.oneof_option_config import OneOfOptionConfig
from .utils.spec_schema_transformations import resolve_refs
from .utils.stream_status_utils import as_airbyte_message

__all__ = [
    # Availability strategy
    "AvailabilityStrategy",
    "HttpAvailabilityStrategy",
    # Checkpoint
    "LegacyCursor",
    "ResumableFullRefreshCursor",
    # Concurrent
    "ConcurrentCursor",
    "ConcurrentSource",
    "ConcurrentSourceAdapter",
    "Cursor",
    "CursorField",
    "DEFAULT_CONCURRENCY",
    "EpochValueConcurrentStreamStateConverter",
    "FinalStateCursor",
    "IsoMillisConcurrentStreamStateConverter",
    "StreamFacade",
    # Config observation
    "create_connector_config_control_message",
    "emit_configuration_as_airbyte_control_message",
    # Connector
    "AbstractSource",
    "BaseConfig",
    "BaseConnector",
    "Connector",
    "Destination",
    "Source",
    "TState",
    # Declarative
    "AddFields",
    "AddedFieldDefinition",
    "ApiKeyAuthenticator",
    "BackoffStrategy",
    "BasicHttpAuthenticator",
    "BearerAuthenticator",
    "CartesianProductStreamSlicer",
    "CursorPaginationStrategy",
    "DatetimeBasedCursor",
    "DeclarativeAuthenticator",
    "DeclarativeOauth2Authenticator",
    "DeclarativeSingleUseRefreshTokenOauth2Authenticator",
    "DeclarativeStream",
    "Decoder",
    "DefaultPaginator",
    "DefaultRequestOptionsProvider",
    "DpathExtractor",
    "FieldPointer",
    "HttpMethod",
    "HttpRequester",
    "InterpolatedBoolean",
    "InterpolatedRequestInputProvider",
    "InterpolatedString",
    "JsonDecoder",
    "JsonFileSchemaLoader",
    "LegacyToPerPartitionStateMigration",
    "MinMaxDatetime",
    "NoAuth",
    "OffsetIncrement",
    "PageIncrement",
    "PaginationStrategy",
    "ParentStreamConfig",
    "ReadException",
    "RecordExtractor",
    "RecordFilter",
    "RecordSelector",
    "RecordTransformation",
    "RequestOption",
    "RequestOptionType",
    "Requester",
    "ResponseStatus",
    "SimpleRetriever",
    "SinglePartitionRouter",
    "StopConditionPaginationStrategyDecorator",
    "StreamSlice",
    "SubstreamPartitionRouter",
    "YamlDeclarativeSource",
    # Entrypoint
    "launch",
    "AirbyteEntrypoint",
    # HTTP
    "AbstractAPIBudget",
    "AbstractHeaderAuthenticator",
    "BaseBackoffException",
    "CachedLimiterSession",
    "DefaultBackoffException",
    "default_backoff_handler",
    "HttpAPIBudget",
    "HttpAuthenticator",
    "HttpRequestMatcher",
    "HttpStream",
    "HttpSubStream",
    "LimiterSession",
    "MovingWindowCallRatePolicy",
    "MultipleTokenAuthenticator",
    "Oauth2Authenticator",
    "Rate",
    "SingleUseRefreshTokenOauth2Authenticator",
    "TokenAuthenticator",
    "UserDefinedBackoffException",
    # Logger
    "AirbyteLogFormatter",
    "init_logger",
    # Protocol classes
    "AirbyteStream",
    "AirbyteConnectionStatus",
    "AirbyteMessage",
    "ConfiguredAirbyteCatalog",
    "Status",
    "Type",
    "OrchestratorType",
    "ConfiguredAirbyteStream",
    "DestinationSyncMode",
    "SyncMode",
    "FailureType",
    "AdvancedAuth",
    "AirbyteLogMessage",
    "OAuthConfigSpecification",
    "ConnectorSpecification",
    "Level",
    "AirbyteRecordMessage",
    # Repository
    "InMemoryMessageRepository",
    "MessageRepository",
    # State management
    "ConnectorStateManager",
    # Stream
    "IncrementalMixin",
    "Stream",
    "StreamData",
    "package_name_from_class",
    # Utils
    "AirbyteTracedException",
    "is_cloud_environment",
    "casing",
    "InternalConfig",
    "ResourceSchemaLoader",
    "check_config_against_spec_or_exit",
    "split_config",
    "TransformConfig",
    "TypeTransformer",
    "ENV_REQUEST_CACHE_PATH",
    "create_timer",
    "OneOfOptionConfig",
    "resolve_refs",
    "as_airbyte_message",
    # Types
    "Config",
    "Record",
    "Source",
    "StreamSlice",
]

__version__: str
"""Version generated by poetry dynamic versioning during publish.

When running in development, dunamai will calculate a new prerelease version
from existing git release tag info.
"""

try:
    __version__ = _dunamai.get_version(
        "airbyte-cdk",
        third_choice=_dunamai.Version.from_any_vcs,
        fallback=_dunamai.Version("0.0.0+dev"),
    ).serialize()
except:
    __version__ = "0.0.0+dev"
