#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction

STRIPE_ERROR_MAPPING = DEFAULT_ERROR_MAPPING | {
    429: ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.transient_error,
        error_message="Too many requests.",
    ),
}
