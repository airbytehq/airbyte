#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_http_response_filter import (
    DefaultHttpResponseFilter,
)
from airbyte_cdk.sources.streams.http.error_handlers.response_models import (
    SUCCESS_RESOLUTION,
    ErrorResolution,
    ResponseAction,
    create_fallback_error_resolution,
)


class LinearErrorHandler(DefaultErrorHandler):
    def interpret_response(
        self, response_or_exception: Optional[Union[requests.Response, Exception]]
    ) -> ErrorResolution:
        if self.response_filters:
            for response_filter in self.response_filters:
                matched_error_resolution = response_filter.matches(response_or_exception=response_or_exception)
                if matched_error_resolution:
                    if matched_error_resolution.response_action in (ResponseAction.RETRY, ResponseAction.RATE_LIMITED):
                        return ErrorResolution(
                            response_action=matched_error_resolution.response_action,
                            failure_type=FailureType.transient_error,
                            error_message=matched_error_resolution.error_message,
                        )
                    return matched_error_resolution

        if isinstance(response_or_exception, requests.Response) and response_or_exception.ok:
            return SUCCESS_RESOLUTION

        default_response_filter = DefaultHttpResponseFilter(parameters={}, config=self.config)
        default_response_filter_resolution = default_response_filter.matches(response_or_exception)
        return (
            default_response_filter_resolution
            if default_response_filter_resolution
            else create_fallback_error_resolution(response_or_exception)
        )
