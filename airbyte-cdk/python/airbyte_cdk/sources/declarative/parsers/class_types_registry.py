#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type

from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.paginators.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.limit_paginator import LimitPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.declarative.requesters.paginators.offset_increment import OffsetIncrement
from airbyte_cdk.sources.declarative.stream_slicers.cartesian_product_stream_slicer import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer
from airbyte_cdk.sources.declarative.transformations import RemoveFields
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

CLASS_TYPES_REGISTRY: Mapping[str, Type] = {
    "DatetimeStreamSlicer": DatetimeStreamSlicer,
    "MinMaxDatetime": MinMaxDatetime,
    "NoPaginator": NoPagination,
    "TokenAuthenticator": TokenAuthenticator,
    "CartesianProductStreamSlicer": CartesianProductStreamSlicer,
    "ListStreamSlicer": ListStreamSlicer,
    "ConstantBackoffStrategy": ConstantBackoffStrategy,
    "LimitPaginator": LimitPaginator,
    "OffsetIncrement": OffsetIncrement,
    "CursorPagination": CursorPaginationStrategy,
    "ExponentialBackoffStrategy": ExponentialBackoffStrategy,
    "CompositeErrorHandler": CompositeErrorHandler,
    "DefaultErrorHandler": DefaultErrorHandler,
    "RemoveFields": RemoveFields,
}
