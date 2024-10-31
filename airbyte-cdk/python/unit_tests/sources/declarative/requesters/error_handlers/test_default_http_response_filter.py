#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_http_response_filter import DefaultHttpResponseFilter
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from requests import RequestException, Response


@pytest.mark.parametrize(
    "http_code, expected_error_resolution",
    [
        pytest.param(403, DEFAULT_ERROR_MAPPING[403], id="403 mapping"),
        pytest.param(404, DEFAULT_ERROR_MAPPING[404], id="404 mapping"),
        pytest.param(408, DEFAULT_ERROR_MAPPING[408], id="408 mapping"),
    ],
)
def test_matches_mapped_http_status_code(http_code, expected_error_resolution):

    response = MagicMock(spec=Response)
    response.status_code = http_code

    response_filter = DefaultHttpResponseFilter(
        config={},
        parameters={},
    )

    actual_error_resolution = response_filter.matches(response)
    assert actual_error_resolution == expected_error_resolution


def test_matches_mapped_exception():

    exc = MagicMock(spec=RequestException)

    response_filter = DefaultHttpResponseFilter(
        config={},
        parameters={},
    )

    actual_error_resolution = response_filter.matches(exc)
    assert actual_error_resolution == DEFAULT_ERROR_MAPPING[RequestException]


def test_unmapped_http_status_code_returns_default_error_resolution():

    response = MagicMock(spec=Response)
    response.status_code = 508

    response_filter = DefaultHttpResponseFilter(
        config={},
        parameters={},
    )

    actual_error_resolution = response_filter.matches(response)
    assert actual_error_resolution
    assert actual_error_resolution.failure_type == FailureType.system_error
    assert actual_error_resolution.response_action == ResponseAction.RETRY
