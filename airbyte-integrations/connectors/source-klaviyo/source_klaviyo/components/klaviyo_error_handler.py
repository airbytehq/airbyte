# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional, Union

import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, ResponseAction
from requests.exceptions import InvalidURL


class KlaviyoErrorHandler(DefaultErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        if isinstance(response_or_exception, InvalidURL):
            return ErrorResolution(
                response_action=ResponseAction.RETRY,
                failure_type=FailureType.transient_error,
                error_message="source-klaviyo has faced a temporary DNS resolution issue. Retrying...",
            )
        return super().interpret_response(response_or_exception)
