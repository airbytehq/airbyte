#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from typing import Mapping, Type, Union

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution
from source_google_analytics_data_api.utils import WRONG_CUSTOM_REPORT_CONFIG


def get_google_analytics_data_api_base_error_mapping(report_name) -> Mapping[Union[int, str, Type[Exception]], ErrorResolution]:
    """
    Updating base default error messages friendly config error message that includes the steam report name
    """
    stream_error_mapping = {}
    for error_key, base_error_resolution in DEFAULT_ERROR_MAPPING.items():
        if base_error_resolution.failure_type in (FailureType.config_error, FailureType.system_error):
            stream_error_mapping[error_key] = ErrorResolution(
                response_action=base_error_resolution.response_action,
                failure_type=FailureType.config_error,
                error_message=WRONG_CUSTOM_REPORT_CONFIG.format(report=report_name),
            )
        else:
            stream_error_mapping[error_key] = base_error_resolution
    return stream_error_mapping
