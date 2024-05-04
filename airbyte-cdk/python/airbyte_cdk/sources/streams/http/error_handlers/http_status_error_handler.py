# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Mapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import FailureType

from .error_handler import ErrorHandler
from .response_action import ResponseAction


class HttpStatusErrorHandler(ErrorHandler):

    _DEFAULT_ERROR_MAPPING: Mapping[Union[int, str, Exception], Mapping[str, Any]] = {
        400: {
            "action": ResponseAction.FAIL,
            "failure_type": FailureType.config_error,
            "error_message": "Bad request. Please check your request parameters.",
        },
        401: {
            "action": ResponseAction.FAIL,
            "failure_type": FailureType.config_error,
            "error_message": "Unauthorized. Please ensure you are authenticated correctly.",
        },
        403: {
            "action": ResponseAction.FAIL,
            "failure_type": FailureType.config_error,
            "error_message": "Forbidden. You don't have permission to access this resource.",
        },
        404: {
            "action": ResponseAction.FAIL,
            "failure_type": FailureType.system_error,
            "error_message": "Not found. The requested resource was not found on the server.",
        },
        408: {
            "action": ResponseAction.FAIL,
            "failure_type": FailureType.transient_error,
            "error_message": "Request timeout. Please try again later.",
        },
        429: {
            "action": ResponseAction.FAIL,
            "failure_type": FailureType.transient_error,
            "error_message": "Too many requests. Please wait and try again later.",
        },
        500: {
            "action": ResponseAction.RETRY,
            "failure_type": FailureType.transient_error,
            "error_message": "Internal server error. Please try again later.",
        },
        502: {
            "action": ResponseAction.RETRY,
            "failure_type": FailureType.transient_error,
            "error_message": "Bad gateway. Please try again later.",
        },
        503: {
            "action": ResponseAction.RETRY,
            "failure_type": FailureType.transient_error,
            "error_message": "Service unavailable. Please try again later.",
        },
    }

    def __init__(
        self,
        logger: logging.Logger,
        error_mapping: Optional[Mapping[Union[int, str, Exception], Mapping[str, Any]]] = None,
    ) -> None:
        """
        Initialize the HttpStatusErrorHandler.

        :param error_mapping: Custom error mappings to extend or override the default mappings.
        """
        self._logger = logger
        self._error_mapping = error_mapping or self._DEFAULT_ERROR_MAPPING

    def interpret_response(
        self, response: Optional[Union[requests.Response, Exception]] = None
    ) -> Tuple[Optional[ResponseAction], Optional[FailureType], Optional[str]]:
        """
        Interpret the response and return the corresponding response action, failure type, and error message.

        :param response: The HTTP response object.
        :return: A tuple containing the response action, failure type, and error message.
        """

        if response is None:
            return ResponseAction.RETRY, FailureType.transient_error, None

        if isinstance(response, requests.Response):
            if response.status_code is None:
                self._logger.debug("Response does not include an HTTP status code.")
                return ResponseAction.RETRY, FailureType.transient_error, "Response does not include an HTTP status code."

            if response.ok:
                return None, None, None

            error_key = response.status_code
        else:
            self._logger.debug(f"Received unexpected response type: {type(response)}")
            return ResponseAction.RETRY, FailureType.transient_error, f"Received unexpected response type: {type(response)}"

        mapped_error = self._error_mapping.get(error_key)

        if mapped_error is not None:
            return (mapped_error.get("action"), mapped_error.get("failure_type"), mapped_error.get("error_message"))
        else:
            self._logger.debug(f"Unexpected 'HTTP Status Code' in error handler: {error_key}")
            return (ResponseAction.RETRY, FailureType.transient_error, f"Unexpected 'HTTP Status Code' in error handler: {error_key}")
