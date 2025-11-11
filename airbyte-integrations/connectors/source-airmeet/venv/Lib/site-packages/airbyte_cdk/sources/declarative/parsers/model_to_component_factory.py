#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import datetime
import importlib
import inspect
import logging
import re
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Type,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from airbyte_protocol_dataclasses.models import ConfiguredAirbyteStream
from isodate import parse_duration
from pydantic.v1 import BaseModel
from requests import Response

from airbyte_cdk.connector_builder.models import (
    LogMessage as ConnectorBuilderLogMessage,
)
from airbyte_cdk.legacy.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.legacy.sources.declarative.incremental import (
    DatetimeBasedCursor,
)
from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    FailureType,
    Level,
    StreamDescriptor,
)
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.declarative.async_job.job_orchestrator import AsyncJobOrchestrator
from airbyte_cdk.sources.declarative.async_job.job_tracker import JobTracker
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository
from airbyte_cdk.sources.declarative.async_job.status import AsyncJobStatus
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator, JwtAuthenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import (
    DeclarativeAuthenticator,
    NoAuth,
)
from airbyte_cdk.sources.declarative.auth.jwt import JwtAlgorithm
from airbyte_cdk.sources.declarative.auth.oauth import (
    DeclarativeSingleUseRefreshTokenOauth2Authenticator,
)
from airbyte_cdk.sources.declarative.auth.selective_authenticator import SelectiveAuthenticator
from airbyte_cdk.sources.declarative.auth.token import (
    ApiKeyAuthenticator,
    BasicHttpAuthenticator,
    BearerAuthenticator,
    LegacySessionTokenAuthenticator,
)
from airbyte_cdk.sources.declarative.auth.token_provider import (
    InterpolatedStringTokenProvider,
    SessionTokenProvider,
    TokenProvider,
)
from airbyte_cdk.sources.declarative.checks import (
    CheckDynamicStream,
    CheckStream,
    DynamicStreamCheckConfig,
)
from airbyte_cdk.sources.declarative.concurrency_level import ConcurrencyLevel
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.decoders import (
    Decoder,
    IterableDecoder,
    JsonDecoder,
    PaginationDecoderDecorator,
    XmlDecoder,
    ZipfileDecoder,
)
from airbyte_cdk.sources.declarative.decoders.composite_raw_decoder import (
    CompositeRawDecoder,
    CsvParser,
    GzipParser,
    JsonLineParser,
    JsonParser,
    Parser,
)
from airbyte_cdk.sources.declarative.extractors import (
    DpathExtractor,
    RecordFilter,
    RecordSelector,
    ResponseToFileExtractor,
)
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import (
    ClientSideIncrementalRecordFilterDecorator,
)
from airbyte_cdk.sources.declarative.incremental import (
    ConcurrentCursorFactory,
    ConcurrentPerPartitionCursor,
)
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.migrations.legacy_to_per_partition_state_migration import (
    LegacyToPerPartitionStateMigration,
)
from airbyte_cdk.sources.declarative.models import (
    CustomStateMigration,
    PaginationResetLimits,
)
from airbyte_cdk.sources.declarative.models.base_model_with_deprecations import (
    DEPRECATION_LOGS_TAG,
    BaseModelWithDeprecations,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    Action1 as PaginationResetActionModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    AddedFieldDefinition as AddedFieldDefinitionModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    AddFields as AddFieldsModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ApiKeyAuthenticator as ApiKeyAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    AsyncJobStatusMap as AsyncJobStatusMapModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    AsyncRetriever as AsyncRetrieverModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    BasicHttpAuthenticator as BasicHttpAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    BearerAuthenticator as BearerAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CheckDynamicStream as CheckDynamicStreamModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CheckStream as CheckStreamModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ComplexFieldType as ComplexFieldTypeModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ComponentMappingDefinition as ComponentMappingDefinitionModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CompositeErrorHandler as CompositeErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConcurrencyLevel as ConcurrencyLevelModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConfigAddFields as ConfigAddFieldsModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConfigComponentsResolver as ConfigComponentsResolverModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConfigMigration as ConfigMigrationModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConfigRemapField as ConfigRemapFieldModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConfigRemoveFields as ConfigRemoveFieldsModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConstantBackoffStrategy as ConstantBackoffStrategyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CsvDecoder as CsvDecoderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CursorPagination as CursorPaginationModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomAuthenticator as CustomAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomBackoffStrategy as CustomBackoffStrategyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomConfigTransformation as CustomConfigTransformationModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomDecoder as CustomDecoderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomErrorHandler as CustomErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomPaginationStrategy as CustomPaginationStrategyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomPartitionRouter as CustomPartitionRouterModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomRecordExtractor as CustomRecordExtractorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomRecordFilter as CustomRecordFilterModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomRequester as CustomRequesterModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomRetriever as CustomRetrieverModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomSchemaLoader as CustomSchemaLoader,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomSchemaNormalization as CustomSchemaNormalizationModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomTransformation as CustomTransformationModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomValidationStrategy as CustomValidationStrategyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DatetimeBasedCursor as DatetimeBasedCursorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DeclarativeStream as DeclarativeStreamModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultPaginator as DefaultPaginatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DpathExtractor as DpathExtractorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DpathFlattenFields as DpathFlattenFieldsModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DpathValidator as DpathValidatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DynamicSchemaLoader as DynamicSchemaLoaderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DynamicStreamCheckConfig as DynamicStreamCheckConfigModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ExponentialBackoffStrategy as ExponentialBackoffStrategyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    FileUploader as FileUploaderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    FixedWindowCallRatePolicy as FixedWindowCallRatePolicyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    FlattenFields as FlattenFieldsModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    GroupByKeyMergeStrategy as GroupByKeyMergeStrategyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    GroupingPartitionRouter as GroupingPartitionRouterModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    GzipDecoder as GzipDecoderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    HTTPAPIBudget as HTTPAPIBudgetModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    HttpComponentsResolver as HttpComponentsResolverModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    HttpRequester as HttpRequesterModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    HttpRequestRegexMatcher as HttpRequestRegexMatcherModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    HttpResponseFilter as HttpResponseFilterModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    IncrementingCountCursor as IncrementingCountCursorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    InlineSchemaLoader as InlineSchemaLoaderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    IterableDecoder as IterableDecoderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    JsonDecoder as JsonDecoderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    JsonFileSchemaLoader as JsonFileSchemaLoaderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    JsonlDecoder as JsonlDecoderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    JsonSchemaPropertySelector as JsonSchemaPropertySelectorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    JwtAuthenticator as JwtAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    JwtHeaders as JwtHeadersModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    JwtPayload as JwtPayloadModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    KeysReplace as KeysReplaceModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    KeysToLower as KeysToLowerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    KeysToSnakeCase as KeysToSnakeCaseModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    LegacySessionTokenAuthenticator as LegacySessionTokenAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    LegacyToPerPartitionStateMigration as LegacyToPerPartitionStateMigrationModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ListPartitionRouter as ListPartitionRouterModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    MinMaxDatetime as MinMaxDatetimeModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    MovingWindowCallRatePolicy as MovingWindowCallRatePolicyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    NoAuth as NoAuthModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    NoPagination as NoPaginationModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    OAuthAuthenticator as OAuthAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    OffsetIncrement as OffsetIncrementModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    PageIncrement as PageIncrementModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    PaginationReset as PaginationResetModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ParametrizedComponentsResolver as ParametrizedComponentsResolverModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ParentStreamConfig as ParentStreamConfigModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    PredicateValidator as PredicateValidatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    PropertiesFromEndpoint as PropertiesFromEndpointModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    PropertyChunking as PropertyChunkingModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    PropertyLimitType as PropertyLimitTypeModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    QueryProperties as QueryPropertiesModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    Rate as RateModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    RecordFilter as RecordFilterModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    RecordSelector as RecordSelectorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    RemoveFields as RemoveFieldsModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    RequestOption as RequestOptionModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    RequestPath as RequestPathModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ResponseToFileExtractor as ResponseToFileExtractorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    SchemaNormalization as SchemaNormalizationModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    SchemaTypeIdentifier as SchemaTypeIdentifierModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    SelectiveAuthenticator as SelectiveAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    SessionTokenAuthenticator as SessionTokenAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    SimpleRetriever as SimpleRetrieverModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import Spec as SpecModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    StateDelegatingStream as StateDelegatingStreamModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    StreamConfig as StreamConfigModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    SubstreamPartitionRouter as SubstreamPartitionRouterModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    TypesMap as TypesMapModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    UnlimitedCallRatePolicy as UnlimitedCallRatePolicyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ValidateAdheresToSchema as ValidateAdheresToSchemaModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ValueType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    WaitTimeFromHeader as WaitTimeFromHeaderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    WaitUntilTimeFromHeader as WaitUntilTimeFromHeaderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    XmlDecoder as XmlDecoderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ZipfileDecoder as ZipfileDecoderModel,
)
from airbyte_cdk.sources.declarative.partition_routers import (
    CartesianProductStreamSlicer,
    GroupingPartitionRouter,
    ListPartitionRouter,
    PartitionRouter,
    SinglePartitionRouter,
    SubstreamPartitionRouter,
)
from airbyte_cdk.sources.declarative.partition_routers.async_job_partition_router import (
    AsyncJobPartitionRouter,
)
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import (
    ParentStreamConfig,
)
from airbyte_cdk.sources.declarative.requesters import HttpRequester, RequestOption
from airbyte_cdk.sources.declarative.requesters.error_handlers import (
    CompositeErrorHandler,
    DefaultErrorHandler,
    HttpResponseFilter,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import (
    ConstantBackoffStrategy,
    ExponentialBackoffStrategy,
    WaitTimeFromHeaderBackoffStrategy,
    WaitUntilTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.http_job_repository import AsyncHttpJobRepository
from airbyte_cdk.sources.declarative.requesters.paginators import (
    DefaultPaginator,
    NoPagination,
    PaginatorTestReadDecorator,
)
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import (
    CursorPaginationStrategy,
    CursorStopCondition,
    OffsetIncrement,
    PageIncrement,
    StopConditionPaginationStrategyDecorator,
)
from airbyte_cdk.sources.declarative.requesters.query_properties import (
    PropertiesFromEndpoint,
    PropertyChunking,
    QueryProperties,
)
from airbyte_cdk.sources.declarative.requesters.query_properties.property_chunking import (
    PropertyLimitType,
)
from airbyte_cdk.sources.declarative.requesters.query_properties.property_selector import (
    JsonSchemaPropertySelector,
)
from airbyte_cdk.sources.declarative.requesters.query_properties.strategies import (
    GroupByKey,
)
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options import (
    DatetimeBasedRequestOptionsProvider,
    DefaultRequestOptionsProvider,
    InterpolatedRequestOptionsProvider,
    RequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.request_options.per_partition_request_option_provider import (
    PerPartitionRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.request_path import RequestPath
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod, Requester
from airbyte_cdk.sources.declarative.resolvers import (
    ComponentMappingDefinition,
    ConfigComponentsResolver,
    HttpComponentsResolver,
    ParametrizedComponentsResolver,
    StreamConfig,
    StreamParametersDefinition,
)
from airbyte_cdk.sources.declarative.retrievers import (
    AsyncRetriever,
    LazySimpleRetriever,
    SimpleRetriever,
)
from airbyte_cdk.sources.declarative.retrievers.file_uploader import (
    ConnectorBuilderFileUploader,
    DefaultFileUploader,
    FileUploader,
    LocalFileSystemFileWriter,
    NoopFileWriter,
)
from airbyte_cdk.sources.declarative.retrievers.pagination_tracker import PaginationTracker
from airbyte_cdk.sources.declarative.schema import (
    ComplexFieldType,
    DefaultSchemaLoader,
    DynamicSchemaLoader,
    InlineSchemaLoader,
    JsonFileSchemaLoader,
    SchemaLoader,
    SchemaTypeIdentifier,
    TypesMap,
)
from airbyte_cdk.sources.declarative.schema.caching_schema_loader_decorator import (
    CachingSchemaLoaderDecorator,
)
from airbyte_cdk.sources.declarative.schema.composite_schema_loader import CompositeSchemaLoader
from airbyte_cdk.sources.declarative.spec import ConfigMigration, Spec
from airbyte_cdk.sources.declarative.stream_slicers import (
    StreamSlicer,
    StreamSlicerTestReadDecorator,
)
from airbyte_cdk.sources.declarative.stream_slicers.declarative_partition_generator import (
    DeclarativePartitionFactory,
    StreamSlicerPartitionGenerator,
)
from airbyte_cdk.sources.declarative.transformations import (
    AddFields,
    RecordTransformation,
    RemoveFields,
)
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.transformations.config_transformations import (
    ConfigAddFields,
    ConfigRemapField,
    ConfigRemoveFields,
)
from airbyte_cdk.sources.declarative.transformations.config_transformations.config_transformation import (
    ConfigTransformation,
)
from airbyte_cdk.sources.declarative.transformations.dpath_flatten_fields import (
    DpathFlattenFields,
    KeyTransformation,
)
from airbyte_cdk.sources.declarative.transformations.flatten_fields import (
    FlattenFields,
)
from airbyte_cdk.sources.declarative.transformations.keys_replace_transformation import (
    KeysReplaceTransformation,
)
from airbyte_cdk.sources.declarative.transformations.keys_to_lower_transformation import (
    KeysToLowerTransformation,
)
from airbyte_cdk.sources.declarative.transformations.keys_to_snake_transformation import (
    KeysToSnakeCaseTransformation,
)
from airbyte_cdk.sources.declarative.validators import (
    DpathValidator,
    PredicateValidator,
    ValidateAdheresToSchema,
)
from airbyte_cdk.sources.http_logger import format_http_message
from airbyte_cdk.sources.message import (
    InMemoryMessageRepository,
    LogAppenderMessageRepositoryDecorator,
    MessageRepository,
    NoopMessageRepository,
)
from airbyte_cdk.sources.message.repository import StateFilteringMessageRepository
from airbyte_cdk.sources.streams.call_rate import (
    APIBudget,
    FixedWindowCallRatePolicy,
    HttpAPIBudget,
    HttpRequestRegexMatcher,
    MovingWindowCallRatePolicy,
    Rate,
    UnlimitedCallRatePolicy,
)
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.clamping import (
    ClampingEndProvider,
    ClampingStrategy,
    DayClampingStrategy,
    MonthClampingStrategy,
    NoClamping,
    WeekClampingStrategy,
    Weekday,
)
from airbyte_cdk.sources.streams.concurrent.cursor import (
    ConcurrentCursor,
    Cursor,
    CursorField,
    FinalStateCursor,
)
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.concurrent.helpers import get_primary_key_from_stream
from airbyte_cdk.sources.streams.concurrent.partitions.stream_slicer import (
    StreamSlicer as ConcurrentStreamSlicer,
)
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    CustomFormatConcurrentStreamStateConverter,
    DateTimeStreamStateConverter,
)
from airbyte_cdk.sources.streams.concurrent.state_converters.incrementing_count_stream_state_converter import (
    IncrementingCountStreamStateConverter,
)
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.sources.types import Config
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

ComponentDefinition = Mapping[str, Any]

SCHEMA_TRANSFORMER_TYPE_MAPPING = {
    SchemaNormalizationModel.None_: TransformConfig.NoTransform,
    SchemaNormalizationModel.Default: TransformConfig.DefaultSchemaNormalization,
}
_NO_STREAM_SLICING = SinglePartitionRouter(parameters={})

# Ideally this should use the value defined in ConcurrentDeclarativeSource, but
# this would be a circular import
MAX_SLICES = 5

LOGGER = logging.getLogger(f"airbyte.model_to_component_factory")


class ModelToComponentFactory:
    EPOCH_DATETIME_FORMAT = "%s"

    def __init__(
        self,
        limit_pages_fetched_per_slice: Optional[int] = None,
        limit_slices_fetched: Optional[int] = None,
        emit_connector_builder_messages: bool = False,
        disable_retries: bool = False,
        disable_cache: bool = False,
        message_repository: Optional[MessageRepository] = None,
        connector_state_manager: Optional[ConnectorStateManager] = None,
        max_concurrent_async_job_count: Optional[int] = None,
        configured_catalog: Optional[ConfiguredAirbyteCatalog] = None,
    ):
        self._init_mappings()
        self._limit_pages_fetched_per_slice = limit_pages_fetched_per_slice
        self._limit_slices_fetched = limit_slices_fetched
        self._emit_connector_builder_messages = emit_connector_builder_messages
        self._disable_retries = disable_retries
        self._disable_cache = disable_cache
        self._message_repository = message_repository or InMemoryMessageRepository(
            self._evaluate_log_level(emit_connector_builder_messages)
        )
        self._stream_name_to_configured_stream = self._create_stream_name_to_configured_stream(
            configured_catalog
        )
        self._connector_state_manager = connector_state_manager or ConnectorStateManager()
        self._api_budget: Optional[Union[APIBudget, HttpAPIBudget]] = None
        self._job_tracker: JobTracker = JobTracker(max_concurrent_async_job_count or 1)
        # placeholder for deprecation warnings
        self._collected_deprecation_logs: List[ConnectorBuilderLogMessage] = []

    def _init_mappings(self) -> None:
        self.PYDANTIC_MODEL_TO_CONSTRUCTOR: Mapping[Type[BaseModel], Callable[..., Any]] = {
            AddedFieldDefinitionModel: self.create_added_field_definition,
            AddFieldsModel: self.create_add_fields,
            ApiKeyAuthenticatorModel: self.create_api_key_authenticator,
            BasicHttpAuthenticatorModel: self.create_basic_http_authenticator,
            BearerAuthenticatorModel: self.create_bearer_authenticator,
            CheckStreamModel: self.create_check_stream,
            DynamicStreamCheckConfigModel: self.create_dynamic_stream_check_config,
            CheckDynamicStreamModel: self.create_check_dynamic_stream,
            CompositeErrorHandlerModel: self.create_composite_error_handler,
            ConcurrencyLevelModel: self.create_concurrency_level,
            ConfigMigrationModel: self.create_config_migration,
            ConfigAddFieldsModel: self.create_config_add_fields,
            ConfigRemapFieldModel: self.create_config_remap_field,
            ConfigRemoveFieldsModel: self.create_config_remove_fields,
            ConstantBackoffStrategyModel: self.create_constant_backoff_strategy,
            CsvDecoderModel: self.create_csv_decoder,
            CursorPaginationModel: self.create_cursor_pagination,
            CustomAuthenticatorModel: self.create_custom_component,
            CustomBackoffStrategyModel: self.create_custom_component,
            CustomDecoderModel: self.create_custom_component,
            CustomErrorHandlerModel: self.create_custom_component,
            CustomRecordExtractorModel: self.create_custom_component,
            CustomRecordFilterModel: self.create_custom_component,
            CustomRequesterModel: self.create_custom_component,
            CustomRetrieverModel: self.create_custom_component,
            CustomSchemaLoader: self.create_custom_component,
            CustomSchemaNormalizationModel: self.create_custom_component,
            CustomStateMigration: self.create_custom_component,
            CustomPaginationStrategyModel: self.create_custom_component,
            CustomPartitionRouterModel: self.create_custom_component,
            CustomTransformationModel: self.create_custom_component,
            CustomValidationStrategyModel: self.create_custom_component,
            CustomConfigTransformationModel: self.create_custom_component,
            DatetimeBasedCursorModel: self.create_datetime_based_cursor,
            DeclarativeStreamModel: self.create_default_stream,
            DefaultErrorHandlerModel: self.create_default_error_handler,
            DefaultPaginatorModel: self.create_default_paginator,
            DpathExtractorModel: self.create_dpath_extractor,
            DpathValidatorModel: self.create_dpath_validator,
            ResponseToFileExtractorModel: self.create_response_to_file_extractor,
            ExponentialBackoffStrategyModel: self.create_exponential_backoff_strategy,
            SessionTokenAuthenticatorModel: self.create_session_token_authenticator,
            GroupByKeyMergeStrategyModel: self.create_group_by_key,
            HttpRequesterModel: self.create_http_requester,
            HttpResponseFilterModel: self.create_http_response_filter,
            InlineSchemaLoaderModel: self.create_inline_schema_loader,
            JsonDecoderModel: self.create_json_decoder,
            JsonlDecoderModel: self.create_jsonl_decoder,
            JsonSchemaPropertySelectorModel: self.create_json_schema_property_selector,
            GzipDecoderModel: self.create_gzip_decoder,
            KeysToLowerModel: self.create_keys_to_lower_transformation,
            KeysToSnakeCaseModel: self.create_keys_to_snake_transformation,
            KeysReplaceModel: self.create_keys_replace_transformation,
            FlattenFieldsModel: self.create_flatten_fields,
            DpathFlattenFieldsModel: self.create_dpath_flatten_fields,
            IterableDecoderModel: self.create_iterable_decoder,
            IncrementingCountCursorModel: self.create_incrementing_count_cursor,
            XmlDecoderModel: self.create_xml_decoder,
            JsonFileSchemaLoaderModel: self.create_json_file_schema_loader,
            DynamicSchemaLoaderModel: self.create_dynamic_schema_loader,
            SchemaTypeIdentifierModel: self.create_schema_type_identifier,
            TypesMapModel: self.create_types_map,
            ComplexFieldTypeModel: self.create_complex_field_type,
            JwtAuthenticatorModel: self.create_jwt_authenticator,
            LegacyToPerPartitionStateMigrationModel: self.create_legacy_to_per_partition_state_migration,
            ListPartitionRouterModel: self.create_list_partition_router,
            MinMaxDatetimeModel: self.create_min_max_datetime,
            NoAuthModel: self.create_no_auth,
            NoPaginationModel: self.create_no_pagination,
            OAuthAuthenticatorModel: self.create_oauth_authenticator,
            OffsetIncrementModel: self.create_offset_increment,
            PageIncrementModel: self.create_page_increment,
            ParentStreamConfigModel: self.create_parent_stream_config_with_substream_wrapper,
            PredicateValidatorModel: self.create_predicate_validator,
            PropertiesFromEndpointModel: self.create_properties_from_endpoint,
            PropertyChunkingModel: self.create_property_chunking,
            QueryPropertiesModel: self.create_query_properties,
            RecordFilterModel: self.create_record_filter,
            RecordSelectorModel: self.create_record_selector,
            RemoveFieldsModel: self.create_remove_fields,
            RequestPathModel: self.create_request_path,
            RequestOptionModel: self.create_request_option,
            LegacySessionTokenAuthenticatorModel: self.create_legacy_session_token_authenticator,
            SelectiveAuthenticatorModel: self.create_selective_authenticator,
            SimpleRetrieverModel: self.create_simple_retriever,
            StateDelegatingStreamModel: self.create_state_delegating_stream,
            SpecModel: self.create_spec,
            SubstreamPartitionRouterModel: self.create_substream_partition_router,
            ValidateAdheresToSchemaModel: self.create_validate_adheres_to_schema,
            WaitTimeFromHeaderModel: self.create_wait_time_from_header,
            WaitUntilTimeFromHeaderModel: self.create_wait_until_time_from_header,
            AsyncRetrieverModel: self.create_async_retriever,
            HttpComponentsResolverModel: self.create_http_components_resolver,
            ConfigComponentsResolverModel: self.create_config_components_resolver,
            ParametrizedComponentsResolverModel: self.create_parametrized_components_resolver,
            StreamConfigModel: self.create_stream_config,
            ComponentMappingDefinitionModel: self.create_components_mapping_definition,
            ZipfileDecoderModel: self.create_zipfile_decoder,
            HTTPAPIBudgetModel: self.create_http_api_budget,
            FileUploaderModel: self.create_file_uploader,
            FixedWindowCallRatePolicyModel: self.create_fixed_window_call_rate_policy,
            MovingWindowCallRatePolicyModel: self.create_moving_window_call_rate_policy,
            UnlimitedCallRatePolicyModel: self.create_unlimited_call_rate_policy,
            RateModel: self.create_rate,
            HttpRequestRegexMatcherModel: self.create_http_request_matcher,
            GroupingPartitionRouterModel: self.create_grouping_partition_router,
        }

        # Needed for the case where we need to perform a second parse on the fields of a custom component
        self.TYPE_NAME_TO_MODEL = {cls.__name__: cls for cls in self.PYDANTIC_MODEL_TO_CONSTRUCTOR}

    @staticmethod
    def _create_stream_name_to_configured_stream(
        configured_catalog: Optional[ConfiguredAirbyteCatalog],
    ) -> Mapping[str, ConfiguredAirbyteStream]:
        return (
            {stream.stream.name: stream for stream in configured_catalog.streams}
            if configured_catalog
            else {}
        )

    def create_component(
        self,
        model_type: Type[BaseModel],
        component_definition: ComponentDefinition,
        config: Config,
        **kwargs: Any,
    ) -> Any:
        """
        Takes a given Pydantic model type and Mapping representing a component definition and creates a declarative component and
        subcomponents which will be used at runtime. This is done by first parsing the mapping into a Pydantic model and then creating
        creating declarative components from that model.

        :param model_type: The type of declarative component that is being initialized
        :param component_definition: The mapping that represents a declarative component
        :param config: The connector config that is provided by the customer
        :return: The declarative component to be used at runtime
        """

        component_type = component_definition.get("type")
        if component_definition.get("type") != model_type.__name__:
            raise ValueError(
                f"Expected manifest component of type {model_type.__name__}, but received {component_type} instead"
            )

        declarative_component_model = model_type.parse_obj(component_definition)

        if not isinstance(declarative_component_model, model_type):
            raise ValueError(
                f"Expected {model_type.__name__} component, but received {declarative_component_model.__class__.__name__}"
            )

        return self._create_component_from_model(
            model=declarative_component_model, config=config, **kwargs
        )

    def _create_component_from_model(self, model: BaseModel, config: Config, **kwargs: Any) -> Any:
        if model.__class__ not in self.PYDANTIC_MODEL_TO_CONSTRUCTOR:
            raise ValueError(
                f"{model.__class__} with attributes {model} is not a valid component type"
            )
        component_constructor = self.PYDANTIC_MODEL_TO_CONSTRUCTOR.get(model.__class__)
        if not component_constructor:
            raise ValueError(f"Could not find constructor for {model.__class__}")

        # collect deprecation warnings for supported models.
        if isinstance(model, BaseModelWithDeprecations):
            self._collect_model_deprecations(model)

        return component_constructor(model=model, config=config, **kwargs)

    def get_model_deprecations(self) -> List[ConnectorBuilderLogMessage]:
        """
        Returns the deprecation warnings that were collected during the creation of components.
        """
        return self._collected_deprecation_logs

    def _collect_model_deprecations(self, model: BaseModelWithDeprecations) -> None:
        """
        Collects deprecation logs from the given model and appends any new logs to the internal collection.

        This method checks if the provided model has deprecation logs (identified by the presence of the DEPRECATION_LOGS_TAG attribute and a non-None `_deprecation_logs` property). It iterates through each deprecation log in the model and appends it to the `_collected_deprecation_logs` list if it has not already been collected, ensuring that duplicate logs are avoided.

        Args:
            model (BaseModelWithDeprecations): The model instance from which to collect deprecation logs.
        """
        if hasattr(model, DEPRECATION_LOGS_TAG) and model._deprecation_logs is not None:
            for log in model._deprecation_logs:
                # avoid duplicates for deprecation logs observed.
                if log not in self._collected_deprecation_logs:
                    self._collected_deprecation_logs.append(log)

    def create_config_migration(
        self, model: ConfigMigrationModel, config: Config
    ) -> ConfigMigration:
        transformations: List[ConfigTransformation] = [
            self._create_component_from_model(transformation, config)
            for transformation in model.transformations
        ]

        return ConfigMigration(
            description=model.description,
            transformations=transformations,
        )

    def create_config_add_fields(
        self, model: ConfigAddFieldsModel, config: Config, **kwargs: Any
    ) -> ConfigAddFields:
        fields = [self._create_component_from_model(field, config) for field in model.fields]
        return ConfigAddFields(
            fields=fields,
            condition=model.condition or "",
        )

    @staticmethod
    def create_config_remove_fields(
        model: ConfigRemoveFieldsModel, config: Config, **kwargs: Any
    ) -> ConfigRemoveFields:
        return ConfigRemoveFields(
            field_pointers=model.field_pointers,
            condition=model.condition or "",
        )

    @staticmethod
    def create_config_remap_field(
        model: ConfigRemapFieldModel, config: Config, **kwargs: Any
    ) -> ConfigRemapField:
        mapping = cast(Mapping[str, Any], model.map)
        return ConfigRemapField(
            map=mapping,
            field_path=model.field_path,
            config=config,
        )

    def create_dpath_validator(self, model: DpathValidatorModel, config: Config) -> DpathValidator:
        strategy = self._create_component_from_model(model.validation_strategy, config)

        return DpathValidator(
            field_path=model.field_path,
            strategy=strategy,
        )

    def create_predicate_validator(
        self, model: PredicateValidatorModel, config: Config
    ) -> PredicateValidator:
        strategy = self._create_component_from_model(model.validation_strategy, config)

        return PredicateValidator(
            value=model.value,
            strategy=strategy,
        )

    @staticmethod
    def create_validate_adheres_to_schema(
        model: ValidateAdheresToSchemaModel, config: Config, **kwargs: Any
    ) -> ValidateAdheresToSchema:
        base_schema = cast(Mapping[str, Any], model.base_schema)
        return ValidateAdheresToSchema(
            schema=base_schema,
        )

    @staticmethod
    def create_added_field_definition(
        model: AddedFieldDefinitionModel, config: Config, **kwargs: Any
    ) -> AddedFieldDefinition:
        interpolated_value = InterpolatedString.create(
            model.value, parameters=model.parameters or {}
        )
        return AddedFieldDefinition(
            path=model.path,
            value=interpolated_value,
            value_type=ModelToComponentFactory._json_schema_type_name_to_type(model.value_type),
            parameters=model.parameters or {},
        )

    def create_add_fields(self, model: AddFieldsModel, config: Config, **kwargs: Any) -> AddFields:
        added_field_definitions = [
            self._create_component_from_model(
                model=added_field_definition_model,
                value_type=ModelToComponentFactory._json_schema_type_name_to_type(
                    added_field_definition_model.value_type
                ),
                config=config,
            )
            for added_field_definition_model in model.fields
        ]
        return AddFields(
            fields=added_field_definitions,
            condition=model.condition or "",
            parameters=model.parameters or {},
        )

    def create_keys_to_lower_transformation(
        self, model: KeysToLowerModel, config: Config, **kwargs: Any
    ) -> KeysToLowerTransformation:
        return KeysToLowerTransformation()

    def create_keys_to_snake_transformation(
        self, model: KeysToSnakeCaseModel, config: Config, **kwargs: Any
    ) -> KeysToSnakeCaseTransformation:
        return KeysToSnakeCaseTransformation()

    def create_keys_replace_transformation(
        self, model: KeysReplaceModel, config: Config, **kwargs: Any
    ) -> KeysReplaceTransformation:
        return KeysReplaceTransformation(
            old=model.old, new=model.new, parameters=model.parameters or {}
        )

    def create_flatten_fields(
        self, model: FlattenFieldsModel, config: Config, **kwargs: Any
    ) -> FlattenFields:
        return FlattenFields(
            flatten_lists=model.flatten_lists if model.flatten_lists is not None else True
        )

    def create_dpath_flatten_fields(
        self, model: DpathFlattenFieldsModel, config: Config, **kwargs: Any
    ) -> DpathFlattenFields:
        model_field_path: List[Union[InterpolatedString, str]] = [x for x in model.field_path]
        key_transformation = (
            KeyTransformation(
                config=config,
                prefix=model.key_transformation.prefix,
                suffix=model.key_transformation.suffix,
                parameters=model.parameters or {},
            )
            if model.key_transformation is not None
            else None
        )
        return DpathFlattenFields(
            config=config,
            field_path=model_field_path,
            delete_origin_value=model.delete_origin_value
            if model.delete_origin_value is not None
            else False,
            replace_record=model.replace_record if model.replace_record is not None else False,
            key_transformation=key_transformation,
            parameters=model.parameters or {},
        )

    @staticmethod
    def _json_schema_type_name_to_type(value_type: Optional[ValueType]) -> Optional[Type[Any]]:
        if not value_type:
            return None
        names_to_types = {
            ValueType.string: str,
            ValueType.number: float,
            ValueType.integer: int,
            ValueType.boolean: bool,
        }
        return names_to_types[value_type]

    def create_api_key_authenticator(
        self,
        model: ApiKeyAuthenticatorModel,
        config: Config,
        token_provider: Optional[TokenProvider] = None,
        **kwargs: Any,
    ) -> ApiKeyAuthenticator:
        if model.inject_into is None and model.header is None:
            raise ValueError(
                "Expected either inject_into or header to be set for ApiKeyAuthenticator"
            )

        if model.inject_into is not None and model.header is not None:
            raise ValueError(
                "inject_into and header cannot be set both for ApiKeyAuthenticator - remove the deprecated header option"
            )

        if token_provider is not None and model.api_token != "":
            raise ValueError(
                "If token_provider is set, api_token is ignored and has to be set to empty string."
            )

        request_option = (
            self._create_component_from_model(
                model.inject_into, config, parameters=model.parameters or {}
            )
            if model.inject_into
            else RequestOption(
                inject_into=RequestOptionType.header,
                field_name=model.header or "",
                parameters=model.parameters or {},
            )
        )

        return ApiKeyAuthenticator(
            token_provider=(
                token_provider
                if token_provider is not None
                else InterpolatedStringTokenProvider(
                    api_token=model.api_token or "",
                    config=config,
                    parameters=model.parameters or {},
                )
            ),
            request_option=request_option,
            config=config,
            parameters=model.parameters or {},
        )

    def create_legacy_to_per_partition_state_migration(
        self,
        model: LegacyToPerPartitionStateMigrationModel,
        config: Mapping[str, Any],
        declarative_stream: DeclarativeStreamModel,
    ) -> LegacyToPerPartitionStateMigration:
        retriever = declarative_stream.retriever
        if not isinstance(retriever, (SimpleRetrieverModel, AsyncRetrieverModel)):
            raise ValueError(
                f"LegacyToPerPartitionStateMigrations can only be applied on a DeclarativeStream with a SimpleRetriever or AsyncRetriever. Got {type(retriever)}"
            )
        partition_router = retriever.partition_router
        if not isinstance(
            partition_router, (SubstreamPartitionRouterModel, CustomPartitionRouterModel)
        ):
            raise ValueError(
                f"LegacyToPerPartitionStateMigrations can only be applied on a SimpleRetriever with a Substream partition router. Got {type(partition_router)}"
            )
        if not hasattr(partition_router, "parent_stream_configs"):
            raise ValueError(
                "LegacyToPerPartitionStateMigrations can only be applied with a parent stream configuration."
            )

        if not hasattr(declarative_stream, "incremental_sync"):
            raise ValueError(
                "LegacyToPerPartitionStateMigrations can only be applied with an incremental_sync configuration."
            )

        return LegacyToPerPartitionStateMigration(
            partition_router,  # type: ignore # was already checked above
            declarative_stream.incremental_sync,  # type: ignore # was already checked. Migration can be applied only to incremental streams.
            config,
            declarative_stream.parameters,  # type: ignore # different type is expected here Mapping[str, Any], got Dict[str, Any]
        )

    def create_session_token_authenticator(
        self, model: SessionTokenAuthenticatorModel, config: Config, name: str, **kwargs: Any
    ) -> Union[ApiKeyAuthenticator, BearerAuthenticator]:
        decoder = (
            self._create_component_from_model(model=model.decoder, config=config)
            if model.decoder
            else JsonDecoder(parameters={})
        )
        login_requester = self._create_component_from_model(
            model=model.login_requester,
            config=config,
            name=f"{name}_login_requester",
            decoder=decoder,
        )
        token_provider = SessionTokenProvider(
            login_requester=login_requester,
            session_token_path=model.session_token_path,
            expiration_duration=parse_duration(model.expiration_duration)
            if model.expiration_duration
            else None,
            parameters=model.parameters or {},
            message_repository=self._message_repository,
            decoder=decoder,
        )
        if model.request_authentication.type == "Bearer":
            return ModelToComponentFactory.create_bearer_authenticator(
                BearerAuthenticatorModel(type="BearerAuthenticator", api_token=""),  # type: ignore # $parameters has a default value
                config,
                token_provider=token_provider,
            )
        else:
            return self.create_api_key_authenticator(
                ApiKeyAuthenticatorModel(
                    type="ApiKeyAuthenticator",
                    api_token="",
                    inject_into=model.request_authentication.inject_into,
                ),  # type: ignore # $parameters and headers default to None
                config=config,
                token_provider=token_provider,
            )

    @staticmethod
    def create_basic_http_authenticator(
        model: BasicHttpAuthenticatorModel, config: Config, **kwargs: Any
    ) -> BasicHttpAuthenticator:
        return BasicHttpAuthenticator(
            password=model.password or "",
            username=model.username,
            config=config,
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_bearer_authenticator(
        model: BearerAuthenticatorModel,
        config: Config,
        token_provider: Optional[TokenProvider] = None,
        **kwargs: Any,
    ) -> BearerAuthenticator:
        if token_provider is not None and model.api_token != "":
            raise ValueError(
                "If token_provider is set, api_token is ignored and has to be set to empty string."
            )
        return BearerAuthenticator(
            token_provider=(
                token_provider
                if token_provider is not None
                else InterpolatedStringTokenProvider(
                    api_token=model.api_token or "",
                    config=config,
                    parameters=model.parameters or {},
                )
            ),
            config=config,
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_dynamic_stream_check_config(
        model: DynamicStreamCheckConfigModel, config: Config, **kwargs: Any
    ) -> DynamicStreamCheckConfig:
        return DynamicStreamCheckConfig(
            dynamic_stream_name=model.dynamic_stream_name,
            stream_count=model.stream_count or 0,
        )

    def create_check_stream(
        self, model: CheckStreamModel, config: Config, **kwargs: Any
    ) -> CheckStream:
        if model.dynamic_streams_check_configs is None and model.stream_names is None:
            raise ValueError(
                "Expected either stream_names or dynamic_streams_check_configs to be set for CheckStream"
            )

        dynamic_streams_check_configs = (
            [
                self._create_component_from_model(model=dynamic_stream_check_config, config=config)
                for dynamic_stream_check_config in model.dynamic_streams_check_configs
            ]
            if model.dynamic_streams_check_configs
            else []
        )

        return CheckStream(
            stream_names=model.stream_names or [],
            dynamic_streams_check_configs=dynamic_streams_check_configs,
            parameters={},
        )

    @staticmethod
    def create_check_dynamic_stream(
        model: CheckDynamicStreamModel, config: Config, **kwargs: Any
    ) -> CheckDynamicStream:
        assert model.use_check_availability is not None  # for mypy

        use_check_availability = model.use_check_availability

        return CheckDynamicStream(
            stream_count=model.stream_count,
            use_check_availability=use_check_availability,
            parameters={},
        )

    def create_composite_error_handler(
        self, model: CompositeErrorHandlerModel, config: Config, **kwargs: Any
    ) -> CompositeErrorHandler:
        error_handlers = [
            self._create_component_from_model(model=error_handler_model, config=config)
            for error_handler_model in model.error_handlers
        ]
        return CompositeErrorHandler(
            error_handlers=error_handlers, parameters=model.parameters or {}
        )

    @staticmethod
    def create_concurrency_level(
        model: ConcurrencyLevelModel, config: Config, **kwargs: Any
    ) -> ConcurrencyLevel:
        return ConcurrencyLevel(
            default_concurrency=model.default_concurrency,
            max_concurrency=model.max_concurrency,
            config=config,
            parameters={},
        )

    @staticmethod
    def apply_stream_state_migrations(
        stream_state_migrations: List[Any] | None, stream_state: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        if stream_state_migrations:
            for state_migration in stream_state_migrations:
                if state_migration.should_migrate(stream_state):
                    # The state variable is expected to be mutable but the migrate method returns an immutable mapping.
                    stream_state = dict(state_migration.migrate(stream_state))
        return stream_state

    def create_concurrent_cursor_from_datetime_based_cursor(
        self,
        model_type: Type[BaseModel],
        component_definition: ComponentDefinition,
        stream_name: str,
        stream_namespace: Optional[str],
        stream_state: MutableMapping[str, Any],
        config: Config,
        message_repository: Optional[MessageRepository] = None,
        runtime_lookback_window: Optional[datetime.timedelta] = None,
        **kwargs: Any,
    ) -> ConcurrentCursor:
        component_type = component_definition.get("type")
        if component_definition.get("type") != model_type.__name__:
            raise ValueError(
                f"Expected manifest component of type {model_type.__name__}, but received {component_type} instead"
            )

        # FIXME the interfaces of the concurrent cursor are kind of annoying as they take a `ComponentDefinition` instead of the actual model. This was done because the ConcurrentDeclarativeSource didn't have access to the models [here for example](https://github.com/airbytehq/airbyte-python-cdk/blob/f525803b3fec9329e4cc8478996a92bf884bfde9/airbyte_cdk/sources/declarative/concurrent_declarative_source.py#L354C54-L354C91). So now we have two cases:
        # * The ComponentDefinition comes from model.__dict__ in which case we have `parameters`
        # * The ComponentDefinition comes from the manifest as a dict in which case we have `$parameters`
        # We should change those interfaces to use the model once we clean up the code in CDS at which point the parameter propagation should happen as part of the ModelToComponentFactory.
        if "$parameters" not in component_definition and "parameters" in component_definition:
            component_definition["$parameters"] = component_definition.get("parameters")  # type: ignore  # This is a dict
        datetime_based_cursor_model = model_type.parse_obj(component_definition)

        if not isinstance(datetime_based_cursor_model, DatetimeBasedCursorModel):
            raise ValueError(
                f"Expected {model_type.__name__} component, but received {datetime_based_cursor_model.__class__.__name__}"
            )

        model_parameters = datetime_based_cursor_model.parameters or {}
        interpolated_cursor_field = InterpolatedString.create(
            datetime_based_cursor_model.cursor_field,
            parameters=model_parameters,
        )
        cursor_field = CursorField(interpolated_cursor_field.eval(config=config))

        interpolated_partition_field_start = InterpolatedString.create(
            datetime_based_cursor_model.partition_field_start or "start_time",
            parameters=model_parameters,
        )
        interpolated_partition_field_end = InterpolatedString.create(
            datetime_based_cursor_model.partition_field_end or "end_time",
            parameters=model_parameters,
        )

        slice_boundary_fields = (
            interpolated_partition_field_start.eval(config=config),
            interpolated_partition_field_end.eval(config=config),
        )

        datetime_format = datetime_based_cursor_model.datetime_format

        cursor_granularity = (
            parse_duration(datetime_based_cursor_model.cursor_granularity)
            if datetime_based_cursor_model.cursor_granularity
            else None
        )

        lookback_window = None
        interpolated_lookback_window = (
            InterpolatedString.create(
                datetime_based_cursor_model.lookback_window,
                parameters=model_parameters,
            )
            if datetime_based_cursor_model.lookback_window
            else None
        )
        if interpolated_lookback_window:
            evaluated_lookback_window = interpolated_lookback_window.eval(config=config)
            if evaluated_lookback_window:
                lookback_window = parse_duration(evaluated_lookback_window)

        connector_state_converter: DateTimeStreamStateConverter
        connector_state_converter = CustomFormatConcurrentStreamStateConverter(
            datetime_format=datetime_format,
            input_datetime_formats=datetime_based_cursor_model.cursor_datetime_formats,
            is_sequential_state=True,  # ConcurrentPerPartitionCursor only works with sequential state
            cursor_granularity=cursor_granularity,
        )

        # Adjusts the stream state by applying the runtime lookback window.
        # This is used to ensure correct state handling in case of failed partitions.
        stream_state_value = stream_state.get(cursor_field.cursor_field_key)
        if runtime_lookback_window and stream_state_value:
            new_stream_state = (
                connector_state_converter.parse_timestamp(stream_state_value)
                - runtime_lookback_window
            )
            stream_state[cursor_field.cursor_field_key] = connector_state_converter.output_format(
                new_stream_state
            )

        start_date_runtime_value: Union[InterpolatedString, str, MinMaxDatetime]
        if isinstance(datetime_based_cursor_model.start_datetime, MinMaxDatetimeModel):
            start_date_runtime_value = self.create_min_max_datetime(
                model=datetime_based_cursor_model.start_datetime, config=config
            )
        else:
            start_date_runtime_value = datetime_based_cursor_model.start_datetime

        end_date_runtime_value: Optional[Union[InterpolatedString, str, MinMaxDatetime]]
        if isinstance(datetime_based_cursor_model.end_datetime, MinMaxDatetimeModel):
            end_date_runtime_value = self.create_min_max_datetime(
                model=datetime_based_cursor_model.end_datetime, config=config
            )
        else:
            end_date_runtime_value = datetime_based_cursor_model.end_datetime

        interpolated_start_date = MinMaxDatetime.create(
            interpolated_string_or_min_max_datetime=start_date_runtime_value,
            parameters=datetime_based_cursor_model.parameters,
        )
        interpolated_end_date = (
            None
            if not end_date_runtime_value
            else MinMaxDatetime.create(
                end_date_runtime_value, datetime_based_cursor_model.parameters
            )
        )

        # If datetime format is not specified then start/end datetime should inherit it from the stream slicer
        if not interpolated_start_date.datetime_format:
            interpolated_start_date.datetime_format = datetime_format
        if interpolated_end_date and not interpolated_end_date.datetime_format:
            interpolated_end_date.datetime_format = datetime_format

        start_date = interpolated_start_date.get_datetime(config=config)
        end_date_provider = (
            partial(interpolated_end_date.get_datetime, config)
            if interpolated_end_date
            else connector_state_converter.get_end_provider()
        )

        if (
            datetime_based_cursor_model.step and not datetime_based_cursor_model.cursor_granularity
        ) or (
            not datetime_based_cursor_model.step and datetime_based_cursor_model.cursor_granularity
        ):
            raise ValueError(
                f"If step is defined, cursor_granularity should be as well and vice-versa. "
                f"Right now, step is `{datetime_based_cursor_model.step}` and cursor_granularity is `{datetime_based_cursor_model.cursor_granularity}`"
            )

        # When step is not defined, default to a step size from the starting date to the present moment
        step_length = datetime.timedelta.max
        interpolated_step = (
            InterpolatedString.create(
                datetime_based_cursor_model.step,
                parameters=model_parameters,
            )
            if datetime_based_cursor_model.step
            else None
        )
        if interpolated_step:
            evaluated_step = interpolated_step.eval(config)
            if evaluated_step:
                step_length = parse_duration(evaluated_step)

        clamping_strategy: ClampingStrategy = NoClamping()
        if datetime_based_cursor_model.clamping:
            # While it is undesirable to interpolate within the model factory (as opposed to at runtime),
            # it is still better than shifting interpolation low-code concept into the ConcurrentCursor runtime
            # object which we want to keep agnostic of being low-code
            target = InterpolatedString(
                string=datetime_based_cursor_model.clamping.target,
                parameters=model_parameters,
            )
            evaluated_target = target.eval(config=config)
            match evaluated_target:
                case "DAY":
                    clamping_strategy = DayClampingStrategy()
                    end_date_provider = ClampingEndProvider(
                        DayClampingStrategy(is_ceiling=False),
                        end_date_provider,  # type: ignore  # Having issues w/ inspection for GapType and CursorValueType as shown in existing tests. Confirmed functionality is working in practice
                        granularity=cursor_granularity or datetime.timedelta(seconds=1),
                    )
                case "WEEK":
                    if (
                        not datetime_based_cursor_model.clamping.target_details
                        or "weekday" not in datetime_based_cursor_model.clamping.target_details
                    ):
                        raise ValueError(
                            "Given WEEK clamping, weekday needs to be provided as target_details"
                        )
                    weekday = self._assemble_weekday(
                        datetime_based_cursor_model.clamping.target_details["weekday"]
                    )
                    clamping_strategy = WeekClampingStrategy(weekday)
                    end_date_provider = ClampingEndProvider(
                        WeekClampingStrategy(weekday, is_ceiling=False),
                        end_date_provider,  # type: ignore  # Having issues w/ inspection for GapType and CursorValueType as shown in existing tests. Confirmed functionality is working in practice
                        granularity=cursor_granularity or datetime.timedelta(days=1),
                    )
                case "MONTH":
                    clamping_strategy = MonthClampingStrategy()
                    end_date_provider = ClampingEndProvider(
                        MonthClampingStrategy(is_ceiling=False),
                        end_date_provider,  # type: ignore  # Having issues w/ inspection for GapType and CursorValueType as shown in existing tests. Confirmed functionality is working in practice
                        granularity=cursor_granularity or datetime.timedelta(days=1),
                    )
                case _:
                    raise ValueError(
                        f"Invalid clamping target {evaluated_target}, expected DAY, WEEK, MONTH"
                    )

        return ConcurrentCursor(
            stream_name=stream_name,
            stream_namespace=stream_namespace,
            stream_state=stream_state,
            message_repository=message_repository or self._message_repository,
            connector_state_manager=self._connector_state_manager,
            connector_state_converter=connector_state_converter,
            cursor_field=cursor_field,
            slice_boundary_fields=slice_boundary_fields,
            start=start_date,  # type: ignore  # Having issues w/ inspection for GapType and CursorValueType as shown in existing tests. Confirmed functionality is working in practice
            end_provider=end_date_provider,  # type: ignore  # Having issues w/ inspection for GapType and CursorValueType as shown in existing tests. Confirmed functionality is working in practice
            lookback_window=lookback_window,
            slice_range=step_length,
            cursor_granularity=cursor_granularity,
            clamping_strategy=clamping_strategy,
        )

    def create_concurrent_cursor_from_incrementing_count_cursor(
        self,
        model_type: Type[BaseModel],
        component_definition: ComponentDefinition,
        stream_name: str,
        stream_namespace: Optional[str],
        stream_state: MutableMapping[str, Any],
        config: Config,
        message_repository: Optional[MessageRepository] = None,
        **kwargs: Any,
    ) -> ConcurrentCursor:
        component_type = component_definition.get("type")
        if component_definition.get("type") != model_type.__name__:
            raise ValueError(
                f"Expected manifest component of type {model_type.__name__}, but received {component_type} instead"
            )

        incrementing_count_cursor_model = model_type.parse_obj(component_definition)

        if not isinstance(incrementing_count_cursor_model, IncrementingCountCursorModel):
            raise ValueError(
                f"Expected {model_type.__name__} component, but received {incrementing_count_cursor_model.__class__.__name__}"
            )

        interpolated_start_value = (
            InterpolatedString.create(
                incrementing_count_cursor_model.start_value,  # type: ignore
                parameters=incrementing_count_cursor_model.parameters or {},
            )
            if incrementing_count_cursor_model.start_value
            else 0
        )

        interpolated_cursor_field = InterpolatedString.create(
            incrementing_count_cursor_model.cursor_field,
            parameters=incrementing_count_cursor_model.parameters or {},
        )
        cursor_field = CursorField(interpolated_cursor_field.eval(config=config))

        connector_state_converter = IncrementingCountStreamStateConverter(
            is_sequential_state=True,  # ConcurrentPerPartitionCursor only works with sequential state
        )

        return ConcurrentCursor(
            stream_name=stream_name,
            stream_namespace=stream_namespace,
            stream_state=stream_state,
            message_repository=message_repository or self._message_repository,
            connector_state_manager=self._connector_state_manager,
            connector_state_converter=connector_state_converter,
            cursor_field=cursor_field,
            slice_boundary_fields=None,
            start=interpolated_start_value,  # type: ignore  # Having issues w/ inspection for GapType and CursorValueType as shown in existing tests. Confirmed functionality is working in practice
            end_provider=connector_state_converter.get_end_provider(),  # type: ignore  # Having issues w/ inspection for GapType and CursorValueType as shown in existing tests. Confirmed functionality is working in practice
        )

    def _assemble_weekday(self, weekday: str) -> Weekday:
        match weekday:
            case "MONDAY":
                return Weekday.MONDAY
            case "TUESDAY":
                return Weekday.TUESDAY
            case "WEDNESDAY":
                return Weekday.WEDNESDAY
            case "THURSDAY":
                return Weekday.THURSDAY
            case "FRIDAY":
                return Weekday.FRIDAY
            case "SATURDAY":
                return Weekday.SATURDAY
            case "SUNDAY":
                return Weekday.SUNDAY
            case _:
                raise ValueError(f"Unknown weekday {weekday}")

    def create_concurrent_cursor_from_perpartition_cursor(
        self,
        state_manager: ConnectorStateManager,
        model_type: Type[BaseModel],
        component_definition: ComponentDefinition,
        stream_name: str,
        stream_namespace: Optional[str],
        config: Config,
        stream_state: MutableMapping[str, Any],
        partition_router: PartitionRouter,
        attempt_to_create_cursor_if_not_provided: bool = False,
        **kwargs: Any,
    ) -> ConcurrentPerPartitionCursor:
        component_type = component_definition.get("type")
        if component_definition.get("type") != model_type.__name__:
            raise ValueError(
                f"Expected manifest component of type {model_type.__name__}, but received {component_type} instead"
            )

        # FIXME the interfaces of the concurrent cursor are kind of annoying as they take a `ComponentDefinition` instead of the actual model. This was done because the ConcurrentDeclarativeSource didn't have access to the models [here for example](https://github.com/airbytehq/airbyte-python-cdk/blob/f525803b3fec9329e4cc8478996a92bf884bfde9/airbyte_cdk/sources/declarative/concurrent_declarative_source.py#L354C54-L354C91). So now we have two cases:
        # * The ComponentDefinition comes from model.__dict__ in which case we have `parameters`
        # * The ComponentDefinition comes from the manifest as a dict in which case we have `$parameters`
        # We should change those interfaces to use the model once we clean up the code in CDS at which point the parameter propagation should happen as part of the ModelToComponentFactory.
        if "$parameters" not in component_definition and "parameters" in component_definition:
            component_definition["$parameters"] = component_definition.get("parameters")  # type: ignore  # This is a dict
        datetime_based_cursor_model = model_type.parse_obj(component_definition)

        if not isinstance(datetime_based_cursor_model, DatetimeBasedCursorModel):
            raise ValueError(
                f"Expected {model_type.__name__} component, but received {datetime_based_cursor_model.__class__.__name__}"
            )

        interpolated_cursor_field = InterpolatedString.create(
            datetime_based_cursor_model.cursor_field,
            # FIXME the interfaces of the concurrent cursor are kind of annoying as they take a `ComponentDefinition` instead of the actual model. This was done because the ConcurrentDeclarativeSource didn't have access to the models [here for example](https://github.com/airbytehq/airbyte-python-cdk/blob/f525803b3fec9329e4cc8478996a92bf884bfde9/airbyte_cdk/sources/declarative/concurrent_declarative_source.py#L354C54-L354C91). So now we have two cases:
            # * The ComponentDefinition comes from model.__dict__ in which case we have `parameters`
            # * The ComponentDefinition comes from the manifest as a dict in which case we have `$parameters`
            # We should change those interfaces to use the model once we clean up the code in CDS at which point the parameter propagation should happen as part of the ModelToComponentFactory.
            parameters=datetime_based_cursor_model.parameters or {},
        )
        cursor_field = CursorField(interpolated_cursor_field.eval(config=config))

        datetime_format = datetime_based_cursor_model.datetime_format

        cursor_granularity = (
            parse_duration(datetime_based_cursor_model.cursor_granularity)
            if datetime_based_cursor_model.cursor_granularity
            else None
        )

        connector_state_converter: DateTimeStreamStateConverter
        connector_state_converter = CustomFormatConcurrentStreamStateConverter(
            datetime_format=datetime_format,
            input_datetime_formats=datetime_based_cursor_model.cursor_datetime_formats,
            is_sequential_state=True,  # ConcurrentPerPartitionCursor only works with sequential state
            cursor_granularity=cursor_granularity,
        )

        # Create the cursor factory
        cursor_factory = ConcurrentCursorFactory(
            partial(
                self.create_concurrent_cursor_from_datetime_based_cursor,
                state_manager=state_manager,
                model_type=model_type,
                component_definition=component_definition,
                stream_name=stream_name,
                stream_namespace=stream_namespace,
                config=config,
                message_repository=NoopMessageRepository(),
            )
        )

        # Per-partition state doesn't make sense for GroupingPartitionRouter, so force the global state
        use_global_cursor = isinstance(
            partition_router, GroupingPartitionRouter
        ) or component_definition.get("global_substream_cursor", False)

        # Return the concurrent cursor and state converter
        return ConcurrentPerPartitionCursor(
            cursor_factory=cursor_factory,
            partition_router=partition_router,
            stream_name=stream_name,
            stream_namespace=stream_namespace,
            stream_state=stream_state,
            message_repository=self._message_repository,  # type: ignore
            connector_state_manager=state_manager,
            connector_state_converter=connector_state_converter,
            cursor_field=cursor_field,
            use_global_cursor=use_global_cursor,
            attempt_to_create_cursor_if_not_provided=attempt_to_create_cursor_if_not_provided,
        )

    @staticmethod
    def create_constant_backoff_strategy(
        model: ConstantBackoffStrategyModel, config: Config, **kwargs: Any
    ) -> ConstantBackoffStrategy:
        return ConstantBackoffStrategy(
            backoff_time_in_seconds=model.backoff_time_in_seconds,
            config=config,
            parameters=model.parameters or {},
        )

    def create_cursor_pagination(
        self, model: CursorPaginationModel, config: Config, decoder: Decoder, **kwargs: Any
    ) -> CursorPaginationStrategy:
        if isinstance(decoder, PaginationDecoderDecorator):
            inner_decoder = decoder.decoder
        else:
            inner_decoder = decoder
            decoder = PaginationDecoderDecorator(decoder=decoder)

        if self._is_supported_decoder_for_pagination(inner_decoder):
            decoder_to_use = decoder
        else:
            raise ValueError(
                self._UNSUPPORTED_DECODER_ERROR.format(decoder_type=type(inner_decoder))
            )

        return CursorPaginationStrategy(
            cursor_value=model.cursor_value,
            decoder=decoder_to_use,
            page_size=model.page_size,
            stop_condition=model.stop_condition,
            config=config,
            parameters=model.parameters or {},
        )

    def create_custom_component(self, model: Any, config: Config, **kwargs: Any) -> Any:
        """
        Generically creates a custom component based on the model type and a class_name reference to the custom Python class being
        instantiated. Only the model's additional properties that match the custom class definition are passed to the constructor
        :param model: The Pydantic model of the custom component being created
        :param config: The custom defined connector config
        :return: The declarative component built from the Pydantic model to be used at runtime
        """
        custom_component_class = self._get_class_from_fully_qualified_class_name(model.class_name)
        component_fields = get_type_hints(custom_component_class)
        model_args = model.dict()
        model_args["config"] = config

        # There are cases where a parent component will pass arguments to a child component via kwargs. When there are field collisions
        # we defer to these arguments over the component's definition
        for key, arg in kwargs.items():
            model_args[key] = arg

        # Pydantic is unable to parse a custom component's fields that are subcomponents into models because their fields and types are not
        # defined in the schema. The fields and types are defined within the Python class implementation. Pydantic can only parse down to
        # the custom component and this code performs a second parse to convert the sub-fields first into models, then declarative components
        for model_field, model_value in model_args.items():
            # If a custom component field doesn't have a type set, we try to use the type hints to infer the type
            if (
                isinstance(model_value, dict)
                and "type" not in model_value
                and model_field in component_fields
            ):
                derived_type = self._derive_component_type_from_type_hints(
                    component_fields.get(model_field)
                )
                if derived_type:
                    model_value["type"] = derived_type

            if self._is_component(model_value):
                model_args[model_field] = self._create_nested_component(
                    model,
                    model_field,
                    model_value,
                    config,
                    **kwargs,
                )
            elif isinstance(model_value, list):
                vals = []
                for v in model_value:
                    if isinstance(v, dict) and "type" not in v and model_field in component_fields:
                        derived_type = self._derive_component_type_from_type_hints(
                            component_fields.get(model_field)
                        )
                        if derived_type:
                            v["type"] = derived_type
                    if self._is_component(v):
                        vals.append(
                            self._create_nested_component(
                                model,
                                model_field,
                                v,
                                config,
                                **kwargs,
                            )
                        )
                    else:
                        vals.append(v)
                model_args[model_field] = vals

        kwargs = {
            class_field: model_args[class_field]
            for class_field in component_fields.keys()
            if class_field in model_args
        }
        return custom_component_class(**kwargs)

    @staticmethod
    def _get_class_from_fully_qualified_class_name(
        full_qualified_class_name: str,
    ) -> Any:
        """Get a class from its fully qualified name.

        If a custom components module is needed, we assume it is already registered - probably
        as `source_declarative_manifest.components` or `components`.

        Args:
            full_qualified_class_name (str): The fully qualified name of the class (e.g., "module.ClassName").

        Returns:
            Any: The class object.

        Raises:
            ValueError: If the class cannot be loaded.
        """
        split = full_qualified_class_name.split(".")
        module_name_full = ".".join(split[:-1])
        class_name = split[-1]

        try:
            module_ref = importlib.import_module(module_name_full)
        except ModuleNotFoundError as e:
            if split[0] == "source_declarative_manifest":
                # During testing, the modules containing the custom components are not moved to source_declarative_manifest. In order to run the test, add the source folder to your PYTHONPATH or add it runtime using sys.path.append
                try:
                    import os

                    module_name_with_source_declarative_manifest = ".".join(split[1:-1])
                    module_ref = importlib.import_module(
                        module_name_with_source_declarative_manifest
                    )
                except ModuleNotFoundError:
                    raise ValueError(f"Could not load module `{module_name_full}`.") from e
            else:
                raise ValueError(f"Could not load module `{module_name_full}`.") from e

        try:
            return getattr(module_ref, class_name)
        except AttributeError as e:
            raise ValueError(
                f"Could not load class `{class_name}` from module `{module_name_full}`.",
            ) from e

    @staticmethod
    def _derive_component_type_from_type_hints(field_type: Any) -> Optional[str]:
        interface = field_type
        while True:
            origin = get_origin(interface)
            if origin:
                # Unnest types until we reach the raw type
                # List[T] -> T
                # Optional[List[T]] -> T
                args = get_args(interface)
                interface = args[0]
            else:
                break
        if isinstance(interface, type) and not ModelToComponentFactory.is_builtin_type(interface):
            return interface.__name__
        return None

    @staticmethod
    def is_builtin_type(cls: Optional[Type[Any]]) -> bool:
        if not cls:
            return False
        return cls.__module__ == "builtins"

    @staticmethod
    def _extract_missing_parameters(error: TypeError) -> List[str]:
        parameter_search = re.search(r"keyword-only.*:\s(.*)", str(error))
        if parameter_search:
            return re.findall(r"\'(.+?)\'", parameter_search.group(1))
        else:
            return []

    def _create_nested_component(
        self, model: Any, model_field: str, model_value: Any, config: Config, **kwargs: Any
    ) -> Any:
        type_name = model_value.get("type", None)
        if not type_name:
            # If no type is specified, we can assume this is a dictionary object which can be returned instead of a subcomponent
            return model_value

        model_type = self.TYPE_NAME_TO_MODEL.get(type_name, None)
        if model_type:
            parsed_model = model_type.parse_obj(model_value)
            try:
                # To improve usability of the language, certain fields are shared between components. This can come in the form of
                # a parent component passing some of its fields to a child component or the parent extracting fields from other child
                # components and passing it to others. One example is the DefaultPaginator referencing the HttpRequester url_base
                # while constructing a SimpleRetriever. However, custom components don't support this behavior because they are created
                # generically in create_custom_component(). This block allows developers to specify extra arguments in $parameters that
                # are needed by a component and could not be shared.
                model_constructor = self.PYDANTIC_MODEL_TO_CONSTRUCTOR.get(parsed_model.__class__)
                constructor_kwargs = inspect.getfullargspec(model_constructor).kwonlyargs
                model_parameters = model_value.get("$parameters", {})
                matching_parameters = {
                    kwarg: model_parameters[kwarg]
                    for kwarg in constructor_kwargs
                    if kwarg in model_parameters
                }
                matching_kwargs = {
                    kwarg: kwargs[kwarg] for kwarg in constructor_kwargs if kwarg in kwargs
                }
                return self._create_component_from_model(
                    model=parsed_model, config=config, **(matching_parameters | matching_kwargs)
                )
            except TypeError as error:
                missing_parameters = self._extract_missing_parameters(error)
                if missing_parameters:
                    raise ValueError(
                        f"Error creating component '{type_name}' with parent custom component {model.class_name}: Please provide "
                        + ", ".join(
                            (
                                f"{type_name}.$parameters.{parameter}"
                                for parameter in missing_parameters
                            )
                        )
                    )
                raise TypeError(
                    f"Error creating component '{type_name}' with parent custom component {model.class_name}: {error}"
                )
        else:
            raise ValueError(
                f"Error creating custom component {model.class_name}. Subcomponent creation has not been implemented for '{type_name}'"
            )

    @staticmethod
    def _is_component(model_value: Any) -> bool:
        return isinstance(model_value, dict) and model_value.get("type") is not None

    def create_datetime_based_cursor(
        self, model: DatetimeBasedCursorModel, config: Config, **kwargs: Any
    ) -> DatetimeBasedCursor:
        start_datetime: Union[str, MinMaxDatetime] = (
            model.start_datetime
            if isinstance(model.start_datetime, str)
            else self.create_min_max_datetime(model.start_datetime, config)
        )
        end_datetime: Union[str, MinMaxDatetime, None] = None
        if model.is_data_feed and model.end_datetime:
            raise ValueError("Data feed does not support end_datetime")
        if model.is_data_feed and model.is_client_side_incremental:
            raise ValueError(
                "`Client side incremental` cannot be applied with `data feed`. Choose only 1 from them."
            )
        if model.end_datetime:
            end_datetime = (
                model.end_datetime
                if isinstance(model.end_datetime, str)
                else self.create_min_max_datetime(model.end_datetime, config)
            )

        end_time_option = (
            self._create_component_from_model(
                model.end_time_option, config, parameters=model.parameters or {}
            )
            if model.end_time_option
            else None
        )
        start_time_option = (
            self._create_component_from_model(
                model.start_time_option, config, parameters=model.parameters or {}
            )
            if model.start_time_option
            else None
        )

        return DatetimeBasedCursor(
            cursor_field=model.cursor_field,
            cursor_datetime_formats=model.cursor_datetime_formats
            if model.cursor_datetime_formats
            else [],
            cursor_granularity=model.cursor_granularity,
            datetime_format=model.datetime_format,
            end_datetime=end_datetime,
            start_datetime=start_datetime,
            step=model.step,
            end_time_option=end_time_option,
            lookback_window=model.lookback_window,
            start_time_option=start_time_option,
            partition_field_end=model.partition_field_end,
            partition_field_start=model.partition_field_start,
            message_repository=self._message_repository,
            is_compare_strictly=model.is_compare_strictly,
            config=config,
            parameters=model.parameters or {},
        )

    def create_default_stream(
        self, model: DeclarativeStreamModel, config: Config, is_parent: bool = False, **kwargs: Any
    ) -> AbstractStream:
        primary_key = model.primary_key.__root__ if model.primary_key else None
        self._migrate_state(model, config)

        partition_router = self._build_stream_slicer_from_partition_router(
            model.retriever,
            config,
            stream_name=model.name,
            **kwargs,
        )
        concurrent_cursor = self._build_concurrent_cursor(model, partition_router, config)
        if model.incremental_sync and isinstance(model.incremental_sync, DatetimeBasedCursorModel):
            cursor_model: DatetimeBasedCursorModel = model.incremental_sync

            end_time_option = (
                self._create_component_from_model(
                    cursor_model.end_time_option, config, parameters=cursor_model.parameters or {}
                )
                if cursor_model.end_time_option
                else None
            )
            start_time_option = (
                self._create_component_from_model(
                    cursor_model.start_time_option, config, parameters=cursor_model.parameters or {}
                )
                if cursor_model.start_time_option
                else None
            )

            datetime_request_options_provider = DatetimeBasedRequestOptionsProvider(
                start_time_option=start_time_option,
                end_time_option=end_time_option,
                partition_field_start=cursor_model.partition_field_start,
                partition_field_end=cursor_model.partition_field_end,
                config=config,
                parameters=model.parameters or {},
            )
            request_options_provider = (
                datetime_request_options_provider
                if not isinstance(concurrent_cursor, ConcurrentPerPartitionCursor)
                else PerPartitionRequestOptionsProvider(
                    partition_router, datetime_request_options_provider
                )
            )
        elif model.incremental_sync and isinstance(
            model.incremental_sync, IncrementingCountCursorModel
        ):
            if isinstance(concurrent_cursor, ConcurrentPerPartitionCursor):
                raise ValueError(
                    "PerPartition does not support per partition states because switching to global state is time based"
                )

            cursor_model: IncrementingCountCursorModel = model.incremental_sync  # type: ignore

            start_time_option = (
                self._create_component_from_model(
                    cursor_model.start_value_option,  # type: ignore # mypy still thinks cursor_model of type DatetimeBasedCursor
                    config,
                    parameters=cursor_model.parameters or {},
                )
                if cursor_model.start_value_option  # type: ignore # mypy still thinks cursor_model of type DatetimeBasedCursor
                else None
            )

            # The concurrent engine defaults the start/end fields on the slice to "start" and "end", but
            # the default DatetimeBasedRequestOptionsProvider() sets them to start_time/end_time
            partition_field_start = "start"

            request_options_provider = DatetimeBasedRequestOptionsProvider(
                start_time_option=start_time_option,
                partition_field_start=partition_field_start,
                config=config,
                parameters=model.parameters or {},
            )
        else:
            request_options_provider = None

        transformations = []
        if model.transformations:
            for transformation_model in model.transformations:
                transformations.append(
                    self._create_component_from_model(model=transformation_model, config=config)
                )
        file_uploader = None
        if model.file_uploader:
            file_uploader = self._create_component_from_model(
                model=model.file_uploader, config=config
            )

        stream_slicer: ConcurrentStreamSlicer = (
            partition_router
            if isinstance(concurrent_cursor, FinalStateCursor)
            else concurrent_cursor
        )

        retriever = self._create_component_from_model(
            model=model.retriever,
            config=config,
            name=model.name,
            primary_key=primary_key,
            request_options_provider=request_options_provider,
            stream_slicer=stream_slicer,
            partition_router=partition_router,
            has_stop_condition_cursor=self._is_stop_condition_on_cursor(model),
            is_client_side_incremental_sync=self._is_client_side_filtering_enabled(model),
            cursor=concurrent_cursor,
            transformations=transformations,
            file_uploader=file_uploader,
            incremental_sync=model.incremental_sync,
        )
        if isinstance(retriever, AsyncRetriever):
            stream_slicer = retriever.stream_slicer

        schema_loader: SchemaLoader
        if model.schema_loader and isinstance(model.schema_loader, list):
            nested_schema_loaders = [
                self._create_component_from_model(model=nested_schema_loader, config=config)
                for nested_schema_loader in model.schema_loader
            ]
            schema_loader = CompositeSchemaLoader(
                schema_loaders=nested_schema_loaders, parameters={}
            )
        elif model.schema_loader:
            schema_loader = self._create_component_from_model(
                model=model.schema_loader,  # type: ignore # If defined, schema_loader is guaranteed not to be a list and will be one of the existing base models
                config=config,
            )
        else:
            options = model.parameters or {}
            if "name" not in options:
                options["name"] = model.name
            schema_loader = DefaultSchemaLoader(config=config, parameters=options)
        schema_loader = CachingSchemaLoaderDecorator(schema_loader)

        stream_name = model.name or ""
        return DefaultStream(
            partition_generator=StreamSlicerPartitionGenerator(
                DeclarativePartitionFactory(
                    stream_name,
                    schema_loader,
                    retriever,
                    self._message_repository,
                ),
                stream_slicer,
                slice_limit=self._limit_slices_fetched,
            ),
            name=stream_name,
            json_schema=schema_loader.get_json_schema,
            primary_key=get_primary_key_from_stream(primary_key),
            cursor_field=concurrent_cursor.cursor_field.cursor_field_key
            if hasattr(concurrent_cursor, "cursor_field")
            else "",  # FIXME we should have the cursor field has part of the interface of cursor,
            logger=logging.getLogger(f"airbyte.{stream_name}"),
            cursor=concurrent_cursor,
            supports_file_transfer=hasattr(model, "file_uploader") and bool(model.file_uploader),
        )

    def _migrate_state(self, model: DeclarativeStreamModel, config: Config) -> None:
        stream_name = model.name or ""
        stream_state = self._connector_state_manager.get_stream_state(
            stream_name=stream_name, namespace=None
        )
        if model.state_migrations:
            state_transformations = [
                self._create_component_from_model(state_migration, config, declarative_stream=model)
                for state_migration in model.state_migrations
            ]
        else:
            state_transformations = []
        stream_state = self.apply_stream_state_migrations(state_transformations, stream_state)
        self._connector_state_manager.update_state_for_stream(
            stream_name=stream_name, namespace=None, value=stream_state
        )

    def _is_stop_condition_on_cursor(self, model: DeclarativeStreamModel) -> bool:
        return bool(
            model.incremental_sync
            and hasattr(model.incremental_sync, "is_data_feed")
            and model.incremental_sync.is_data_feed
        )

    def _is_client_side_filtering_enabled(self, model: DeclarativeStreamModel) -> bool:
        return bool(
            model.incremental_sync
            and hasattr(model.incremental_sync, "is_client_side_incremental")
            and model.incremental_sync.is_client_side_incremental
        )

    def _build_stream_slicer_from_partition_router(
        self,
        model: Union[
            AsyncRetrieverModel,
            CustomRetrieverModel,
            SimpleRetrieverModel,
        ],
        config: Config,
        stream_name: Optional[str] = None,
        **kwargs: Any,
    ) -> PartitionRouter:
        if (
            hasattr(model, "partition_router")
            and isinstance(model, (SimpleRetrieverModel, AsyncRetrieverModel, CustomRetrieverModel))
            and model.partition_router
        ):
            stream_slicer_model = model.partition_router
            if isinstance(stream_slicer_model, list):
                return CartesianProductStreamSlicer(
                    [
                        self._create_component_from_model(
                            model=slicer, config=config, stream_name=stream_name or ""
                        )
                        for slicer in stream_slicer_model
                    ],
                    parameters={},
                )
            elif isinstance(stream_slicer_model, dict):
                # partition router comes from CustomRetrieverModel therefore has not been parsed as a model
                params = stream_slicer_model.get("$parameters")
                if not isinstance(params, dict):
                    params = {}
                    stream_slicer_model["$parameters"] = params

                if stream_name is not None:
                    params["stream_name"] = stream_name

                return self._create_nested_component(  # type: ignore[no-any-return] # There is no guarantee that this will return a stream slicer. If not, we expect an AttributeError during the call to `stream_slices`
                    model,
                    "partition_router",
                    stream_slicer_model,
                    config,
                    **kwargs,
                )
            else:
                return self._create_component_from_model(  # type: ignore[no-any-return] # Will be created PartitionRouter as stream_slicer_model is model.partition_router
                    model=stream_slicer_model, config=config, stream_name=stream_name or ""
                )
        return SinglePartitionRouter(parameters={})

    def _build_concurrent_cursor(
        self,
        model: DeclarativeStreamModel,
        stream_slicer: Optional[PartitionRouter],
        config: Config,
    ) -> Cursor:
        stream_name = model.name or ""
        stream_state = self._connector_state_manager.get_stream_state(stream_name, None)

        if (
            model.incremental_sync
            and stream_slicer
            and not isinstance(stream_slicer, SinglePartitionRouter)
        ):
            if isinstance(model.incremental_sync, IncrementingCountCursorModel):
                # We don't currently support usage of partition routing and IncrementingCountCursor at the
                # same time because we didn't solve for design questions like what the lookback window would
                # be as well as global cursor fall backs. We have not seen customers that have needed both
                # at the same time yet and are currently punting on this until we need to solve it.
                raise ValueError(
                    f"The low-code framework does not currently support usage of a PartitionRouter and an IncrementingCountCursor at the same time. Please specify only one of these options for stream {stream_name}."
                )
            return self.create_concurrent_cursor_from_perpartition_cursor(  # type: ignore # This is a known issue that we are creating and returning a ConcurrentCursor which does not technically implement the (low-code) StreamSlicer. However, (low-code) StreamSlicer and ConcurrentCursor both implement StreamSlicer.stream_slices() which is the primary method needed for checkpointing
                state_manager=self._connector_state_manager,
                model_type=DatetimeBasedCursorModel,
                component_definition=model.incremental_sync.__dict__,
                stream_name=stream_name,
                stream_state=stream_state,
                stream_namespace=None,
                config=config or {},
                partition_router=stream_slicer,
                attempt_to_create_cursor_if_not_provided=True,  # FIXME can we remove that now?
            )
        elif model.incremental_sync:
            if type(model.incremental_sync) == IncrementingCountCursorModel:
                return self.create_concurrent_cursor_from_incrementing_count_cursor(  # type: ignore # This is a known issue that we are creating and returning a ConcurrentCursor which does not technically implement the (low-code) StreamSlicer. However, (low-code) StreamSlicer and ConcurrentCursor both implement StreamSlicer.stream_slices() which is the primary method needed for checkpointing
                    model_type=IncrementingCountCursorModel,
                    component_definition=model.incremental_sync.__dict__,
                    stream_name=stream_name,
                    stream_namespace=None,
                    stream_state=stream_state,
                    config=config or {},
                )
            elif type(model.incremental_sync) == DatetimeBasedCursorModel:
                return self.create_concurrent_cursor_from_datetime_based_cursor(  # type: ignore # This is a known issue that we are creating and returning a ConcurrentCursor which does not technically implement the (low-code) StreamSlicer. However, (low-code) StreamSlicer and ConcurrentCursor both implement StreamSlicer.stream_slices() which is the primary method needed for checkpointing
                    model_type=type(model.incremental_sync),
                    component_definition=model.incremental_sync.__dict__,
                    stream_name=stream_name,
                    stream_namespace=None,
                    stream_state=stream_state,
                    config=config or {},
                    attempt_to_create_cursor_if_not_provided=True,
                )
            else:
                raise ValueError(
                    f"Incremental sync of type {type(model.incremental_sync)} is not supported"
                )
        return FinalStateCursor(stream_name, None, self._message_repository)

    def create_default_error_handler(
        self, model: DefaultErrorHandlerModel, config: Config, **kwargs: Any
    ) -> DefaultErrorHandler:
        backoff_strategies = []
        if model.backoff_strategies:
            for backoff_strategy_model in model.backoff_strategies:
                backoff_strategies.append(
                    self._create_component_from_model(model=backoff_strategy_model, config=config)
                )

        response_filters = []
        if model.response_filters:
            for response_filter_model in model.response_filters:
                response_filters.append(
                    self._create_component_from_model(model=response_filter_model, config=config)
                )
        response_filters.append(
            HttpResponseFilter(config=config, parameters=model.parameters or {})
        )

        return DefaultErrorHandler(
            backoff_strategies=backoff_strategies,
            max_retries=model.max_retries,
            response_filters=response_filters,
            config=config,
            parameters=model.parameters or {},
        )

    def create_default_paginator(
        self,
        model: DefaultPaginatorModel,
        config: Config,
        *,
        url_base: str,
        extractor_model: Optional[Union[CustomRecordExtractorModel, DpathExtractorModel]] = None,
        decoder: Optional[Decoder] = None,
        cursor_used_for_stop_condition: Optional[Cursor] = None,
    ) -> Union[DefaultPaginator, PaginatorTestReadDecorator]:
        if decoder:
            if self._is_supported_decoder_for_pagination(decoder):
                decoder_to_use = PaginationDecoderDecorator(decoder=decoder)
            else:
                raise ValueError(self._UNSUPPORTED_DECODER_ERROR.format(decoder_type=type(decoder)))
        else:
            decoder_to_use = PaginationDecoderDecorator(decoder=JsonDecoder(parameters={}))
        page_size_option = (
            self._create_component_from_model(model=model.page_size_option, config=config)
            if model.page_size_option
            else None
        )
        page_token_option = (
            self._create_component_from_model(model=model.page_token_option, config=config)
            if model.page_token_option
            else None
        )
        pagination_strategy = self._create_component_from_model(
            model=model.pagination_strategy,
            config=config,
            decoder=decoder_to_use,
            extractor_model=extractor_model,
        )
        if cursor_used_for_stop_condition:
            pagination_strategy = StopConditionPaginationStrategyDecorator(
                pagination_strategy, CursorStopCondition(cursor_used_for_stop_condition)
            )
        paginator = DefaultPaginator(
            decoder=decoder_to_use,
            page_size_option=page_size_option,
            page_token_option=page_token_option,
            pagination_strategy=pagination_strategy,
            url_base=url_base,
            config=config,
            parameters=model.parameters or {},
        )
        if self._limit_pages_fetched_per_slice:
            return PaginatorTestReadDecorator(paginator, self._limit_pages_fetched_per_slice)
        return paginator

    def create_dpath_extractor(
        self,
        model: DpathExtractorModel,
        config: Config,
        decoder: Optional[Decoder] = None,
        **kwargs: Any,
    ) -> DpathExtractor:
        if decoder:
            decoder_to_use = decoder
        else:
            decoder_to_use = JsonDecoder(parameters={})
        model_field_path: List[Union[InterpolatedString, str]] = [x for x in model.field_path]
        return DpathExtractor(
            decoder=decoder_to_use,
            field_path=model_field_path,
            config=config,
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_response_to_file_extractor(
        model: ResponseToFileExtractorModel,
        **kwargs: Any,
    ) -> ResponseToFileExtractor:
        return ResponseToFileExtractor(parameters=model.parameters or {})

    @staticmethod
    def create_exponential_backoff_strategy(
        model: ExponentialBackoffStrategyModel, config: Config
    ) -> ExponentialBackoffStrategy:
        return ExponentialBackoffStrategy(
            factor=model.factor or 5, parameters=model.parameters or {}, config=config
        )

    @staticmethod
    def create_group_by_key(model: GroupByKeyMergeStrategyModel, config: Config) -> GroupByKey:
        return GroupByKey(model.key, config=config, parameters=model.parameters or {})

    def create_http_requester(
        self,
        model: HttpRequesterModel,
        config: Config,
        decoder: Decoder = JsonDecoder(parameters={}),
        query_properties_key: Optional[str] = None,
        use_cache: Optional[bool] = None,
        *,
        name: str,
    ) -> HttpRequester:
        authenticator = (
            self._create_component_from_model(
                model=model.authenticator,
                config=config,
                url_base=model.url or model.url_base,
                name=name,
                decoder=decoder,
            )
            if model.authenticator
            else None
        )
        error_handler = (
            self._create_component_from_model(model=model.error_handler, config=config)
            if model.error_handler
            else DefaultErrorHandler(
                backoff_strategies=[],
                response_filters=[],
                config=config,
                parameters=model.parameters or {},
            )
        )

        api_budget = self._api_budget

        request_options_provider = InterpolatedRequestOptionsProvider(
            request_body=model.request_body,
            request_body_data=model.request_body_data,
            request_body_json=model.request_body_json,
            request_headers=model.request_headers,
            request_parameters=model.request_parameters,  # type: ignore  # QueryProperties have been removed in `create_simple_retriever`
            query_properties_key=query_properties_key,
            config=config,
            parameters=model.parameters or {},
        )

        assert model.use_cache is not None  # for mypy
        assert model.http_method is not None  # for mypy

        should_use_cache = (model.use_cache or bool(use_cache)) and not self._disable_cache

        return HttpRequester(
            name=name,
            url=model.url,
            url_base=model.url_base,
            path=model.path,
            authenticator=authenticator,
            error_handler=error_handler,
            api_budget=api_budget,
            http_method=HttpMethod[model.http_method.value],
            request_options_provider=request_options_provider,
            config=config,
            disable_retries=self._disable_retries,
            parameters=model.parameters or {},
            message_repository=self._message_repository,
            use_cache=should_use_cache,
            decoder=decoder,
            stream_response=decoder.is_stream_response() if decoder else False,
        )

    @staticmethod
    def create_http_response_filter(
        model: HttpResponseFilterModel, config: Config, **kwargs: Any
    ) -> HttpResponseFilter:
        if model.action:
            action = ResponseAction(model.action.value)
        else:
            action = None

        failure_type = FailureType(model.failure_type.value) if model.failure_type else None

        http_codes = (
            set(model.http_codes) if model.http_codes else set()
        )  # JSON schema notation has no set data type. The schema enforces an array of unique elements

        return HttpResponseFilter(
            action=action,
            failure_type=failure_type,
            error_message=model.error_message or "",
            error_message_contains=model.error_message_contains or "",
            http_codes=http_codes,
            predicate=model.predicate or "",
            config=config,
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_inline_schema_loader(
        model: InlineSchemaLoaderModel, config: Config, **kwargs: Any
    ) -> InlineSchemaLoader:
        return InlineSchemaLoader(schema=model.schema_ or {}, parameters={})

    def create_complex_field_type(
        self, model: ComplexFieldTypeModel, config: Config, **kwargs: Any
    ) -> ComplexFieldType:
        items = (
            self._create_component_from_model(model=model.items, config=config)
            if isinstance(model.items, ComplexFieldTypeModel)
            else model.items
        )

        return ComplexFieldType(field_type=model.field_type, items=items)

    def create_types_map(self, model: TypesMapModel, config: Config, **kwargs: Any) -> TypesMap:
        target_type = (
            self._create_component_from_model(model=model.target_type, config=config)
            if isinstance(model.target_type, ComplexFieldTypeModel)
            else model.target_type
        )

        return TypesMap(
            target_type=target_type,
            current_type=model.current_type,
            condition=model.condition if model.condition is not None else "True",
        )

    def create_schema_type_identifier(
        self, model: SchemaTypeIdentifierModel, config: Config, **kwargs: Any
    ) -> SchemaTypeIdentifier:
        types_mapping = []
        if model.types_mapping:
            types_mapping.extend(
                [
                    self._create_component_from_model(types_map, config=config)
                    for types_map in model.types_mapping
                ]
            )
        model_schema_pointer: List[Union[InterpolatedString, str]] = (
            [x for x in model.schema_pointer] if model.schema_pointer else []
        )
        model_key_pointer: List[Union[InterpolatedString, str]] = [x for x in model.key_pointer]
        model_type_pointer: Optional[List[Union[InterpolatedString, str]]] = (
            [x for x in model.type_pointer] if model.type_pointer else None
        )

        return SchemaTypeIdentifier(
            schema_pointer=model_schema_pointer,
            key_pointer=model_key_pointer,
            type_pointer=model_type_pointer,
            types_mapping=types_mapping,
            parameters=model.parameters or {},
        )

    def create_dynamic_schema_loader(
        self, model: DynamicSchemaLoaderModel, config: Config, **kwargs: Any
    ) -> DynamicSchemaLoader:
        schema_transformations = []
        if model.schema_transformations:
            for transformation_model in model.schema_transformations:
                schema_transformations.append(
                    self._create_component_from_model(model=transformation_model, config=config)
                )
        name = "dynamic_properties"
        retriever = self._create_component_from_model(
            model=model.retriever,
            config=config,
            name=name,
            primary_key=None,
            partition_router=self._build_stream_slicer_from_partition_router(
                model.retriever, config
            ),
            transformations=[],
            use_cache=True,
            log_formatter=(
                lambda response: format_http_message(
                    response,
                    f"Schema loader '{name}' request",
                    f"Request performed in order to extract schema.",
                    name,
                    is_auxiliary=True,
                )
            ),
        )
        schema_type_identifier = self._create_component_from_model(
            model.schema_type_identifier, config=config, parameters=model.parameters or {}
        )
        schema_filter = (
            self._create_component_from_model(
                model.schema_filter, config=config, parameters=model.parameters or {}
            )
            if model.schema_filter is not None
            else None
        )

        return DynamicSchemaLoader(
            retriever=retriever,
            config=config,
            schema_transformations=schema_transformations,
            schema_filter=schema_filter,
            schema_type_identifier=schema_type_identifier,
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_json_decoder(model: JsonDecoderModel, config: Config, **kwargs: Any) -> Decoder:
        return JsonDecoder(parameters={})

    def create_csv_decoder(self, model: CsvDecoderModel, config: Config, **kwargs: Any) -> Decoder:
        return CompositeRawDecoder(
            parser=ModelToComponentFactory._get_parser(model, config),
            stream_response=False if self._emit_connector_builder_messages else True,
        )

    def create_jsonl_decoder(
        self, model: JsonlDecoderModel, config: Config, **kwargs: Any
    ) -> Decoder:
        return CompositeRawDecoder(
            parser=ModelToComponentFactory._get_parser(model, config),
            stream_response=False if self._emit_connector_builder_messages else True,
        )

    def create_gzip_decoder(
        self, model: GzipDecoderModel, config: Config, **kwargs: Any
    ) -> Decoder:
        _compressed_response_types = {
            "gzip",
            "x-gzip",
            "gzip, deflate",
            "x-gzip, deflate",
            "application/zip",
            "application/gzip",
            "application/x-gzip",
            "application/x-zip-compressed",
        }

        gzip_parser: GzipParser = ModelToComponentFactory._get_parser(model, config)  # type: ignore  # based on the model, we know this will be a GzipParser

        if self._emit_connector_builder_messages:
            # This is very surprising but if the response is not streamed,
            # CompositeRawDecoder calls response.content and the requests library actually uncompress the data as opposed to response.raw,
            # which uses urllib3 directly and does not uncompress the data.
            return CompositeRawDecoder(gzip_parser.inner_parser, False)

        return CompositeRawDecoder.by_headers(
            [({"Content-Encoding", "Content-Type"}, _compressed_response_types, gzip_parser)],
            stream_response=True,
            fallback_parser=gzip_parser.inner_parser,
        )

    # todo: This method should be removed once we deprecate the SimpleRetriever.cursor field and the various
    #  state methods
    @staticmethod
    def create_incrementing_count_cursor(
        model: IncrementingCountCursorModel, config: Config, **kwargs: Any
    ) -> DatetimeBasedCursor:
        # This should not actually get used anywhere at runtime, but needed to add this to pass checks since
        # we still parse models into components. The issue is that there's no runtime implementation of a
        # IncrementingCountCursor.
        # A known and expected issue with this stub is running a check with the declared IncrementingCountCursor because it is run without ConcurrentCursor.
        return DatetimeBasedCursor(
            cursor_field=model.cursor_field,
            datetime_format="%Y-%m-%d",
            start_datetime="2024-12-12",
            config=config,
            parameters={},
        )

    @staticmethod
    def create_iterable_decoder(
        model: IterableDecoderModel, config: Config, **kwargs: Any
    ) -> IterableDecoder:
        return IterableDecoder(parameters={})

    @staticmethod
    def create_xml_decoder(model: XmlDecoderModel, config: Config, **kwargs: Any) -> XmlDecoder:
        return XmlDecoder(parameters={})

    def create_zipfile_decoder(
        self, model: ZipfileDecoderModel, config: Config, **kwargs: Any
    ) -> ZipfileDecoder:
        return ZipfileDecoder(parser=ModelToComponentFactory._get_parser(model.decoder, config))

    @staticmethod
    def _get_parser(model: BaseModel, config: Config) -> Parser:
        if isinstance(model, JsonDecoderModel):
            # Note that the logic is a bit different from the JsonDecoder as there is some legacy that is maintained to return {} on error cases
            return JsonParser()
        elif isinstance(model, JsonlDecoderModel):
            return JsonLineParser()
        elif isinstance(model, CsvDecoderModel):
            return CsvParser(
                encoding=model.encoding,
                delimiter=model.delimiter,
                set_values_to_none=model.set_values_to_none,
            )
        elif isinstance(model, GzipDecoderModel):
            return GzipParser(
                inner_parser=ModelToComponentFactory._get_parser(model.decoder, config)
            )
        elif isinstance(
            model, (CustomDecoderModel, IterableDecoderModel, XmlDecoderModel, ZipfileDecoderModel)
        ):
            raise ValueError(f"Decoder type {model} does not have parser associated to it")

        raise ValueError(f"Unknown decoder type {model}")

    @staticmethod
    def create_json_file_schema_loader(
        model: JsonFileSchemaLoaderModel, config: Config, **kwargs: Any
    ) -> JsonFileSchemaLoader:
        return JsonFileSchemaLoader(
            file_path=model.file_path or "", config=config, parameters=model.parameters or {}
        )

    def create_jwt_authenticator(
        self, model: JwtAuthenticatorModel, config: Config, **kwargs: Any
    ) -> JwtAuthenticator:
        jwt_headers = model.jwt_headers or JwtHeadersModel(kid=None, typ="JWT", cty=None)
        jwt_payload = model.jwt_payload or JwtPayloadModel(iss=None, sub=None, aud=None)
        request_option = (
            self._create_component_from_model(model.request_option, config)
            if model.request_option
            else None
        )
        return JwtAuthenticator(
            config=config,
            parameters=model.parameters or {},
            algorithm=JwtAlgorithm(model.algorithm.value),
            secret_key=model.secret_key,
            base64_encode_secret_key=model.base64_encode_secret_key,
            token_duration=model.token_duration,
            header_prefix=model.header_prefix,
            kid=jwt_headers.kid,
            typ=jwt_headers.typ,
            cty=jwt_headers.cty,
            iss=jwt_payload.iss,
            sub=jwt_payload.sub,
            aud=jwt_payload.aud,
            additional_jwt_headers=model.additional_jwt_headers,
            additional_jwt_payload=model.additional_jwt_payload,
            passphrase=model.passphrase,
            request_option=request_option,
        )

    def create_list_partition_router(
        self, model: ListPartitionRouterModel, config: Config, **kwargs: Any
    ) -> ListPartitionRouter:
        request_option = (
            self._create_component_from_model(model.request_option, config)
            if model.request_option
            else None
        )
        return ListPartitionRouter(
            cursor_field=model.cursor_field,
            request_option=request_option,
            values=model.values,
            config=config,
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_min_max_datetime(
        model: MinMaxDatetimeModel, config: Config, **kwargs: Any
    ) -> MinMaxDatetime:
        return MinMaxDatetime(
            datetime=model.datetime,
            datetime_format=model.datetime_format or "",
            max_datetime=model.max_datetime or "",
            min_datetime=model.min_datetime or "",
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_no_auth(model: NoAuthModel, config: Config, **kwargs: Any) -> NoAuth:
        return NoAuth(parameters=model.parameters or {})

    @staticmethod
    def create_no_pagination(
        model: NoPaginationModel, config: Config, **kwargs: Any
    ) -> NoPagination:
        return NoPagination(parameters={})

    def create_oauth_authenticator(
        self, model: OAuthAuthenticatorModel, config: Config, **kwargs: Any
    ) -> DeclarativeOauth2Authenticator:
        profile_assertion = (
            self._create_component_from_model(model.profile_assertion, config=config)
            if model.profile_assertion
            else None
        )

        if model.refresh_token_updater:
            # ignore type error because fixing it would have a lot of dependencies, revisit later
            return DeclarativeSingleUseRefreshTokenOauth2Authenticator(  # type: ignore
                config,
                InterpolatedString.create(
                    model.token_refresh_endpoint,  # type: ignore
                    parameters=model.parameters or {},
                ).eval(config),
                access_token_name=InterpolatedString.create(
                    model.access_token_name or "access_token", parameters=model.parameters or {}
                ).eval(config),
                refresh_token_name=model.refresh_token_updater.refresh_token_name,
                expires_in_name=InterpolatedString.create(
                    model.expires_in_name or "expires_in", parameters=model.parameters or {}
                ).eval(config),
                client_id_name=InterpolatedString.create(
                    model.client_id_name or "client_id", parameters=model.parameters or {}
                ).eval(config),
                client_id=InterpolatedString.create(
                    model.client_id, parameters=model.parameters or {}
                ).eval(config)
                if model.client_id
                else model.client_id,
                client_secret_name=InterpolatedString.create(
                    model.client_secret_name or "client_secret", parameters=model.parameters or {}
                ).eval(config),
                client_secret=InterpolatedString.create(
                    model.client_secret, parameters=model.parameters or {}
                ).eval(config)
                if model.client_secret
                else model.client_secret,
                access_token_config_path=model.refresh_token_updater.access_token_config_path,
                refresh_token_config_path=model.refresh_token_updater.refresh_token_config_path,
                token_expiry_date_config_path=model.refresh_token_updater.token_expiry_date_config_path,
                grant_type_name=InterpolatedString.create(
                    model.grant_type_name or "grant_type", parameters=model.parameters or {}
                ).eval(config),
                grant_type=InterpolatedString.create(
                    model.grant_type or "refresh_token", parameters=model.parameters or {}
                ).eval(config),
                refresh_request_body=InterpolatedMapping(
                    model.refresh_request_body or {}, parameters=model.parameters or {}
                ).eval(config),
                refresh_request_headers=InterpolatedMapping(
                    model.refresh_request_headers or {}, parameters=model.parameters or {}
                ).eval(config),
                scopes=model.scopes,
                token_expiry_date_format=model.token_expiry_date_format,
                token_expiry_is_time_of_expiration=bool(model.token_expiry_date_format),
                message_repository=self._message_repository,
                refresh_token_error_status_codes=model.refresh_token_updater.refresh_token_error_status_codes,
                refresh_token_error_key=model.refresh_token_updater.refresh_token_error_key,
                refresh_token_error_values=model.refresh_token_updater.refresh_token_error_values,
            )
        # ignore type error because fixing it would have a lot of dependencies, revisit later
        return DeclarativeOauth2Authenticator(  # type: ignore
            access_token_name=model.access_token_name or "access_token",
            access_token_value=model.access_token_value,
            client_id_name=model.client_id_name or "client_id",
            client_id=model.client_id,
            client_secret_name=model.client_secret_name or "client_secret",
            client_secret=model.client_secret,
            expires_in_name=model.expires_in_name or "expires_in",
            grant_type_name=model.grant_type_name or "grant_type",
            grant_type=model.grant_type or "refresh_token",
            refresh_request_body=model.refresh_request_body,
            refresh_request_headers=model.refresh_request_headers,
            refresh_token_name=model.refresh_token_name or "refresh_token",
            refresh_token=model.refresh_token,
            scopes=model.scopes,
            token_expiry_date=model.token_expiry_date,
            token_expiry_date_format=model.token_expiry_date_format,
            token_expiry_is_time_of_expiration=bool(model.token_expiry_date_format),
            token_refresh_endpoint=model.token_refresh_endpoint,
            config=config,
            parameters=model.parameters or {},
            message_repository=self._message_repository,
            profile_assertion=profile_assertion,
            use_profile_assertion=model.use_profile_assertion,
        )

    def create_offset_increment(
        self,
        model: OffsetIncrementModel,
        config: Config,
        decoder: Decoder,
        extractor_model: Optional[Union[CustomRecordExtractorModel, DpathExtractorModel]] = None,
        **kwargs: Any,
    ) -> OffsetIncrement:
        if isinstance(decoder, PaginationDecoderDecorator):
            inner_decoder = decoder.decoder
        else:
            inner_decoder = decoder
            decoder = PaginationDecoderDecorator(decoder=decoder)

        if self._is_supported_decoder_for_pagination(inner_decoder):
            decoder_to_use = decoder
        else:
            raise ValueError(
                self._UNSUPPORTED_DECODER_ERROR.format(decoder_type=type(inner_decoder))
            )

        # Ideally we would instantiate the runtime extractor from highest most level (in this case the SimpleRetriever)
        # so that it can be shared by OffSetIncrement and RecordSelector. However, due to how we instantiate the
        # decoder with various decorators here, but not in create_record_selector, it is simpler to retain existing
        # behavior by having two separate extractors with identical behavior since they use the same extractor model.
        # When we have more time to investigate we can look into reusing the same component.
        extractor = (
            self._create_component_from_model(
                model=extractor_model, config=config, decoder=decoder_to_use
            )
            if extractor_model
            else None
        )

        return OffsetIncrement(
            page_size=model.page_size,
            config=config,
            decoder=decoder_to_use,
            extractor=extractor,
            inject_on_first_request=model.inject_on_first_request or False,
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_page_increment(
        model: PageIncrementModel, config: Config, **kwargs: Any
    ) -> PageIncrement:
        return PageIncrement(
            page_size=model.page_size,
            config=config,
            start_from_page=model.start_from_page or 0,
            inject_on_first_request=model.inject_on_first_request or False,
            parameters=model.parameters or {},
        )

    def create_parent_stream_config(
        self, model: ParentStreamConfigModel, config: Config, *, stream_name: str, **kwargs: Any
    ) -> ParentStreamConfig:
        declarative_stream = self._create_component_from_model(
            model.stream,
            config=config,
            is_parent=True,
            **kwargs,
        )
        request_option = (
            self._create_component_from_model(model.request_option, config=config)
            if model.request_option
            else None
        )

        if model.lazy_read_pointer and any("*" in pointer for pointer in model.lazy_read_pointer):
            raise ValueError(
                "The '*' wildcard in 'lazy_read_pointer' is not supported — only direct paths are allowed."
            )

        model_lazy_read_pointer: List[Union[InterpolatedString, str]] = (
            [x for x in model.lazy_read_pointer] if model.lazy_read_pointer else []
        )

        return ParentStreamConfig(
            parent_key=model.parent_key,
            request_option=request_option,
            stream=declarative_stream,
            partition_field=model.partition_field,
            config=config,
            incremental_dependency=model.incremental_dependency or False,
            parameters=model.parameters or {},
            extra_fields=model.extra_fields,
            lazy_read_pointer=model_lazy_read_pointer,
        )

    def create_properties_from_endpoint(
        self, model: PropertiesFromEndpointModel, config: Config, **kwargs: Any
    ) -> PropertiesFromEndpoint:
        retriever = self._create_component_from_model(
            model=model.retriever,
            config=config,
            name="dynamic_properties",
            primary_key=None,
            stream_slicer=None,
            transformations=[],
            use_cache=True,  # Enable caching on the HttpRequester/HttpClient because the properties endpoint will be called for every slice being processed, and it is highly unlikely for the response to different
        )
        return PropertiesFromEndpoint(
            property_field_path=model.property_field_path,
            retriever=retriever,
            config=config,
            parameters=model.parameters or {},
        )

    def create_property_chunking(
        self, model: PropertyChunkingModel, config: Config, **kwargs: Any
    ) -> PropertyChunking:
        record_merge_strategy = (
            self._create_component_from_model(
                model=model.record_merge_strategy, config=config, **kwargs
            )
            if model.record_merge_strategy
            else None
        )

        property_limit_type: PropertyLimitType
        match model.property_limit_type:
            case PropertyLimitTypeModel.property_count:
                property_limit_type = PropertyLimitType.property_count
            case PropertyLimitTypeModel.characters:
                property_limit_type = PropertyLimitType.characters
            case _:
                raise ValueError(f"Invalid PropertyLimitType {property_limit_type}")

        return PropertyChunking(
            property_limit_type=property_limit_type,
            property_limit=model.property_limit,
            record_merge_strategy=record_merge_strategy,
            config=config,
            parameters=model.parameters or {},
        )

    def create_query_properties(
        self, model: QueryPropertiesModel, config: Config, *, stream_name: str, **kwargs: Any
    ) -> QueryProperties:
        if isinstance(model.property_list, list):
            property_list = model.property_list
        else:
            property_list = self._create_component_from_model(
                model=model.property_list, config=config, **kwargs
            )

        property_chunking = (
            self._create_component_from_model(
                model=model.property_chunking, config=config, **kwargs
            )
            if model.property_chunking
            else None
        )

        property_selector = (
            self._create_component_from_model(
                model=model.property_selector, config=config, stream_name=stream_name, **kwargs
            )
            if model.property_selector
            else None
        )

        return QueryProperties(
            property_list=property_list,
            always_include_properties=model.always_include_properties,
            property_chunking=property_chunking,
            property_selector=property_selector,
            config=config,
            parameters=model.parameters or {},
        )

    def create_json_schema_property_selector(
        self,
        model: JsonSchemaPropertySelectorModel,
        config: Config,
        *,
        stream_name: str,
        **kwargs: Any,
    ) -> JsonSchemaPropertySelector:
        configured_stream = self._stream_name_to_configured_stream.get(stream_name)

        transformations = []
        if model.transformations:
            for transformation_model in model.transformations:
                transformations.append(
                    self._create_component_from_model(model=transformation_model, config=config)
                )

        return JsonSchemaPropertySelector(
            configured_stream=configured_stream,
            properties_transformations=transformations,
            config=config,
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_record_filter(
        model: RecordFilterModel, config: Config, **kwargs: Any
    ) -> RecordFilter:
        return RecordFilter(
            condition=model.condition or "", config=config, parameters=model.parameters or {}
        )

    @staticmethod
    def create_request_path(model: RequestPathModel, config: Config, **kwargs: Any) -> RequestPath:
        return RequestPath(parameters={})

    @staticmethod
    def create_request_option(
        model: RequestOptionModel, config: Config, **kwargs: Any
    ) -> RequestOption:
        inject_into = RequestOptionType(model.inject_into.value)
        field_path: Optional[List[Union[InterpolatedString, str]]] = (
            [
                InterpolatedString.create(segment, parameters=kwargs.get("parameters", {}))
                for segment in model.field_path
            ]
            if model.field_path
            else None
        )
        field_name = (
            InterpolatedString.create(model.field_name, parameters=kwargs.get("parameters", {}))
            if model.field_name
            else None
        )
        return RequestOption(
            field_name=field_name,
            field_path=field_path,
            inject_into=inject_into,
            parameters=kwargs.get("parameters", {}),
        )

    def create_record_selector(
        self,
        model: RecordSelectorModel,
        config: Config,
        *,
        name: str,
        transformations: List[RecordTransformation] | None = None,
        decoder: Decoder | None = None,
        client_side_incremental_sync_cursor: Optional[Cursor] = None,
        file_uploader: Optional[DefaultFileUploader] = None,
        **kwargs: Any,
    ) -> RecordSelector:
        extractor = self._create_component_from_model(
            model=model.extractor, decoder=decoder, config=config
        )
        record_filter = (
            self._create_component_from_model(model.record_filter, config=config)
            if model.record_filter
            else None
        )

        transform_before_filtering = (
            False if model.transform_before_filtering is None else model.transform_before_filtering
        )
        if client_side_incremental_sync_cursor:
            record_filter = ClientSideIncrementalRecordFilterDecorator(
                config=config,
                parameters=model.parameters,
                condition=model.record_filter.condition
                if (model.record_filter and hasattr(model.record_filter, "condition"))
                else None,
                cursor=client_side_incremental_sync_cursor,
            )
            transform_before_filtering = (
                True
                if model.transform_before_filtering is None
                else model.transform_before_filtering
            )

        if model.schema_normalization is None:
            # default to no schema normalization if not set
            model.schema_normalization = SchemaNormalizationModel.None_

        schema_normalization = (
            TypeTransformer(SCHEMA_TRANSFORMER_TYPE_MAPPING[model.schema_normalization])
            if isinstance(model.schema_normalization, SchemaNormalizationModel)
            else self._create_component_from_model(model.schema_normalization, config=config)  # type: ignore[arg-type] # custom normalization model expected here
        )

        return RecordSelector(
            extractor=extractor,
            name=name,
            config=config,
            record_filter=record_filter,
            transformations=transformations or [],
            file_uploader=file_uploader,
            schema_normalization=schema_normalization,
            parameters=model.parameters or {},
            transform_before_filtering=transform_before_filtering,
        )

    @staticmethod
    def create_remove_fields(
        model: RemoveFieldsModel, config: Config, **kwargs: Any
    ) -> RemoveFields:
        return RemoveFields(
            field_pointers=model.field_pointers, condition=model.condition or "", parameters={}
        )

    def create_selective_authenticator(
        self, model: SelectiveAuthenticatorModel, config: Config, **kwargs: Any
    ) -> DeclarativeAuthenticator:
        authenticators = {
            name: self._create_component_from_model(model=auth, config=config)
            for name, auth in model.authenticators.items()
        }
        # SelectiveAuthenticator will return instance of DeclarativeAuthenticator or raise ValueError error
        return SelectiveAuthenticator(  # type: ignore[abstract]
            config=config,
            authenticators=authenticators,
            authenticator_selection_path=model.authenticator_selection_path,
            **kwargs,
        )

    @staticmethod
    def create_legacy_session_token_authenticator(
        model: LegacySessionTokenAuthenticatorModel, config: Config, *, url_base: str, **kwargs: Any
    ) -> LegacySessionTokenAuthenticator:
        return LegacySessionTokenAuthenticator(
            api_url=url_base,
            header=model.header,
            login_url=model.login_url,
            password=model.password or "",
            session_token=model.session_token or "",
            session_token_response_key=model.session_token_response_key or "",
            username=model.username or "",
            validate_session_url=model.validate_session_url,
            config=config,
            parameters=model.parameters or {},
        )

    def create_simple_retriever(
        self,
        model: SimpleRetrieverModel,
        config: Config,
        *,
        name: str,
        primary_key: Optional[Union[str, List[str], List[List[str]]]],
        request_options_provider: Optional[RequestOptionsProvider] = None,
        cursor: Optional[Cursor] = None,
        has_stop_condition_cursor: bool = False,
        is_client_side_incremental_sync: bool = False,
        transformations: List[RecordTransformation],
        file_uploader: Optional[DefaultFileUploader] = None,
        incremental_sync: Optional[
            Union[IncrementingCountCursorModel, DatetimeBasedCursorModel]
        ] = None,
        use_cache: Optional[bool] = None,
        log_formatter: Optional[Callable[[Response], Any]] = None,
        partition_router: Optional[PartitionRouter] = None,
        **kwargs: Any,
    ) -> SimpleRetriever:
        def _get_url(req: Requester) -> str:
            """
            Closure to get the URL from the requester. This is used to get the URL in the case of a lazy retriever.
            This is needed because the URL is not set until the requester is created.
            """

            _url: str = (
                model.requester.url
                if hasattr(model.requester, "url") and model.requester.url is not None
                else req.get_url(stream_state=None, stream_slice=None, next_page_token=None)
            )
            _url_base: str = (
                model.requester.url_base
                if hasattr(model.requester, "url_base") and model.requester.url_base is not None
                else req.get_url_base(stream_state=None, stream_slice=None, next_page_token=None)
            )

            return _url or _url_base

        if cursor is None:
            cursor = FinalStateCursor(name, None, self._message_repository)

        decoder = (
            self._create_component_from_model(model=model.decoder, config=config)
            if model.decoder
            else JsonDecoder(parameters={})
        )
        record_selector = self._create_component_from_model(
            model=model.record_selector,
            name=name,
            config=config,
            decoder=decoder,
            transformations=transformations,
            client_side_incremental_sync_cursor=cursor if is_client_side_incremental_sync else None,
            file_uploader=file_uploader,
        )

        query_properties: Optional[QueryProperties] = None
        query_properties_key: Optional[str] = None
        self._ensure_query_properties_to_model(model.requester)
        if self._has_query_properties_in_request_parameters(model.requester):
            # It is better to be explicit about an error if PropertiesFromEndpoint is defined in multiple
            # places instead of default to request_parameters which isn't clearly documented
            if (
                hasattr(model.requester, "fetch_properties_from_endpoint")
                and model.requester.fetch_properties_from_endpoint
            ):
                raise ValueError(
                    f"PropertiesFromEndpoint should only be specified once per stream, but found in {model.requester.type}.fetch_properties_from_endpoint and {model.requester.type}.request_parameters"
                )

            query_properties_definitions = []
            for key, request_parameter in model.requester.request_parameters.items():  # type: ignore # request_parameters is already validated to be a Mapping using _has_query_properties_in_request_parameters()
                if isinstance(request_parameter, QueryPropertiesModel):
                    query_properties_key = key
                    query_properties_definitions.append(request_parameter)

            if len(query_properties_definitions) > 1:
                raise ValueError(
                    f"request_parameters only supports defining one QueryProperties field, but found {len(query_properties_definitions)} usages"
                )

            if len(query_properties_definitions) == 1:
                query_properties = self._create_component_from_model(
                    model=query_properties_definitions[0], stream_name=name, config=config
                )

            # Removes QueryProperties components from the interpolated mappings because it has been designed
            # to be used by the SimpleRetriever and will be resolved from the provider from the slice directly
            # instead of through jinja interpolation
            if hasattr(model.requester, "request_parameters") and isinstance(
                model.requester.request_parameters, Mapping
            ):
                model.requester.request_parameters = self._remove_query_properties(
                    model.requester.request_parameters
                )
        elif (
            hasattr(model.requester, "fetch_properties_from_endpoint")
            and model.requester.fetch_properties_from_endpoint
        ):
            # todo: Deprecate this condition once dependent connectors migrate to query_properties
            query_properties_definition = QueryPropertiesModel(
                type="QueryProperties",
                property_list=model.requester.fetch_properties_from_endpoint,
                always_include_properties=None,
                property_chunking=None,
            )  # type: ignore # $parameters has a default value

            query_properties = self.create_query_properties(
                model=query_properties_definition,
                stream_name=name,
                config=config,
            )
        elif hasattr(model.requester, "query_properties") and model.requester.query_properties:
            query_properties = self.create_query_properties(
                model=model.requester.query_properties,
                stream_name=name,
                config=config,
            )

        requester = self._create_component_from_model(
            model=model.requester,
            decoder=decoder,
            name=name,
            query_properties_key=query_properties_key,
            use_cache=use_cache,
            config=config,
        )

        if not request_options_provider:
            request_options_provider = DefaultRequestOptionsProvider(parameters={})
        if isinstance(request_options_provider, DefaultRequestOptionsProvider) and isinstance(
            partition_router, PartitionRouter
        ):
            request_options_provider = partition_router

        paginator = (
            self._create_component_from_model(
                model=model.paginator,
                config=config,
                url_base=_get_url(requester),
                extractor_model=model.record_selector.extractor,
                decoder=decoder,
                cursor_used_for_stop_condition=cursor if has_stop_condition_cursor else None,
            )
            if model.paginator
            else NoPagination(parameters={})
        )

        ignore_stream_slicer_parameters_on_paginated_requests = (
            model.ignore_stream_slicer_parameters_on_paginated_requests or False
        )

        if (
            model.partition_router
            and isinstance(model.partition_router, SubstreamPartitionRouterModel)
            and not bool(self._connector_state_manager.get_stream_state(name, None))
            and any(
                parent_stream_config.lazy_read_pointer
                for parent_stream_config in model.partition_router.parent_stream_configs
            )
        ):
            if incremental_sync:
                if incremental_sync.type != "DatetimeBasedCursor":
                    raise ValueError(
                        f"LazySimpleRetriever only supports DatetimeBasedCursor. Found: {incremental_sync.type}."
                    )

                elif incremental_sync.step or incremental_sync.cursor_granularity:
                    raise ValueError(
                        f"Found more that one slice per parent. LazySimpleRetriever only supports single slice read for stream - {name}."
                    )

            if model.decoder and model.decoder.type != "JsonDecoder":
                raise ValueError(
                    f"LazySimpleRetriever only supports JsonDecoder. Found: {model.decoder.type}."
                )

            return LazySimpleRetriever(
                name=name,
                paginator=paginator,
                primary_key=primary_key,
                requester=requester,
                record_selector=record_selector,
                stream_slicer=_NO_STREAM_SLICING,
                request_option_provider=request_options_provider,
                cursor=None,
                config=config,
                ignore_stream_slicer_parameters_on_paginated_requests=ignore_stream_slicer_parameters_on_paginated_requests,
                parameters=model.parameters or {},
            )

        if (
            model.record_selector.record_filter
            and model.pagination_reset
            and model.pagination_reset.limits
        ):
            raise ValueError("PaginationResetLimits are not supported while having record filter.")

        return SimpleRetriever(
            name=name,
            paginator=paginator,
            primary_key=primary_key,
            requester=requester,
            record_selector=record_selector,
            stream_slicer=_NO_STREAM_SLICING,
            request_option_provider=request_options_provider,
            cursor=None,
            config=config,
            ignore_stream_slicer_parameters_on_paginated_requests=ignore_stream_slicer_parameters_on_paginated_requests,
            additional_query_properties=query_properties,
            log_formatter=self._get_log_formatter(log_formatter, name),
            pagination_tracker_factory=self._create_pagination_tracker_factory(
                model.pagination_reset, cursor
            ),
            parameters=model.parameters or {},
        )

    def _create_pagination_tracker_factory(
        self, model: Optional[PaginationResetModel], cursor: Cursor
    ) -> Callable[[], PaginationTracker]:
        if model is None:
            return lambda: PaginationTracker()

        # Until we figure out a way to use any cursor for PaginationTracker, we will have to have this cursor selector logic
        cursor_factory: Callable[[], Optional[ConcurrentCursor]] = lambda: None
        if model.action == PaginationResetActionModel.RESET:
            # in that case, we will let cursor_factory to return None even if the stream has a cursor
            pass
        elif model.action == PaginationResetActionModel.SPLIT_USING_CURSOR:
            if isinstance(cursor, ConcurrentCursor):
                cursor_factory = lambda: cursor.copy_without_state()  # type: ignore  # the if condition validates that it is a ConcurrentCursor
            elif isinstance(cursor, ConcurrentPerPartitionCursor):
                cursor_factory = lambda: cursor._cursor_factory.create(  # type: ignore  # if this becomes a problem, we would need to extract the cursor_factory instantiation logic and make it accessible here
                    {}, datetime.timedelta(0)
                )
            elif not isinstance(cursor, FinalStateCursor):
                LOGGER.warning(
                    "Unknown cursor for PaginationTracker. Pagination resets might not work properly"
                )
        else:
            raise ValueError(f"Unknown PaginationReset action: {model.action}")

        limit = model.limits.number_of_records if model and model.limits else None
        return lambda: PaginationTracker(cursor_factory(), limit)

    def _get_log_formatter(
        self, log_formatter: Callable[[Response], Any] | None, name: str
    ) -> Callable[[Response], Any] | None:
        if self._should_limit_slices_fetched():
            return (
                (
                    lambda response: format_http_message(
                        response,
                        f"Stream '{name}' request",
                        f"Request performed in order to extract records for stream '{name}'",
                        name,
                    )
                )
                if not log_formatter
                else log_formatter
            )
        return None

    def _should_limit_slices_fetched(self) -> bool:
        """
        Returns True if the number of slices fetched should be limited, False otherwise.
        This is used to limit the number of slices fetched during tests.
        """
        return bool(self._limit_slices_fetched or self._emit_connector_builder_messages)

    @staticmethod
    def _has_query_properties_in_request_parameters(
        requester: Union[HttpRequesterModel, CustomRequesterModel],
    ) -> bool:
        if not hasattr(requester, "request_parameters"):
            return False
        request_parameters = requester.request_parameters
        if request_parameters and isinstance(request_parameters, Mapping):
            for request_parameter in request_parameters.values():
                if isinstance(request_parameter, QueryPropertiesModel):
                    return True
        return False

    @staticmethod
    def _remove_query_properties(
        request_parameters: Mapping[str, Union[str, QueryPropertiesModel]],
    ) -> Mapping[str, str]:
        return {
            parameter_field: request_parameter
            for parameter_field, request_parameter in request_parameters.items()
            if not isinstance(request_parameter, QueryPropertiesModel)
        }

    def create_state_delegating_stream(
        self,
        model: StateDelegatingStreamModel,
        config: Config,
        has_parent_state: Optional[bool] = None,
        **kwargs: Any,
    ) -> DeclarativeStream:
        if (
            model.full_refresh_stream.name != model.name
            or model.name != model.incremental_stream.name
        ):
            raise ValueError(
                f"state_delegating_stream, full_refresh_stream name and incremental_stream must have equal names. Instead has {model.name}, {model.full_refresh_stream.name} and {model.incremental_stream.name}."
            )

        stream_model = self._get_state_delegating_stream_model(
            False if has_parent_state is None else has_parent_state, model
        )

        return self._create_component_from_model(stream_model, config=config, **kwargs)  # type: ignore[no-any-return]  # DeclarativeStream will be created as stream_model is alwyas DeclarativeStreamModel

    def _get_state_delegating_stream_model(
        self, has_parent_state: bool, model: StateDelegatingStreamModel
    ) -> DeclarativeStreamModel:
        return (
            model.incremental_stream
            if self._connector_state_manager.get_stream_state(model.name, None) or has_parent_state
            else model.full_refresh_stream
        )

    def _create_async_job_status_mapping(
        self, model: AsyncJobStatusMapModel, config: Config, **kwargs: Any
    ) -> Mapping[str, AsyncJobStatus]:
        api_status_to_cdk_status = {}
        for cdk_status, api_statuses in model.dict().items():
            if cdk_status == "type":
                # This is an element of the dict because of the typing of the CDK but it is not a CDK status
                continue

            for status in api_statuses:
                if status in api_status_to_cdk_status:
                    raise ValueError(
                        f"API status {status} is already set for CDK status {cdk_status}. Please ensure API statuses are only provided once"
                    )
                api_status_to_cdk_status[status] = self._get_async_job_status(cdk_status)
        return api_status_to_cdk_status

    def _get_async_job_status(self, status: str) -> AsyncJobStatus:
        match status:
            case "running":
                return AsyncJobStatus.RUNNING
            case "completed":
                return AsyncJobStatus.COMPLETED
            case "failed":
                return AsyncJobStatus.FAILED
            case "timeout":
                return AsyncJobStatus.TIMED_OUT
            case _:
                raise ValueError(f"Unsupported CDK status {status}")

    def create_async_retriever(
        self,
        model: AsyncRetrieverModel,
        config: Config,
        *,
        name: str,
        primary_key: Optional[
            Union[str, List[str], List[List[str]]]
        ],  # this seems to be needed to match create_simple_retriever
        stream_slicer: Optional[StreamSlicer],
        client_side_incremental_sync: Optional[Dict[str, Any]] = None,
        transformations: List[RecordTransformation],
        **kwargs: Any,
    ) -> AsyncRetriever:
        if model.download_target_requester and not model.download_target_extractor:
            raise ValueError(
                f"`download_target_extractor` required if using a `download_target_requester`"
            )

        def _get_download_retriever(
            requester: Requester, extractor: RecordExtractor, _decoder: Decoder
        ) -> SimpleRetriever:
            # We create a record selector for the download retriever
            # with no schema normalization and no transformations, neither record filter
            # as all this occurs in the record_selector of the AsyncRetriever
            record_selector = RecordSelector(
                extractor=extractor,
                name=name,
                record_filter=None,
                transformations=[],
                schema_normalization=TypeTransformer(TransformConfig.NoTransform),
                config=config,
                parameters={},
            )
            paginator = (
                self._create_component_from_model(
                    model=model.download_paginator,
                    decoder=_decoder,
                    config=config,
                    url_base="",
                )
                if model.download_paginator
                else NoPagination(parameters={})
            )

            return SimpleRetriever(
                requester=requester,
                record_selector=record_selector,
                primary_key=None,
                name=name,
                paginator=paginator,
                config=config,
                parameters={},
                log_formatter=self._get_log_formatter(None, name),
            )

        def _get_job_timeout() -> datetime.timedelta:
            user_defined_timeout: Optional[int] = (
                int(
                    InterpolatedString.create(
                        str(model.polling_job_timeout),
                        parameters={},
                    ).eval(config)
                )
                if model.polling_job_timeout
                else None
            )

            # check for user defined timeout during the test read or 15 minutes
            test_read_timeout = datetime.timedelta(minutes=user_defined_timeout or 15)
            # default value for non-connector builder is 60 minutes.
            default_sync_timeout = datetime.timedelta(minutes=user_defined_timeout or 60)

            return (
                test_read_timeout if self._emit_connector_builder_messages else default_sync_timeout
            )

        decoder = (
            self._create_component_from_model(model=model.decoder, config=config)
            if model.decoder
            else JsonDecoder(parameters={})
        )
        record_selector = self._create_component_from_model(
            model=model.record_selector,
            config=config,
            decoder=decoder,
            name=name,
            transformations=transformations,
            client_side_incremental_sync=client_side_incremental_sync,
        )

        stream_slicer = stream_slicer or SinglePartitionRouter(parameters={})
        if self._should_limit_slices_fetched():
            stream_slicer = cast(
                StreamSlicer,
                StreamSlicerTestReadDecorator(
                    wrapped_slicer=stream_slicer,
                    maximum_number_of_slices=self._limit_slices_fetched or 5,
                ),
            )

        creation_requester = self._create_component_from_model(
            model=model.creation_requester,
            decoder=decoder,
            config=config,
            name=f"job creation - {name}",
        )
        polling_requester = self._create_component_from_model(
            model=model.polling_requester,
            decoder=decoder,
            config=config,
            name=f"job polling - {name}",
        )
        job_download_components_name = f"job download - {name}"
        download_decoder = (
            self._create_component_from_model(model=model.download_decoder, config=config)
            if model.download_decoder
            else JsonDecoder(parameters={})
        )
        download_extractor = (
            self._create_component_from_model(
                model=model.download_extractor,
                config=config,
                decoder=download_decoder,
                parameters=model.parameters,
            )
            if model.download_extractor
            else DpathExtractor(
                [],
                config=config,
                decoder=download_decoder,
                parameters=model.parameters or {},
            )
        )
        download_requester = self._create_component_from_model(
            model=model.download_requester,
            decoder=download_decoder,
            config=config,
            name=job_download_components_name,
        )
        download_retriever = _get_download_retriever(
            download_requester, download_extractor, download_decoder
        )
        abort_requester = (
            self._create_component_from_model(
                model=model.abort_requester,
                decoder=decoder,
                config=config,
                name=f"job abort - {name}",
            )
            if model.abort_requester
            else None
        )
        delete_requester = (
            self._create_component_from_model(
                model=model.delete_requester,
                decoder=decoder,
                config=config,
                name=f"job delete - {name}",
            )
            if model.delete_requester
            else None
        )
        download_target_requester = (
            self._create_component_from_model(
                model=model.download_target_requester,
                decoder=decoder,
                config=config,
                name=f"job extract_url - {name}",
            )
            if model.download_target_requester
            else None
        )
        status_extractor = self._create_component_from_model(
            model=model.status_extractor, decoder=decoder, config=config, name=name
        )
        download_target_extractor = (
            self._create_component_from_model(
                model=model.download_target_extractor,
                decoder=decoder,
                config=config,
                name=name,
            )
            if model.download_target_extractor
            else None
        )

        job_repository: AsyncJobRepository = AsyncHttpJobRepository(
            creation_requester=creation_requester,
            polling_requester=polling_requester,
            download_retriever=download_retriever,
            download_target_requester=download_target_requester,
            abort_requester=abort_requester,
            delete_requester=delete_requester,
            status_extractor=status_extractor,
            status_mapping=self._create_async_job_status_mapping(model.status_mapping, config),
            download_target_extractor=download_target_extractor,
            job_timeout=_get_job_timeout(),
        )

        async_job_partition_router = AsyncJobPartitionRouter(
            job_orchestrator_factory=lambda stream_slices: AsyncJobOrchestrator(
                job_repository,
                stream_slices,
                self._job_tracker,
                self._message_repository,
                # FIXME work would need to be done here in order to detect if a stream as a parent stream that is bulk
                has_bulk_parent=False,
                # set the `job_max_retry` to 1 for the `Connector Builder`` use-case.
                # `None` == default retry is set to 3 attempts, under the hood.
                job_max_retry=1 if self._emit_connector_builder_messages else None,
            ),
            stream_slicer=stream_slicer,
            config=config,
            parameters=model.parameters or {},
        )

        return AsyncRetriever(
            record_selector=record_selector,
            stream_slicer=async_job_partition_router,
            config=config,
            parameters=model.parameters or {},
        )

    def create_spec(self, model: SpecModel, config: Config, **kwargs: Any) -> Spec:
        config_migrations = [
            self._create_component_from_model(migration, config)
            for migration in (
                model.config_normalization_rules.config_migrations
                if (
                    model.config_normalization_rules
                    and model.config_normalization_rules.config_migrations
                )
                else []
            )
        ]
        config_transformations = [
            self._create_component_from_model(transformation, config)
            for transformation in (
                model.config_normalization_rules.transformations
                if (
                    model.config_normalization_rules
                    and model.config_normalization_rules.transformations
                )
                else []
            )
        ]
        config_validations = [
            self._create_component_from_model(validation, config)
            for validation in (
                model.config_normalization_rules.validations
                if (
                    model.config_normalization_rules
                    and model.config_normalization_rules.validations
                )
                else []
            )
        ]

        return Spec(
            connection_specification=model.connection_specification,
            documentation_url=model.documentation_url,
            advanced_auth=model.advanced_auth,
            parameters={},
            config_migrations=config_migrations,
            config_transformations=config_transformations,
            config_validations=config_validations,
        )

    def create_substream_partition_router(
        self,
        model: SubstreamPartitionRouterModel,
        config: Config,
        *,
        stream_name: str,
        **kwargs: Any,
    ) -> SubstreamPartitionRouter:
        parent_stream_configs = []
        if model.parent_stream_configs:
            parent_stream_configs.extend(
                [
                    self.create_parent_stream_config_with_substream_wrapper(
                        model=parent_stream_config, config=config, stream_name=stream_name, **kwargs
                    )
                    for parent_stream_config in model.parent_stream_configs
                ]
            )

        return SubstreamPartitionRouter(
            parent_stream_configs=parent_stream_configs,
            parameters=model.parameters or {},
            config=config,
        )

    def create_parent_stream_config_with_substream_wrapper(
        self, model: ParentStreamConfigModel, config: Config, *, stream_name: str, **kwargs: Any
    ) -> Any:
        # getting the parent state
        child_state = self._connector_state_manager.get_stream_state(stream_name, None)

        # This flag will be used exclusively for StateDelegatingStream when a parent stream is created
        has_parent_state = bool(
            self._connector_state_manager.get_stream_state(stream_name, None)
            if model.incremental_dependency
            else False
        )
        connector_state_manager = self._instantiate_parent_stream_state_manager(
            child_state, config, model, has_parent_state
        )

        substream_factory = ModelToComponentFactory(
            connector_state_manager=connector_state_manager,
            limit_pages_fetched_per_slice=self._limit_pages_fetched_per_slice,
            limit_slices_fetched=self._limit_slices_fetched,
            emit_connector_builder_messages=self._emit_connector_builder_messages,
            disable_retries=self._disable_retries,
            disable_cache=self._disable_cache,
            message_repository=StateFilteringMessageRepository(
                LogAppenderMessageRepositoryDecorator(
                    {
                        "airbyte_cdk": {"stream": {"is_substream": True}},
                        "http": {"is_auxiliary": True},
                    },
                    self._message_repository,
                    self._evaluate_log_level(self._emit_connector_builder_messages),
                ),
            ),
        )

        return substream_factory.create_parent_stream_config(
            model=model, config=config, stream_name=stream_name, **kwargs
        )

    def _instantiate_parent_stream_state_manager(
        self,
        child_state: MutableMapping[str, Any],
        config: Config,
        model: ParentStreamConfigModel,
        has_parent_state: bool,
    ) -> ConnectorStateManager:
        """
        With DefaultStream, the state needs to be provided during __init__ of the cursor as opposed to the
        `set_initial_state` flow that existed for the declarative cursors. This state is taken from
        self._connector_state_manager.get_stream_state (`self` being a newly created ModelToComponentFactory to account
        for the MessageRepository being different). So we need to pass a ConnectorStateManager to the
        ModelToComponentFactory that has the parent states. This method populates this if there is a child state and if
        incremental_dependency is set.
        """
        if model.incremental_dependency and child_state:
            parent_stream_name = model.stream.name or ""
            parent_state = ConcurrentPerPartitionCursor.get_parent_state(
                child_state, parent_stream_name
            )

            if not parent_state:
                # there are two migration cases: state value from child stream or from global state
                parent_state = ConcurrentPerPartitionCursor.get_global_state(
                    child_state, parent_stream_name
                )

                if not parent_state and not isinstance(parent_state, dict):
                    cursor_values = child_state.values()
                    if cursor_values and len(cursor_values) == 1:
                        # We assume the child state is a pair `{<cursor_field>: <cursor_value>}` and we will use the
                        # cursor value as a parent state.
                        incremental_sync_model: Union[
                            DatetimeBasedCursorModel,
                            IncrementingCountCursorModel,
                        ] = (
                            model.stream.incremental_sync  # type: ignore  # if we are there, it is because there is incremental_dependency and therefore there is an incremental_sync on the parent stream
                            if isinstance(model.stream, DeclarativeStreamModel)
                            else self._get_state_delegating_stream_model(
                                has_parent_state, model.stream
                            ).incremental_sync
                        )
                        cursor_field = InterpolatedString.create(
                            incremental_sync_model.cursor_field,
                            parameters=incremental_sync_model.parameters or {},
                        ).eval(config)
                        parent_state = AirbyteStateMessage(
                            type=AirbyteStateType.STREAM,
                            stream=AirbyteStreamState(
                                stream_descriptor=StreamDescriptor(
                                    name=parent_stream_name, namespace=None
                                ),
                                stream_state=AirbyteStateBlob(
                                    {cursor_field: list(cursor_values)[0]}
                                ),
                            ),
                        )
            return ConnectorStateManager([parent_state] if parent_state else [])

        return ConnectorStateManager([])

    @staticmethod
    def create_wait_time_from_header(
        model: WaitTimeFromHeaderModel, config: Config, **kwargs: Any
    ) -> WaitTimeFromHeaderBackoffStrategy:
        return WaitTimeFromHeaderBackoffStrategy(
            header=model.header,
            parameters=model.parameters or {},
            config=config,
            regex=model.regex,
            max_waiting_time_in_seconds=model.max_waiting_time_in_seconds
            if model.max_waiting_time_in_seconds is not None
            else None,
        )

    @staticmethod
    def create_wait_until_time_from_header(
        model: WaitUntilTimeFromHeaderModel, config: Config, **kwargs: Any
    ) -> WaitUntilTimeFromHeaderBackoffStrategy:
        return WaitUntilTimeFromHeaderBackoffStrategy(
            header=model.header,
            parameters=model.parameters or {},
            config=config,
            min_wait=model.min_wait,
            regex=model.regex,
        )

    def get_message_repository(self) -> MessageRepository:
        return self._message_repository

    def _evaluate_log_level(self, emit_connector_builder_messages: bool) -> Level:
        return Level.DEBUG if emit_connector_builder_messages else Level.INFO

    @staticmethod
    def create_components_mapping_definition(
        model: ComponentMappingDefinitionModel, config: Config, **kwargs: Any
    ) -> ComponentMappingDefinition:
        interpolated_value = InterpolatedString.create(
            model.value, parameters=model.parameters or {}
        )
        field_path = [
            InterpolatedString.create(path, parameters=model.parameters or {})
            for path in model.field_path
        ]
        return ComponentMappingDefinition(
            field_path=field_path,  # type: ignore[arg-type] # field_path can be str and InterpolatedString
            value=interpolated_value,
            value_type=ModelToComponentFactory._json_schema_type_name_to_type(model.value_type),
            create_or_update=model.create_or_update,
            condition=model.condition,
            parameters=model.parameters or {},
        )

    def create_http_components_resolver(
        self, model: HttpComponentsResolverModel, config: Config, stream_name: Optional[str] = None
    ) -> Any:
        retriever = self._create_component_from_model(
            model=model.retriever,
            config=config,
            name=f"{stream_name if stream_name else '__http_components_resolver'}",
            primary_key=None,
            stream_slicer=self._build_stream_slicer_from_partition_router(model.retriever, config),
            transformations=[],
        )

        components_mapping = []
        for component_mapping_definition_model in model.components_mapping:
            if component_mapping_definition_model.condition:
                raise ValueError("`condition` is only supported for     `ConfigComponentsResolver`")
            components_mapping.append(
                self._create_component_from_model(
                    model=component_mapping_definition_model,
                    value_type=ModelToComponentFactory._json_schema_type_name_to_type(
                        component_mapping_definition_model.value_type
                    ),
                    config=config,
                )
            )

        return HttpComponentsResolver(
            retriever=retriever,
            stream_slicer=self._build_stream_slicer_from_partition_router(model.retriever, config),
            config=config,
            components_mapping=components_mapping,
            parameters=model.parameters or {},
        )

    @staticmethod
    def create_stream_config(
        model: StreamConfigModel, config: Config, **kwargs: Any
    ) -> StreamConfig:
        model_configs_pointer: List[Union[InterpolatedString, str]] = (
            [x for x in model.configs_pointer] if model.configs_pointer else []
        )

        return StreamConfig(
            configs_pointer=model_configs_pointer,
            default_values=model.default_values,
            parameters=model.parameters or {},
        )

    def create_config_components_resolver(
        self,
        model: ConfigComponentsResolverModel,
        config: Config,
    ) -> Any:
        model_stream_configs = (
            model.stream_config if isinstance(model.stream_config, list) else [model.stream_config]
        )

        stream_configs = [
            self._create_component_from_model(
                stream_config, config=config, parameters=model.parameters or {}
            )
            for stream_config in model_stream_configs
        ]

        components_mapping = [
            self._create_component_from_model(
                model=components_mapping_definition_model,
                value_type=ModelToComponentFactory._json_schema_type_name_to_type(
                    components_mapping_definition_model.value_type
                ),
                config=config,
                parameters=model.parameters,
            )
            for components_mapping_definition_model in model.components_mapping
        ]

        return ConfigComponentsResolver(
            stream_configs=stream_configs,
            config=config,
            components_mapping=components_mapping,
            parameters=model.parameters or {},
        )

    def create_parametrized_components_resolver(
        self,
        model: ParametrizedComponentsResolverModel,
        config: Config,
    ) -> ParametrizedComponentsResolver:
        stream_parameters = StreamParametersDefinition(
            list_of_parameters_for_stream=model.stream_parameters.list_of_parameters_for_stream
        )

        components_mapping = []
        for components_mapping_definition_model in model.components_mapping:
            if components_mapping_definition_model.condition:
                raise ValueError("`condition` is only supported for `ConfigComponentsResolver`")
            components_mapping.append(
                self._create_component_from_model(
                    model=components_mapping_definition_model,
                    value_type=ModelToComponentFactory._json_schema_type_name_to_type(
                        components_mapping_definition_model.value_type
                    ),
                    config=config,
                )
            )
        return ParametrizedComponentsResolver(
            stream_parameters=stream_parameters,
            config=config,
            components_mapping=components_mapping,
            parameters=model.parameters or {},
        )

    _UNSUPPORTED_DECODER_ERROR = (
        "Specified decoder of {decoder_type} is not supported for pagination."
        "Please set as `JsonDecoder`, `XmlDecoder`, or a `CompositeRawDecoder` with an inner_parser of `JsonParser` or `GzipParser` instead."
        "If using `GzipParser`, please ensure that the lowest level inner_parser is a `JsonParser`."
    )

    def _is_supported_decoder_for_pagination(self, decoder: Decoder) -> bool:
        if isinstance(decoder, (JsonDecoder, XmlDecoder)):
            return True
        elif isinstance(decoder, CompositeRawDecoder):
            return self._is_supported_parser_for_pagination(decoder.parser)
        else:
            return False

    def _is_supported_parser_for_pagination(self, parser: Parser) -> bool:
        if isinstance(parser, JsonParser):
            return True
        elif isinstance(parser, GzipParser):
            return isinstance(parser.inner_parser, JsonParser)
        else:
            return False

    def create_http_api_budget(
        self, model: HTTPAPIBudgetModel, config: Config, **kwargs: Any
    ) -> HttpAPIBudget:
        policies = [
            self._create_component_from_model(model=policy, config=config)
            for policy in model.policies
        ]

        return HttpAPIBudget(
            policies=policies,
            ratelimit_reset_header=model.ratelimit_reset_header or "ratelimit-reset",
            ratelimit_remaining_header=model.ratelimit_remaining_header or "ratelimit-remaining",
            status_codes_for_ratelimit_hit=model.status_codes_for_ratelimit_hit or [429],
        )

    def create_fixed_window_call_rate_policy(
        self, model: FixedWindowCallRatePolicyModel, config: Config, **kwargs: Any
    ) -> FixedWindowCallRatePolicy:
        matchers = [
            self._create_component_from_model(model=matcher, config=config)
            for matcher in model.matchers
        ]

        # Set the initial reset timestamp to 10 days from now.
        # This value will be updated by the first request.
        return FixedWindowCallRatePolicy(
            next_reset_ts=datetime.datetime.now() + datetime.timedelta(days=10),
            period=parse_duration(model.period),
            call_limit=model.call_limit,
            matchers=matchers,
        )

    def create_file_uploader(
        self, model: FileUploaderModel, config: Config, **kwargs: Any
    ) -> FileUploader:
        name = "File Uploader"
        requester = self._create_component_from_model(
            model=model.requester,
            config=config,
            name=name,
            **kwargs,
        )
        download_target_extractor = self._create_component_from_model(
            model=model.download_target_extractor,
            config=config,
            name=name,
            **kwargs,
        )
        emit_connector_builder_messages = self._emit_connector_builder_messages
        file_uploader = DefaultFileUploader(
            requester=requester,
            download_target_extractor=download_target_extractor,
            config=config,
            file_writer=NoopFileWriter()
            if emit_connector_builder_messages
            else LocalFileSystemFileWriter(),
            parameters=model.parameters or {},
            filename_extractor=model.filename_extractor if model.filename_extractor else None,
        )

        return (
            ConnectorBuilderFileUploader(file_uploader)
            if emit_connector_builder_messages
            else file_uploader
        )

    def create_moving_window_call_rate_policy(
        self, model: MovingWindowCallRatePolicyModel, config: Config, **kwargs: Any
    ) -> MovingWindowCallRatePolicy:
        rates = [
            self._create_component_from_model(model=rate, config=config) for rate in model.rates
        ]
        matchers = [
            self._create_component_from_model(model=matcher, config=config)
            for matcher in model.matchers
        ]
        return MovingWindowCallRatePolicy(
            rates=rates,
            matchers=matchers,
        )

    def create_unlimited_call_rate_policy(
        self, model: UnlimitedCallRatePolicyModel, config: Config, **kwargs: Any
    ) -> UnlimitedCallRatePolicy:
        matchers = [
            self._create_component_from_model(model=matcher, config=config)
            for matcher in model.matchers
        ]

        return UnlimitedCallRatePolicy(
            matchers=matchers,
        )

    def create_rate(self, model: RateModel, config: Config, **kwargs: Any) -> Rate:
        interpolated_limit = InterpolatedString.create(str(model.limit), parameters={})
        return Rate(
            limit=int(interpolated_limit.eval(config=config)),
            interval=parse_duration(model.interval),
        )

    def create_http_request_matcher(
        self, model: HttpRequestRegexMatcherModel, config: Config, **kwargs: Any
    ) -> HttpRequestRegexMatcher:
        return HttpRequestRegexMatcher(
            method=model.method,
            url_base=model.url_base,
            url_path_pattern=model.url_path_pattern,
            params=model.params,
            headers=model.headers,
        )

    def set_api_budget(self, component_definition: ComponentDefinition, config: Config) -> None:
        self._api_budget = self.create_component(
            model_type=HTTPAPIBudgetModel, component_definition=component_definition, config=config
        )

    def create_grouping_partition_router(
        self,
        model: GroupingPartitionRouterModel,
        config: Config,
        *,
        stream_name: str,
        **kwargs: Any,
    ) -> GroupingPartitionRouter:
        underlying_router = self._create_component_from_model(
            model=model.underlying_partition_router,
            config=config,
            stream_name=stream_name,
            **kwargs,
        )
        if model.group_size < 1:
            raise ValueError(f"Group size must be greater than 0, got {model.group_size}")

        # Request options in underlying partition routers are not supported for GroupingPartitionRouter
        # because they are specific to individual partitions and cannot be aggregated or handled
        # when grouping, potentially leading to incorrect API calls. Any request customization
        # should be managed at the stream level through the requester's configuration.
        if isinstance(underlying_router, SubstreamPartitionRouter):
            if any(
                parent_config.request_option
                for parent_config in underlying_router.parent_stream_configs
            ):
                raise ValueError("Request options are not supported for GroupingPartitionRouter.")

        if isinstance(underlying_router, ListPartitionRouter):
            if underlying_router.request_option:
                raise ValueError("Request options are not supported for GroupingPartitionRouter.")

        return GroupingPartitionRouter(
            group_size=model.group_size,
            underlying_partition_router=underlying_router,
            deduplicate=model.deduplicate if model.deduplicate is not None else True,
            config=config,
        )

    def _ensure_query_properties_to_model(
        self, requester: Union[HttpRequesterModel, CustomRequesterModel]
    ) -> None:
        """
        For some reason, it seems like CustomRequesterModel request_parameters stays as dictionaries which means that
        the other conditions relying on it being QueryPropertiesModel instead of a dict fail. Here, we migrate them to
        proper model.
        """
        if not hasattr(requester, "request_parameters"):
            return

        request_parameters = requester.request_parameters
        if request_parameters and isinstance(request_parameters, Dict):
            for request_parameter_key in request_parameters.keys():
                request_parameter = request_parameters[request_parameter_key]
                if (
                    isinstance(request_parameter, Dict)
                    and request_parameter.get("type") == "QueryProperties"
                ):
                    request_parameters[request_parameter_key] = QueryPropertiesModel.parse_obj(
                        request_parameter
                    )
