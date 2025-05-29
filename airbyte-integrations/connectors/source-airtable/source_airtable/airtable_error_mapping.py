#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction

AIRTABLE_ERROR_MAPPING = DEFAULT_ERROR_MAPPING | {
    403: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message="Permission denied or entity is unprocessable.",
    ),
    422: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message="Permission denied or entity is unprocessable.",
    ),
}
