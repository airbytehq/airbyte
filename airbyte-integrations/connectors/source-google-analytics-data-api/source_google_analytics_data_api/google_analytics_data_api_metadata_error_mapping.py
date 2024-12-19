#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from typing import Mapping, Type, Union

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction

PROPERTY_ID_DOCS_URL = "https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id"
MESSAGE = "Incorrect Property ID: {property_id}. Access was denied to the property ID entered. Check your access to the Property ID or use Google Analytics {property_id_docs_url} to find your Property ID."


def get_google_analytics_data_api_metadata_error_mapping(property_id) -> Mapping[Union[int, str, Type[Exception]], ErrorResolution]:
    """
    Adding friendly messages to bad request and forbidden responses that includes the property id and the documentation guidance.
    """
    return DEFAULT_ERROR_MAPPING | {
        403: ErrorResolution(
            response_action=ResponseAction.FAIL,
            failure_type=FailureType.config_error,
            error_message=MESSAGE.format(property_id=property_id, property_id_docs_url=PROPERTY_ID_DOCS_URL),
        ),
        400: ErrorResolution(
            response_action=ResponseAction.FAIL,
            failure_type=FailureType.config_error,
            error_message=MESSAGE.format(property_id=property_id, property_id_docs_url=PROPERTY_ID_DOCS_URL),
        ),
    }
