#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type

from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.offset_paginator import OffsetPaginator
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

CLASS_TYPES_REGISTRY: Mapping[str, Type] = {
    "NextPageUrlPaginator": NextPageUrlPaginator,
    "InterpolatedPaginator": InterpolatedPaginator,
    "OffsetPaginator": OffsetPaginator,
    "TokenAuthenticator": TokenAuthenticator,
}
