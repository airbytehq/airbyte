# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional, Union

import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, ResponseAction
from requests import exceptions

RESPONSE_CONSUMPTION_EXCEPTIONS = (
    exceptions.ChunkedEncodingError,
    exceptions.JSONDecodeError,
)

TRANSIENT_EXCEPTIONS = (
    exceptions.ConnectTimeout,
    exceptions.ConnectionError,
    exceptions.HTTPError,
    exceptions.ReadTimeout,
    # This error was added as part of the migration from REST to bulk (https://github.com/airbytehq/airbyte/commit/f5094041bebb80cd6602a98829c19a7515276ed3) but it is unclear in which case it occurs and why it is transient
    exceptions.SSLError,
) + RESPONSE_CONSUMPTION_EXCEPTIONS

_NO_ERROR_RESOLUTION = ErrorResolution(ResponseAction.SUCCESS, None, None)


class ShopifyErrorHandler(ErrorHandler):
    def __init__(self, stream_name: str = "<no specified stream>") -> None:
        self._stream_name = stream_name

    @property
    def max_retries(self) -> Optional[int]:
        return 5

    @property
    def max_time(self) -> Optional[int]:
        return 20

    def interpret_response(self, response: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        if isinstance(response, TRANSIENT_EXCEPTIONS):
            return ErrorResolution(
                ResponseAction.RETRY,
                FailureType.transient_error,
                f"Error of type {type(response)} is considered transient. Try again later. (full error message is {response})",
            )
        elif isinstance(response, requests.Response):
            if response.ok:
                return _NO_ERROR_RESOLUTION

            if response.status_code == 429 or response.status_code >= 500:
                return ErrorResolution(
                    ResponseAction.RETRY,
                    FailureType.transient_error,
                    f"Status code `{response.status_code}` is considered transient. Try again later. (full error message is {response.content})",
                )

        return _NO_ERROR_RESOLUTION  # Not all the error handling is defined here so it assumes the previous code will handle the error if there is one
