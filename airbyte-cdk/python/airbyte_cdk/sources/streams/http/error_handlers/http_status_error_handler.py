# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Mapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import FailureType

from .error_handler import ErrorHandler
from .response_action import ResponseAction


class HttpStatusErrorHandler(ErrorHandler):

    _DEFAULT_ERROR_MAPPING: Mapping[Union[int, str], Mapping[str, Any]] = {
        400: {
            "action": ResponseAction.FAIL,
            "failure_type": FailureType.config_error,
            "error_message": "Placeholder error message for 400 -- TBD",
        },
        401: {"action": ResponseAction.FAIL, "failure_type": FailureType.config_error},
        403: {"action": ResponseAction.FAIL, "failure_type": FailureType.config_error},
        404: {"action": ResponseAction.FAIL, "failure_type": FailureType.system_error},
        408: {"action": ResponseAction.FAIL, "failure_type": FailureType.transient_error},
        429: {"action": ResponseAction.FAIL, "failure_type": FailureType.transient_error},
        500: {"action": ResponseAction.RETRY, "failure_type": FailureType.transient_error},
        502: {"action": ResponseAction.RETRY, "failure_type": FailureType.transient_error},
        503: {"action": ResponseAction.RETRY, "failure_type": FailureType.transient_error},
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
        self, response: Optional[Union[requests.Response, Exception]]
    ) -> Tuple[Optional[ResponseAction], Optional[FailureType], Optional[str]]:
        """
        Interpret the response and return the corresponding response action, failure type, and error message.

        :param response: The HTTP response object.
        :return: A tuple containing the response action, failure type, and error message.
        """

        if response.ok:
            return None, None, None

        error_key = response.status_code
        mapped_error = self._error_mapping.get(error_key, None)

        if mapped_error is not None:
            response_action = mapped_error.get("action", ResponseAction.RETRY)
            response_failure_type = mapped_error.get("failure_type", FailureType.transient_error)
            error_message = mapped_error.get("error_message", None)
        else:
            self._logger.debug(f"Unexpected 'HTTP Status Code' in error handler: {error_key}")
            response_action = ResponseAction.RETRY
            response_failure_type = FailureType.transient_error
            error_message = f"Unexpected 'HTTP Status Code' in error handler: {error_key}"

        return response_action, response_failure_type, error_message
