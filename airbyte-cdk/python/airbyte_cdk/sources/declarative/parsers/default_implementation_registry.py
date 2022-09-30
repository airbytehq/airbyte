#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type

from airbyte_cdk.sources.declarative.checks.check_stream import CheckStream
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.default_paginator import RequestOption
from airbyte_cdk.sources.declarative.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema.json_schema import JsonSchema
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.stream_slicers.single_slice import SingleSlice
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.substream_slicer import ParentStreamConfig
from airbyte_cdk.sources.streams.core import Stream

"""
DEFAULT_IMPLEMENTATIONS_REGISTRY contains a mapping of interface -> subclass
enabling the factory to instantiate a reasonable default class when no type or classname is specified
"""
DEFAULT_IMPLEMENTATIONS_REGISTRY: Mapping[Type, Type] = {
    ConnectionChecker: CheckStream,
    Decoder: JsonDecoder,
    ErrorHandler: DefaultErrorHandler,
    HttpResponseFilter: HttpResponseFilter,
    HttpSelector: RecordSelector,
    InterpolatedBoolean: InterpolatedBoolean,
    InterpolatedRequestOptionsProvider: InterpolatedRequestOptionsProvider,
    InterpolatedString: InterpolatedString,
    MinMaxDatetime: MinMaxDatetime,
    Paginator: NoPagination,
    ParentStreamConfig: ParentStreamConfig,
    RecordExtractor: DpathExtractor,
    RequestOption: RequestOption,
    RequestOptionsProvider: InterpolatedRequestOptionsProvider,
    Requester: HttpRequester,
    Retriever: SimpleRetriever,
    SchemaLoader: JsonSchema,
    Stream: DeclarativeStream,
    StreamSlicer: SingleSlice,
}
