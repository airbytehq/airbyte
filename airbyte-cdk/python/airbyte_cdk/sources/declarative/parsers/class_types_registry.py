#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import ApiKeyAuthenticator, BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.limit_paginator import LimitPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.offset_increment import OffsetIncrement
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema.json_schema import JsonSchema
from airbyte_cdk.sources.declarative.stream_slicers.cartesian_product_stream_slicer import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.substream_slicer import SubstreamSlicer
from airbyte_cdk.sources.declarative.transformations import RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddFields

"""
CLASS_TYPES_REGISTRY contains a mapping of developer-friendly string -> class to abstract the specific class referred to
"""
CLASS_TYPES_REGISTRY: Mapping[str, Type] = {
    "AddFields": AddFields,
    "ApiKeyAuthenticator": ApiKeyAuthenticator,
    "BasicHttpAuthenticator": BasicHttpAuthenticator,
    "BearerAuthenticator": BearerAuthenticator,
    "CartesianProductStreamSlicer": CartesianProductStreamSlicer,
    "CompositeErrorHandler": CompositeErrorHandler,
    "ConstantBackoffStrategy": ConstantBackoffStrategy,
    "CursorPagination": CursorPaginationStrategy,
    "DatetimeStreamSlicer": DatetimeStreamSlicer,
    "DeclarativeStream": DeclarativeStream,
    "DefaultErrorHandler": DefaultErrorHandler,
    "DpathExtractor": DpathExtractor,
    "ExponentialBackoffStrategy": ExponentialBackoffStrategy,
    "HttpRequester": HttpRequester,
    "InterpolatedBoolean": InterpolatedBoolean,
    "InterpolatedString": InterpolatedString,
    "JsonSchema": JsonSchema,
    "LimitPaginator": LimitPaginator,
    "ListStreamSlicer": ListStreamSlicer,
    "MinMaxDatetime": MinMaxDatetime,
    "NoAuth": NoAuth,
    "NoPagination": NoPagination,
    "OAuthAuthenticator": DeclarativeOauth2Authenticator,
    "OffsetIncrement": OffsetIncrement,
    "RecordSelector": RecordSelector,
    "RemoveFields": RemoveFields,
    "SimpleRetriever": SimpleRetriever,
    "SubstreamSlicer": SubstreamSlicer,
}
