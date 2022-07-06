#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type

from airbyte_cdk.sources.declarative.requesters.paginators.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.limit_paginator import LimitPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.declarative.requesters.paginators.offset_increment import OffsetIncrement
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.retriers.chain_retrier import ChainRetrier
from airbyte_cdk.sources.declarative.requesters.retriers.default_retrier import DefaultRetrier
from airbyte_cdk.sources.declarative.stream_slicers.cartesian_product_stream_slicer import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

CLASS_TYPES_REGISTRY: Mapping[str, Type] = {
    "NextPageUrlPaginator": NextPageUrlPaginator,
    "InterpolatedPaginator": InterpolatedPaginator,
    "NoPaginator": NoPagination,
    "TokenAuthenticator": TokenAuthenticator,
    "DatetimeStreamSlicer": DatetimeStreamSlicer,
    "CartesianProductStreamSlicer": CartesianProductStreamSlicer,
    "ListStreamSlicer": ListStreamSlicer,
    "ConstantBackoffStrategy": ConstantBackoffStrategy,
    "ChainRetrier": ChainRetrier,
    "DefaultRetrier": DefaultRetrier,
    "LimitPaginator": LimitPaginator,
    "OffsetIncrement": OffsetIncrement,
    "CursorPagination": CursorPaginationStrategy,
}
