# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import FailureType

from .error_handler import ErrorHandler
from .error_mapping import ErrorMapping
from .response_action import ResponseAction


class HttpStatusErrorHandler(ErrorHandler):
    def __init__(
        self, error_mapping: Optional[Mapping[Union[int, str], Mapping[str, Any]]] = None, extend_default_mapping: bool = True
    ) -> None:
        """
        Initialize the HttpStatusErrorHandler.

        :param error_mapping: Custom error mappings to extend or override the default mappings.
        :param extend_default_mapping: Whether to extend the default mapping with custom mappings.
        """
        self._error_mapping = ErrorMapping(error_mapping)
        if extend_default_mapping:
            self._error_mapping.update_error_mapping(error_mapping)

    def interpret_response(
        self, response: Optional[requests.Response], exception: Optional[Exception]
    ) -> Optional[Tuple[ResponseAction, FailureType, str]]:
        """
        Interpret the response or exception and return the corresponding response action, failure type, and error message.

        :param response: The HTTP response object.
        :param exception: The exception raised during the request.
        :return: A tuple containing the response action, failure type, and error message.
        :raises ValueError: If both response and exception are provided or if the error is not mapped.
        """

        if response and exception:
            raise ValueError("Only one of response and exception should be provided")

        error_key = exception if exception else response.status_code

        mapped_error = self._error_mapping.get_error_mapping(error_key)

        if mapped_error is None:
            raise ValueError(f"Unexpected {'exception' if exception else 'HTTP status code'}: {error_key}")

        response_action = mapped_error.get("action", None)
        response_failure_type = mapped_error.get("failure_type", None)
        error_message = mapped_error.get("error_message", None)

        return response_action, response_failure_type, error_message
