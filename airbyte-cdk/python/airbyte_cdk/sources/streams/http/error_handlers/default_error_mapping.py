#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type, Union

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction
from requests.exceptions import InvalidSchema, InvalidURL, RequestException

DEFAULT_ERROR_MAPPING: Mapping[Union[int, str, Type[Exception]], ErrorResolution] = {
    InvalidSchema: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message="Invalid Protocol Schema: The endpoint that data is being requested from is using an invalid or insecure. Exception: requests.exceptions.InvalidSchema",
    ),
    InvalidURL: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message="Invalid URL specified: The endpoint that data is being requested from is not a valid URL. Exception: requests.exceptions.InvalidURL",
    ),
    RequestException: ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.transient_error,
        error_message="An exception occurred when making the request. Exception: requests.exceptions.RequestException",
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
        response_action=ResponseAction.RATE_LIMITED,
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
