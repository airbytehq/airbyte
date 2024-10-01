#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import re
from typing import Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_protocol.models import FailureType


class MixpanelStreamErrorHandler(HttpStatusErrorHandler):
    """
    Custom error handler for Mixpanel stream that interprets responses and exceptions.

    This handler specifically addresses:
    - 400 status code with "Unable to authenticate request" message, indicating potential credential expiration.
    - 402 status code, indicating a payment required error.

    If the response does not match these specific cases, the handler defers to the parent class's implementation.
    """

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code == 400 and "Unable to authenticate request" in response_or_exception.text:
                message = (
                    f"Your credentials might have expired. Please update your config with valid credentials."
                    f" See more details: {response_or_exception.text}"
                )
                return ErrorResolution(
                    response_action=ResponseAction.FAIL,
                    failure_type=FailureType.config_error,
                    error_message=message,
                )
            elif response_or_exception.status_code == 402:
                message = f"Unable to perform a request. Payment Required: {response_or_exception.json()['error']}"
                return ErrorResolution(
                    response_action=ResponseAction.FAIL,
                    failure_type=FailureType.transient_error,
                    error_message=message,
                )
        return super().interpret_response(response_or_exception)
