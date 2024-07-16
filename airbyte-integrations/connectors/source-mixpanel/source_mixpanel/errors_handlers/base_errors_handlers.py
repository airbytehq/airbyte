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


class DateSlicesMixinErrorHandler(HttpStatusErrorHandler):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            if (
                response_or_exception.status_code == requests.codes.bad_request
                and "to_date cannot be later than today" in response_or_exception.text
            ):
                self.stream._timezone_mismatch = True
                message = "Your project timezone must be misconfigured. Please set it to the one defined in your Mixpanel project settings. Stopping current stream sync."
                return ErrorResolution(
                    response_action=ResponseAction.IGNORE,
                    failure_type=FailureType.config_error,
                    error_message=message,
                )
        return super().interpret_response(response_or_exception)
