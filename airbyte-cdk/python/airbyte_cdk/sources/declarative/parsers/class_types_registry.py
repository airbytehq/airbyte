#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Mapping

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.auth.jwt import JwtAuthenticator
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import (
    ApiKeyAuthenticator,
    BasicHttpAuthenticator,
    BearerAuthenticator,
    LegacySessionTokenAuthenticator,
)
from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.extractors import RecordFilter
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.cartesian_product_stream_slicer import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.partition_routers.list_partition_router import ListPartitionRouter
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.error_handlers import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_time_from_header_backoff_strategy import (
    WaitTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_until_time_from_header_backoff_strategy import (
    WaitUntilTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.default_paginator import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.offset_increment import OffsetIncrement
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema.inline_schema_loader import InlineSchemaLoader
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.sources.declarative.transformations import RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition, AddFields
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import SingleUseRefreshTokenOauth2Authenticator

"""
CLASS_TYPES_REGISTRY contains a mapping of developer-friendly string -> class to abstract the specific class referred to
"""
CLASS_TYPES_REGISTRY: Mapping[str, type] = {
    "AddedFieldDefinition": AddedFieldDefinition,
    "AddFields": AddFields,
    "ApiKeyAuthenticator": ApiKeyAuthenticator,
    "BasicHttpAuthenticator": BasicHttpAuthenticator,
    "BearerAuthenticator": BearerAuthenticator,
    "CartesianProductStreamSlicer": CartesianProductStreamSlicer,
    "CheckStream": CheckStream,
    "CompositeErrorHandler": CompositeErrorHandler,
    "ConstantBackoffStrategy": ConstantBackoffStrategy,
    "CursorPagination": CursorPaginationStrategy,
    "DatetimeBasedCursor": DatetimeBasedCursor,
    "DeclarativeStream": DeclarativeStream,
    "DefaultErrorHandler": DefaultErrorHandler,
    "DefaultPaginator": DefaultPaginator,
    "DpathExtractor": DpathExtractor,
    "ExponentialBackoffStrategy": ExponentialBackoffStrategy,
    "HttpRequester": HttpRequester,
    "HttpResponseFilter": HttpResponseFilter,
    "InlineSchemaLoader": InlineSchemaLoader,
    "InterpolatedBoolean": InterpolatedBoolean,
    "InterpolatedRequestOptionsProvider": InterpolatedRequestOptionsProvider,
    "InterpolatedString": InterpolatedString,
    "JsonFileSchemaLoader": JsonFileSchemaLoader,
    "JwtAuthenticator": JwtAuthenticator,
    "ListPartitionRouter": ListPartitionRouter,
    "MinMaxDatetime": MinMaxDatetime,
    "NoAuth": NoAuth,
    "NoPagination": NoPagination,
    "OAuthAuthenticator": DeclarativeOauth2Authenticator,
    "SingleUseRefreshTokenOAuthAuthenticator": SingleUseRefreshTokenOauth2Authenticator,
    "OffsetIncrement": OffsetIncrement,
    "PageIncrement": PageIncrement,
    "ParentStreamConfig": ParentStreamConfig,
    "RecordFilter": RecordFilter,
    "RecordSelector": RecordSelector,
    "RequestOption": RequestOption,
    "RemoveFields": RemoveFields,
    "SimpleRetriever": SimpleRetriever,
    "Spec": Spec,
    "SubstreamPartitionRouter": SubstreamPartitionRouter,
    "SessionTokenAuthenticator": LegacySessionTokenAuthenticator,
    "WaitUntilTimeFromHeader": WaitUntilTimeFromHeaderBackoffStrategy,
    "WaitTimeFromHeader": WaitTimeFromHeaderBackoffStrategy,
}
