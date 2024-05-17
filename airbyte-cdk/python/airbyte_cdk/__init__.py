#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from importlib import metadata

from destinations import Destination
from models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type, FailureType, AirbyteStream, AdvancedAuth, DestinationSyncMode, ConnectorSpecification, OAuthConfigSpecification, OrchestratorType, ConfiguredAirbyteStream, SyncMode, AirbyteLogMessage, Level, AirbyteRecordMessage
from destinations.vector_db_based.config import VectorDBConfigModel
from destinations.vector_db_based.document_processor import DocumentProcessor, Chunk
from destinations.vector_db_based.embedder import Embedder, create_from_config, OPEN_AI_VECTOR_SIZE, OPEN_AI_TOKEN_LIMIT, FakeEmbedder, OpenAIEmbedder
from destinations.vector_db_based.indexer import Indexer
from destinations.vector_db_based.writer import Writer
from destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from destinations.vector_db_based.utils import create_chunks, create_stream_identifier, format_exception

from sources import Source
from config_observation import create_connector_config_control_message, emit_configuration_as_airbyte_control_message
from connector import BaseConnector, Connector

from destinations.vector_db_based import FakeEmbeddingConfigModel, OpenAIEmbeddingConfigModel
from destinations.vector_db_based.test_utils import BaseIntegrationTest

from entrypoint import launch, AirbyteEntrypoint

from logger import AirbyteLogFormatter, init_logger
from sources import AbstractSource
from sources.concurrent_source.concurrent_source import ConcurrentSource
from sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from sources.config import BaseConfig
from sources.types import Config, Record, StreamSlice
from sources.connector_state_manager import ConnectorStateManager
from sources.declarative.auth import DeclarativeOauth2Authenticator
from sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from sources.declarative.auth.declarative_authenticator import NoAuth
from sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator, ApiKeyAuthenticator
from sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from sources.declarative.declarative_stream import DeclarativeStream
from sources.declarative.decoders import Decoder, JsonDecoder
from sources.declarative.exceptions import ReadException
from sources.declarative.extractors import DpathExtractor, RecordSelector
from sources.declarative.extractors.record_extractor import RecordExtractor
from sources.declarative.extractors.record_filter import RecordFilter
from sources.declarative.incremental import DatetimeBasedCursor
from sources.declarative.interpolation import InterpolatedString, InterpolatedBoolean
from sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from sources.declarative.migrations.legacy_to_per_partition_state_migration import LegacyToPerPartitionStateMigration

from sources.declarative.partition_routers import SinglePartitionRouter, SubstreamPartitionRouter
from sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from sources.declarative.requesters import Requester, HttpRequester

from sources.declarative.requesters.error_handlers import BackoffStrategy
from sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from sources.declarative.requesters.paginators import DefaultPaginator, PaginationStrategy
from sources.declarative.requesters.paginators.strategies import OffsetIncrement, CursorPaginationStrategy, PageIncrement, StopConditionPaginationStrategyDecorator

from sources.declarative.requesters.request_option import RequestOption, RequestOptionType

from sources.declarative.requesters.request_options.interpolated_request_input_provider import InterpolatedRequestInputProvider
from sources.declarative.requesters.requester import HttpMethod
from sources.declarative.retrievers import SimpleRetriever
from sources.declarative.schema import JsonFileSchemaLoader
from sources.declarative.stream_slicers import CartesianProductStreamSlicer
from sources.declarative.transformations.add_fields import AddFields, AddedFieldDefinition
from sources.declarative.transformations.transformation import RecordTransformation
from sources.declarative.types import FieldPointer
from sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from sources.file_based.config.csv_format import CsvFormat
from sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from sources.file_based.config.jsonl_format import JsonlFormat
from sources.file_based.exceptions import CustomFileBasedException, ErrorListingFiles, FileBasedSourceError
from sources.file_based.file_based_source import DEFAULT_CONCURRENCY, FileBasedSource
from sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from sources.file_based.remote_file import RemoteFile
from sources.file_based.stream.cursor import DefaultFileBasedCursor
from sources.message import InMemoryMessageRepository, MessageRepository
from sources.source import TState
from sources.streams.availability_strategy import AvailabilityStrategy
from sources.streams.call_rate import AbstractAPIBudget, HttpAPIBudget, HttpRequestMatcher, MovingWindowCallRatePolicy, Rate, CachedLimiterSession, LimiterSession
from sources.streams.concurrent.adapters import StreamFacade
from sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, FinalStateCursor
from sources.streams.concurrent.cursor import Cursor
from sources.streams.concurrent.state_converters.datetime_stream_state_converter import EpochValueConcurrentStreamStateConverter, IsoMillisConcurrentStreamStateConverter
from sources.streams.core import Stream, IncrementalMixin, package_name_from_class
from sources.streams.http import HttpStream, HttpSubStream
from sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from sources.streams.http.exceptions import BaseBackoffException, DefaultBackoffException, UserDefinedBackoffException
from sources.streams.http.rate_limiting import default_backoff_handler
from sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator, SingleUseRefreshTokenOauth2Authenticator
from sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from sources.utils import casing
from sources.utils.schema_helpers import InternalConfig, ResourceSchemaLoader, check_config_against_spec_or_exit, split_config, expand_refs
from sources.utils.transform import TransformConfig, TypeTransformer
import test
from utils import AirbyteTracedException, is_cloud_environment
from utils.constants import ENV_REQUEST_CACHE_PATH
from utils.event_timing import create_timer
from utils.oneof_option_config import OneOfOptionConfig
from utils.spec_schema_transformations import resolve_refs
from utils.stream_status_utils import as_airbyte_message


__all__ = [
    # Availability strategy
    "AvailabilityStrategy",
    "HttpAvailabilityStrategy",

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
    "DatetimeBasedCursor"
    "DeclarativeAuthenticator",
    "DeclarativeOauth2Authenticator",
    "DeclarativeSingleUseRefreshTokenOauth2Authenticator",
    "DeclarativeStream",
    "Decoder",
    "DefaultPaginator",
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
    "ManifestDeclarativeSource",
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

    # File based
    "AbstractFileBasedSpec",
    "AbstractFileBasedStreamReader",
    "CsvFormat",
    "CustomFileBasedException",
    "DefaultFileBasedCursor",
    "ErrorListingFiles",
    "FileBasedSource",
    "FileBasedSourceError",
    "FileBasedStreamConfig",
    "FileReadMode",
    "JsonlFormat",
    "RemoteFile",

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
    "MultipleTokenAuthenticator"
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
    "AirbyteConnectionStatus", "AirbyteMessage", "ConfiguredAirbyteCatalog", "Status", "Type",
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

    # Vector destinations
    "BaseIntegrationTest",
    "Chunk",
    "create_chunks",
    "create_from_config",
    "create_stream_identifier",
    "DocumentProcessor",
    "Embedder",
    "FakeEmbedder",
    "FakeEmbeddingConfigModel",
    "format_exception",
    "Indexer",
    "METADATA_RECORD_ID_FIELD",
    "METADATA_STREAM_FIELD",
    "OPEN_AI_TOKEN_LIMIT",
    "OPEN_AI_VECTOR_SIZE",
    "OpenAIEmbedder",
    "OpenAIEmbeddingConfigModel",
    "VectorDBConfigModel",
    "Writer",

    # export the test package separately
    "test",

]

__version__ = metadata.version("airbyte_cdk")
