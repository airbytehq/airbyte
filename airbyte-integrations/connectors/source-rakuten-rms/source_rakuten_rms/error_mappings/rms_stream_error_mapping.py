#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction

PARENT_INCREMENTAL_RMS_STREAM_ERROR_MAPPING = DEFAULT_ERROR_MAPPING | {
    404: ErrorResolution(
        response_action=ResponseAction.IGNORE,
        error_message="Data was not found for URL.",
    ),
}