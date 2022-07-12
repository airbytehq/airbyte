#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type

from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.offset_paginator import OffsetPaginator
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.transformations import RemoveFields
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

CLASS_TYPES_REGISTRY: Mapping[str, Type] = {
    "DatetimeStreamSlicer": DatetimeStreamSlicer,
    "InterpolatedPaginator": InterpolatedPaginator,
    "MinMaxDatetime": MinMaxDatetime,
    "NextPageUrlPaginator": NextPageUrlPaginator,
    "OffsetPaginator": OffsetPaginator,
    "TokenAuthenticator": TokenAuthenticator,
    "RemoveFields": RemoveFields,
}
