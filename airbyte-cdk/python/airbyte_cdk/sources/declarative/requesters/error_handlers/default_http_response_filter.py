#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import DEFAULT_ERROR_RESOLUTION, ErrorResolution


class DefaultHttpResponseFilter(HttpResponseFilter):
    def matches(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> Optional[ErrorResolution]:

        default_mapped_error_resolution = None

        if isinstance(response_or_exception, (requests.Response, Exception)):

            mapped_key: Union[int, type] = (
                response_or_exception.status_code
                if isinstance(response_or_exception, requests.Response)
                else response_or_exception.__class__
            )

            default_mapped_error_resolution = DEFAULT_ERROR_MAPPING.get(mapped_key)

        return default_mapped_error_resolution if default_mapped_error_resolution else DEFAULT_ERROR_RESOLUTION
