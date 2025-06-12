#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Type, Union

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction


PINTEREST_AD_ACCOUNT_DOCS_URL = "https://developers.pinterest.com/docs/api/v5/ad_accounts-get"
ERROR_MESSAGE = "Invalid Ad Account ID: {account_id}. Access denied. Check your permissions or visit {docs_url} for guidance."


def get_pinterest_ad_account_error_mapping(account_id: str) -> Mapping[Union[int, str, Type[Exception]], ErrorResolution]:
    """
    Maps API response errors to messages for Pinterest Ad Account validation.
    """
    return DEFAULT_ERROR_MAPPING | {
        403: ErrorResolution(
            response_action=ResponseAction.FAIL,
            failure_type=FailureType.config_error,
            error_message=ERROR_MESSAGE.format(account_id=account_id, docs_url=PINTEREST_AD_ACCOUNT_DOCS_URL),
        ),
        400: ErrorResolution(
            response_action=ResponseAction.FAIL,
            failure_type=FailureType.config_error,
            error_message=ERROR_MESSAGE.format(account_id=account_id, docs_url=PINTEREST_AD_ACCOUNT_DOCS_URL),
        ),
    }
