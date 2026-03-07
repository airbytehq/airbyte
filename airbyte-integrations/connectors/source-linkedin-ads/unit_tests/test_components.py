#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

import pytest
from requests import Response
from requests.exceptions import InvalidURL
from requests.models import PreparedRequest

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction


logger = logging.getLogger("airbyte")


@pytest.fixture
def mock_response():
    response = MagicMock(spec=Response)
    response.json.return_value = {
        "elements": [
            {"lastModified": "2024-09-01T00:00:00Z", "created": "2024-08-01T00:00:00Z", "data": "value1"},
            {"lastModified": "2024-09-02T00:00:00Z", "created": "2024-08-02T00:00:00Z", "data": "value2"},
        ]
    }
    return response


@pytest.fixture
def mock_analytics_cursor_params():
    return {
        "start_datetime": MagicMock(),
        "cursor_field": MagicMock(),
        "datetime_format": "%s",
        "config": MagicMock(),
        "parameters": MagicMock(),
    }


@pytest.fixture
def mock_retriever_params():
    return {"requester": MagicMock(), "record_selector": MagicMock(), "config": MagicMock(), "parameters": MagicMock()}


def test_safe_http_client_create_prepared_request(components_module):
    SafeHttpClient = components_module.SafeHttpClient

    client = SafeHttpClient(name="test_client", logger=logger)

    http_method = "GET"
    url = "http://example.com"
    params = {"key1": "value1", "key2": "value2"}

    prepared_request = client._create_prepared_request(
        http_method=http_method,
        url=url,
        params=params,
    )

    assert isinstance(prepared_request, PreparedRequest)
    assert "key1=value1&key2=value2" in prepared_request.url


def test_safe_encode_http_requester_post_init(components_module):
    SafeHttpClient = components_module.SafeHttpClient
    SafeEncodeHttpRequester = components_module.SafeEncodeHttpRequester

    parameters = {"param1": "value1"}
    requester = SafeEncodeHttpRequester(
        name="test_requester",
        url_base="http://example.com",
        path="test/path",
        http_method="GET",
        parameters=parameters,
        config={},
    )

    assert requester._http_client is not None
    assert isinstance(requester._http_client, SafeHttpClient)


def test_linkedin_ads_record_extractor_extract_records(components_module, mock_response):
    LinkedInAdsRecordExtractor = components_module.LinkedInAdsRecordExtractor

    expected_records = [
        {"lastModified": "2024-09-01T00:00:00+00:00", "created": "2024-08-01T00:00:00+00:00", "data": "value1"},
        {"lastModified": "2024-09-02T00:00:00+00:00", "created": "2024-08-02T00:00:00+00:00", "data": "value2"},
    ]

    extractor = LinkedInAdsRecordExtractor()
    records = list(extractor.extract_records(response=mock_response))

    assert len(records) == 2
    for i, record in enumerate(records):
        assert record["lastModified"] == expected_records[i]["lastModified"]
        assert record["created"] == expected_records[i]["created"]


def test_date_str_from_date_range(components_module):
    transform_date_range = components_module.transform_date_range

    expected_start_date = "2021-08-13"
    expected_end_date = "2021-08-30"

    record = {"dateRange": {"start": {"month": 8, "day": 13, "year": 2021}, "end": {"month": 8, "day": 30, "year": 2021}}}
    transformed_record = transform_date_range(record)

    assert transformed_record["start_date"] == expected_start_date
    assert transformed_record["end_date"] == expected_end_date


def test_linkedin_ads_error_handler_invalid_url(components_module):
    """
    Test that LinkedInAdsErrorHandler handles InvalidURL exceptions with RETRY action.

    This tests the custom error handling behavior added by LinkedInAdsErrorHandler
    which extends DefaultErrorHandler to handle DNS resolution issues gracefully.
    """
    LinkedInAdsErrorHandler = components_module.LinkedInAdsErrorHandler

    error_handler = LinkedInAdsErrorHandler(parameters={}, config={})
    invalid_url_exception = InvalidURL("Invalid URL 'http://invalid': No host supplied")

    error_resolution = error_handler.interpret_response(invalid_url_exception)

    assert error_resolution.response_action == ResponseAction.RETRY
    assert error_resolution.failure_type == FailureType.transient_error
    assert "temporary DNS resolution issue" in error_resolution.error_message


def test_linkedin_ads_error_handler_http_response(components_module):
    """
    Test that LinkedInAdsErrorHandler delegates HTTP responses to DefaultErrorHandler.

    For regular HTTP responses (not InvalidURL exceptions), the handler should
    delegate to the parent DefaultErrorHandler behavior.
    """
    LinkedInAdsErrorHandler = components_module.LinkedInAdsErrorHandler

    error_handler = LinkedInAdsErrorHandler(parameters={}, config={})
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.ok = True

    error_resolution = error_handler.interpret_response(mock_response)

    # For a successful response, DefaultErrorHandler returns SUCCESS action
    assert error_resolution.response_action == ResponseAction.SUCCESS
