#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type

from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.extractors.jello import JelloExtractor
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.offset_paginator import OffsetPaginator
from airbyte_cdk.sources.declarative.stream_slicers.cartesian_product_stream_slicer import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer
from airbyte_cdk.sources.declarative.transformations import RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddFields
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

CLASS_TYPES_REGISTRY: Mapping[str, Type] = {
    "AddFields": AddFields,
    "CartesianProductStreamSlicer": CartesianProductStreamSlicer,
    "CompositeErrorHandler": CompositeErrorHandler,
    "ConstantBackoffStrategy": ConstantBackoffStrategy,
    "DatetimeStreamSlicer": DatetimeStreamSlicer,
    "DeclarativeStream": DeclarativeStream,
    "DefaultErrorHandler": DefaultErrorHandler,
    "ExponentialBackoffStrategy": ExponentialBackoffStrategy,
    "HttpRequester": HttpRequester,
    "InterpolatedPaginator": InterpolatedPaginator,
    "JelloExtractor": JelloExtractor,
    "ListStreamSlicer": ListStreamSlicer,
    "MinMaxDatetime": MinMaxDatetime,
    "NextPageUrlPaginator": NextPageUrlPaginator,
    "OffsetPaginator": OffsetPaginator,
    "RemoveFields": RemoveFields,
    "TokenAuthenticator": TokenAuthenticator,
}
