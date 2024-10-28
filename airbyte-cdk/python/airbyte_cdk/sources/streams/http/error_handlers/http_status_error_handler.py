#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import timedelta
from typing import Mapping, Optional, Union

import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction


class HttpStatusErrorHandler(ErrorHandler):
    def __init__(
        self,
        logger: logging.Logger,
        error_mapping: Optional[Mapping[Union[int, str, type[Exception]], ErrorResolution]] = None,
        max_retries: int = 5,
        max_time: timedelta = timedelta(seconds=600),
    ) -> None:
        """
        Initialize the HttpStatusErrorHandler.

        :param error_mapping: Custom error mappings to extend or override the default mappings.
        """
        self._logger = logger
        self._error_mapping = error_mapping or DEFAULT_ERROR_MAPPING
        self._max_retries = max_retries
        self._max_time = int(max_time.total_seconds())

    @property
    def max_retries(self) -> Optional[int]:
        return self._max_retries

    @property
    def max_time(self) -> Optional[int]:
        return self._max_time

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        """
        Interpret the response and return the corresponding response action, failure type, and error message.

        :param response: The HTTP response object.
        :return: A tuple containing the response action, failure type, and error message.
        """

        if isinstance(response_or_exception, Exception):
            mapped_error: Optional[ErrorResolution] = self._error_mapping.get(response_or_exception.__class__)

            if mapped_error is not None:
                return mapped_error
            else:
                self._logger.error(f"Unexpected exception in error handler: {response_or_exception}")
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.system_error,
                    error_message=f"Unexpected exception in error handler: {response_or_exception}",
                )

        elif isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code is None:
                self._logger.error("Response does not include an HTTP status code.")
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message="Response does not include an HTTP status code.",
                )

            if response_or_exception.ok:
                return ErrorResolution(
                    response_action=ResponseAction.SUCCESS,
                    failure_type=None,
                    error_message=None,
                )

            error_key = response_or_exception.status_code

            mapped_error = self._error_mapping.get(error_key)

            if mapped_error is not None:
                return mapped_error
            else:
                self._logger.warning(f"Unexpected HTTP Status Code in error handler: '{error_key}'")
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.system_error,
                    error_message=f"Unexpected HTTP Status Code in error handler: {error_key}",
                )
        else:
            self._logger.error(f"Received unexpected response type: {type(response_or_exception)}")
            return ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.system_error,
                error_message=f"Received unexpected response type: {type(response_or_exception)}",
            )
