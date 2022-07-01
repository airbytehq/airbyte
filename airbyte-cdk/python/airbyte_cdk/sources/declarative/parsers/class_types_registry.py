#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type

from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.declarative.requesters.paginators.offset_paginator import OffsetPaginator
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.stream_slicers.cartesian_product_stream_slicer import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

CLASS_TYPES_REGISTRY: Mapping[str, Type] = {
    "NextPageUrlPaginator": NextPageUrlPaginator,
    "InterpolatedPaginator": InterpolatedPaginator,
    "OffsetPaginator": OffsetPaginator,
    "NoPaginator": NoPagination,
    "TokenAuthenticator": TokenAuthenticator,
    "DatetimeStreamSlicer": DatetimeStreamSlicer,
    "CartesianProductStreamSlicer": CartesianProductStreamSlicer,
    "ListStreamSlicer": ListStreamSlicer,
    "ConstantBackoffStrategy": ConstantBackoffStrategy,
}
