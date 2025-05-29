# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets
from requests import HTTPError


class ResponseAction(Enum):
    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    FAIL = "FAIL"
    IGNORE = "IGNORE"
    RATE_LIMITED = "RATE_LIMITED"


@dataclass
class ErrorResolution:
    response_action: Optional[ResponseAction] = None
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None


def _format_exception_error_message(exception: Exception) -> str:
    return f"{type(exception).__name__}: {str(exception)}"


def _format_response_error_message(response: requests.Response) -> str:
    try:
        response.raise_for_status()
    except HTTPError as exception:
        return filter_secrets(f"Response was not ok: `{str(exception)}`. Response content is: {response.text}")
    # We purposefully do not add the response.content because the response is "ok" so there might be sensitive information in the payload.
    # Feel free the
    return f"Unexpected response with HTTP status {response.status_code}"


def create_fallback_error_resolution(response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
    if response_or_exception is None:
        # We do not expect this case to happen but if it does, it would be good to understand the cause and improve the error message
        error_message = "Error handler did not receive a valid response or exception. This is unexpected please contact Airbyte Support"
    elif isinstance(response_or_exception, Exception):
        error_message = _format_exception_error_message(response_or_exception)
    else:
        error_message = _format_response_error_message(response_or_exception)

    return ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.system_error,
        error_message=error_message,
    )


SUCCESS_RESOLUTION = ErrorResolution(response_action=ResponseAction.SUCCESS, failure_type=None, error_message=None)
