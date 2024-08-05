#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction
from source_stripe.error_mappings.stripe_error_mapping import STRIPE_ERROR_MAPPING

PARENT_INCREMENTAL_STRIPE_SUB_STREAM_ERROR_MAPPING = STRIPE_ERROR_MAPPING | {
    404: ErrorResolution(
        response_action=ResponseAction.IGNORE,
        failure_type=FailureType.config_error,
        error_message="Data was not found for URL.",
    ),
}
