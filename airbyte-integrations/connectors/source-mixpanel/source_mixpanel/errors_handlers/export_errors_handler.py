#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

import requests

from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_protocol.models import FailureType

from .base_errors_handler import MixpanelStreamErrorHandler


class ExportErrorHandler(MixpanelStreamErrorHandler):
    """
    Custom error handler for handling export errors specific to Mixpanel streams.

    This handler addresses:
    - 400 status code with "to_date cannot be later than today" message, indicating a potential timezone mismatch.
    - ConnectionResetError during response parsing, indicating a need to retry the request.

    If the response does not match these specific cases, the handler defers to the parent class's implementation.

    Attributes:
        stream (HttpStream): The HTTP stream associated with this error handler.
    """

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
            try:
                # trying to parse response to avoid ConnectionResetError and retry if it occurs
                self.stream.iter_dicts(response_or_exception.iter_lines(decode_unicode=True))
            except ConnectionResetError:
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",
                )
        return super().interpret_response(response_or_exception)
