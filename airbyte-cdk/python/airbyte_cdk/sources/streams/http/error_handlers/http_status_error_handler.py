# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from typing import Mapping, Optional, Type, Union

import requests
from airbyte_cdk.models import FailureType
from requests import RequestException

from .error_handler import ErrorHandler
from .response_models import ErrorResolution, ResponseAction


class HttpStatusErrorHandler(ErrorHandler):

    _DEFAULT_ERROR_MAPPING: Mapping[Union[int, str, Type[Exception]], ErrorResolution] = {
        RequestException: ErrorResolution(
            response_action=ResponseAction.RETRY,
            failure_type=FailureType.transient_error,
            error_message="An exception occurred when making the request.",
        ),
        400: ErrorResolution(
            response_action=ResponseAction.FAIL,
            failure_type=FailureType.system_error,
            error_message="Bad request. Please check your request parameters.",
        ),
        401: ErrorResolution(
            response_action=ResponseAction.FAIL,
            failure_type=FailureType.config_error,
            error_message="Unauthorized. Please ensure you are authenticated correctly.",
        ),
        403: ErrorResolution(
            response_action=ResponseAction.FAIL,
            failure_type=FailureType.config_error,
            error_message="Forbidden. You don't have permission to access this resource.",
        ),
        404: ErrorResolution(
            response_action=ResponseAction.FAIL,
            failure_type=FailureType.system_error,
            error_message="Not found. The requested resource was not found on the server.",
        ),
        405: ErrorResolution(
            response_action=ResponseAction.FAIL,
            failure_type=FailureType.system_error,
            error_message="Method not allowed. Please check your request method.",
        ),
        408: ErrorResolution(
            response_action=ResponseAction.RETRY,
            failure_type=FailureType.transient_error,
            error_message="Request timeout.",
        ),
        429: ErrorResolution(
            response_action=ResponseAction.RETRY,
            failure_type=FailureType.transient_error,
            error_message="Too many requests.",
        ),
        500: ErrorResolution(
            response_action=ResponseAction.RETRY,
            failure_type=FailureType.transient_error,
            error_message="Internal server error.",
        ),
        502: ErrorResolution(
            response_action=ResponseAction.RETRY,
            failure_type=FailureType.transient_error,
            error_message="Bad gateway.",
        ),
        503: ErrorResolution(
            response_action=ResponseAction.RETRY,
            failure_type=FailureType.transient_error,
            error_message="Service unavailable.",
        ),
        504: ErrorResolution(
            response_action=ResponseAction.RETRY,
            failure_type=FailureType.transient_error,
            error_message="Gateway timeout.",
        ),
    }

    def __init__(
        self,
        logger: logging.Logger,
        error_mapping: Optional[Mapping[Union[int, str, type[Exception]], ErrorResolution]] = None,
    ) -> None:
        """
        Initialize the HttpStatusErrorHandler.

        :param error_mapping: Custom error mappings to extend or override the default mappings.
        """
        self._logger = logger
        self._error_mapping = error_mapping or self._DEFAULT_ERROR_MAPPING

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
