#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Mapping, Union
from unittest.mock import MagicMock

import pytest
from requests import Response
from requests.exceptions import InvalidURL
from requests.models import PreparedRequest

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction


logger = logging.getLogger("airbyte")
_DATA_VOLUME_RATE_LIMIT_MESSAGE = (
    "The data request limit has been exceeded. More than 45 million metric values were requested in a 5-minute window."
)


def _response(status_code: int, body: Union[Mapping[str, str], bytes]) -> Response:
    response = Response()
    response.status_code = status_code
    response._content = body if isinstance(body, bytes) else json.dumps(body).encode()
    return response


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


@pytest.mark.parametrize(
    "body,expected_message",
    [
        pytest.param(
            {"message": _DATA_VOLUME_RATE_LIMIT_MESSAGE},
            "LinkedIn Ads metric-value rate limit is exceeded.",
            id="data_volume_throttle",
        ),
        pytest.param(
            {"message": "Rate limit exceeded for LinkedIn API."},
            "HTTP Status Code: 429. Error: Too many requests.",
            id="count_throttle",
        ),
        pytest.param({}, "HTTP Status Code: 429. Error: Too many requests.", id="missing_message"),
        pytest.param(b"not-json", "HTTP Status Code: 429. Error: Too many requests.", id="malformed_body"),
    ],
)
def test_linkedin_ads_error_handler_rate_limit_response(components_module, body, expected_message):
    error_handler = components_module.LinkedInAdsErrorHandler(parameters={}, config={})

    error_resolution = error_handler.interpret_response(_response(429, body))

    assert error_resolution.response_action == ResponseAction.RATE_LIMITED
    assert error_resolution.failure_type == FailureType.transient_error
    assert error_resolution.error_message == expected_message


def test_linkedin_ads_error_handler_uri_too_long(components_module):
    error_handler = components_module.LinkedInAdsErrorHandler(parameters={}, config={})

    error_resolution = error_handler.interpret_response(_response(414, {}))

    assert error_resolution.response_action == ResponseAction.FAIL
    assert error_resolution.failure_type == FailureType.system_error
    assert error_resolution.error_message == "LinkedIn Ads request URL exceeds the API length limit."


@pytest.mark.parametrize(
    "response_or_exception,expected_backoff",
    [
        pytest.param(
            _response(429, {"message": _DATA_VOLUME_RATE_LIMIT_MESSAGE}),
            330.0,
            id="data_volume_throttle",
        ),
        pytest.param(_response(429, {"message": "Rate limit exceeded."}), None, id="count_throttle"),
        pytest.param(_response(429, b"not-json"), None, id="malformed_body"),
        pytest.param(InvalidURL("Invalid URL"), None, id="request_exception"),
    ],
)
def test_linkedin_ads_data_volume_backoff_strategy(components_module, response_or_exception, expected_backoff):
    strategy = components_module.LinkedInAdsDataVolumeBackoffStrategy()

    assert strategy.backoff_time(response_or_exception=response_or_exception, attempt_count=1) == expected_backoff


@pytest.mark.parametrize(
    "stream_state,expected_should_migrate,expected_state",
    [
        pytest.param(
            {
                "states": [
                    {"partition": {"campaign_id": "1"}, "cursor": {"end_date": "2024-06-05"}},
                    {"partition": {"campaign_id": "2"}, "cursor": {"end_date": "2024-06-01"}},
                ],
                "state": {"end_date": "2024-06-05"},
                "parent_state": {"campaigns": {"lastModified": "2024-06-06T00:00:00Z"}},
            },
            True,
            {
                "end_date": "2024-06-01",
                "parent_state": {"campaigns": {"lastModified": "2024-06-06T00:00:00Z"}},
            },
            id="per_partition_state_uses_earliest_cursor",
        ),
        pytest.param(
            {"end_date": "2024-06-01"},
            False,
            {"end_date": "2024-06-01"},
            id="global_state_is_unchanged",
        ),
        pytest.param(
            {
                "use_global_cursor": True,
                "state": {"end_date": "2024-06-01"},
                "parent_state": {"campaigns": {"lastModified": "2024-06-06T00:00:00Z"}},
            },
            False,
            {
                "use_global_cursor": True,
                "state": {"end_date": "2024-06-01"},
                "parent_state": {"campaigns": {"lastModified": "2024-06-06T00:00:00Z"}},
            },
            id="current_global_state_does_not_migrate_again",
        ),
        pytest.param(
            {
                "states": [
                    {
                        "partition": {"campaign_id": "urn%3Ali%3AsponsoredCampaign%3A1,urn%3Ali%3AsponsoredCampaign%3A2"},
                        "cursor": {"end_date": "2024-06-03"},
                    },
                    {
                        "partition": {"campaign_id": "urn%3Ali%3AsponsoredCampaign%3A3"},
                        "cursor": {"end_date": "2024-06-02"},
                    },
                ],
                "state": {"end_date": "2024-06-03"},
            },
            True,
            {"end_date": "2024-06-02"},
            id="batched_state_uses_earliest_cursor",
        ),
    ],
)
def test_linkedin_ads_batched_analytics_state_migration(
    components_module,
    stream_state,
    expected_should_migrate,
    expected_state,
):
    migration = components_module.LinkedInAdsBatchedAnalyticsStateMigration(config={}, declarative_stream=MagicMock())

    assert migration.should_migrate(stream_state) is expected_should_migrate
    migrated_state = migration.migrate(stream_state) if expected_should_migrate else stream_state
    assert migrated_state == expected_state
    assert not migration.should_migrate(migrated_state)
