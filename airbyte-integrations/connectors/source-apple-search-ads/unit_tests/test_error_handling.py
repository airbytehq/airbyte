# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for Apple Search Ads error classification."""

from unittest.mock import patch

import pytest
from _helpers import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "org_id": 123456789,
    "start_date": "2026-08-30",
    "end_date": "2026-08-30",
    "lookback_window": 30,
    "backoff_factor": 5,
    "timezone": "UTC",
    "token_refresh_endpoint": "https://appleid.apple.com/auth/oauth2/token?grant_type=client_credentials&scope=searchadsorg",
    "num_workers": 1,
}
_TOKEN_URL = _CONFIG["token_refresh_endpoint"]
_API_URL = "https://api.searchads.apple.com/api/v5"
_CAMPAIGNS_URL = f"{_API_URL}/campaigns"


def _read_stream(stream_name, *, sync_mode=SyncMode.full_refresh, expecting_exception=False):
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(
        get_source(_CONFIG, catalog=catalog),
        config=_CONFIG,
        catalog=catalog,
        expecting_exception=expecting_exception,
    )


def _register_token(requests_mock, *, response_list=None):
    if response_list is not None:
        requests_mock.post(_TOKEN_URL, response_list=response_list)
        return
    requests_mock.post(
        _TOKEN_URL,
        status_code=200,
        json={"access_token": "test-access-token", "token_type": "bearer", "expires_in": 3600},
    )


def test_oauth_400_invalid_client_is_configuration_error(requests_mock):
    requests_mock.post(
        _TOKEN_URL,
        status_code=400,
        json={"error": "invalid_client", "error_description": "The client authentication failed."},
    )

    output = _read_stream("campaigns", expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "HTTPError" not in error.message
    assert "invalid_client" in error.message


@pytest.mark.parametrize(
    "status_code, expected_message, failure_type",
    [
        (400, "Apple Ads rejected the request as invalid (400)", FailureType.system_error),
        (403, "Apple Ads denied access (403) for org 123456789", FailureType.config_error),
        (404, "Apple Ads returned 404 for https://api.searchads.apple.com/api/v5/campaigns", FailureType.system_error),
    ],
)
def test_api_errors_include_apple_message(requests_mock, status_code, expected_message, failure_type):
    _register_token(requests_mock)
    requests_mock.get(
        _CAMPAIGNS_URL,
        status_code=status_code,
        json={"error": {"errors": [{"messageCode": "X", "message": "Apple detail here", "field": ""}]}},
    )

    output = _read_stream("campaigns", expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type == failure_type
    assert expected_message in error.message
    assert "Apple said: Apple detail here" in error.message


def test_child_404_is_a_system_error(requests_mock):
    _register_token(requests_mock)
    requests_mock.get(_CAMPAIGNS_URL, json={"data": [{"id": 1}]})
    requests_mock.get(
        f"{_CAMPAIGNS_URL}/1/adgroups",
        status_code=404,
        json={"data": None, "error": {"errors": [{"messageCode": "NOT_FOUND", "message": "Campaign not found", "field": ""}]}},
    )

    output = _read_stream("adgroups", expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.system_error
    assert "deleted while the sync was running" in error.message
    assert "/campaigns/1/adgroups" in error.message
    assert "Org Id" not in error.message


def test_report_400_points_at_the_report_date_window(requests_mock):
    _register_token(requests_mock)
    requests_mock.post(
        f"{_API_URL}/reports/campaigns",
        status_code=400,
        json={
            "data": None,
            "error": {"errors": [{"messageCode": "INVALID_DATE_RANGE", "message": "Apple date detail", "field": "startTime"}]},
        },
    )

    output = _read_stream("campaigns_report_daily", sync_mode=SyncMode.incremental, expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "last 90 days" in error.message
    assert "Apple said: Apple date detail" in error.message


@pytest.mark.parametrize(
    "response_body",
    [
        {"error": "forbidden"},
        {"error": {"errors": []}},
    ],
)
def test_forbidden_errors_without_apple_details_use_safe_fallback(requests_mock, response_body):
    _register_token(requests_mock)
    requests_mock.get(_CAMPAIGNS_URL, status_code=403, json=response_body)

    output = _read_stream("campaigns", expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "no error details returned" in error.message


def test_401_refreshes_token_and_retries(requests_mock):
    _register_token(
        requests_mock,
        response_list=[
            {"json": {"access_token": "initial-token", "token_type": "bearer", "expires_in": 3600}},
            {"json": {"access_token": "refreshed-token", "token_type": "bearer", "expires_in": 3600}},
        ],
    )
    sent_tokens = []

    def campaigns(request, context):
        # The CDK re-signs the same PreparedRequest on retry, so request_history would only show the last token.
        sent_tokens.append(request.headers["Authorization"])
        context.status_code = 401 if len(sent_tokens) == 1 else 200
        return {"error": "unauthorized"} if len(sent_tokens) == 1 else {"data": [{"id": "campaign-1"}]}

    requests_mock.get(_CAMPAIGNS_URL, json=campaigns)

    output = _read_stream("campaigns")

    assert len(output.records) == 1
    assert sent_tokens == ["Bearer initial-token", "Bearer refreshed-token"]
    assert requests_mock.call_count == 4
    assert requests_mock.request_history[0].url == _TOKEN_URL
    assert requests_mock.request_history[1].url.startswith(_CAMPAIGNS_URL)
    assert requests_mock.request_history[2].url == _TOKEN_URL
    assert requests_mock.request_history[3].url.startswith(_CAMPAIGNS_URL)


def test_persistent_401_is_a_configuration_error(requests_mock):
    _register_token(
        requests_mock,
        response_list=[
            {"json": {"access_token": "initial-token", "token_type": "bearer", "expires_in": 3600}},
            {"json": {"access_token": "refreshed-token", "token_type": "bearer", "expires_in": 3600}},
        ],
    )
    requests_mock.get(
        _CAMPAIGNS_URL,
        response_list=[
            {"status_code": 401, "json": {"error": "unauthorized"}},
            {"status_code": 401, "json": {"error": "unauthorized"}},
        ],
    )

    with patch("time.sleep"):
        output = _read_stream("campaigns", expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "Apple Ads rejected the credentials (401)" in error.internal_message


def test_429_retries_then_succeeds(requests_mock):
    _register_token(requests_mock)
    requests_mock.get(
        _CAMPAIGNS_URL,
        response_list=[
            {"status_code": 429, "json": {"error": "rate_limited"}},
            {"status_code": 200, "json": {"data": [{"id": "campaign-1"}]}},
        ],
    )

    with patch("time.sleep"):
        output = _read_stream("campaigns")

    assert len(output.records) == 1
    assert requests_mock.call_count == 3


def test_keywords_report_daily_ignores_missing_keyword_campaign(requests_mock):
    _register_token(requests_mock)
    requests_mock.get(_CAMPAIGNS_URL, json={"data": [{"id": "campaign-1"}]})
    requests_mock.post(
        f"{_API_URL}/reports/campaigns/campaign-1/keywords",
        status_code=400,
        json={"error": {"errors": [{"message": "CAMPAIGN DOES NOT CONTAIN KEYWORD"}]}},
    )

    output = _read_stream("keywords_report_daily", sync_mode=SyncMode.incremental)

    assert output.errors == []
    assert output.records == []


def test_keywords_report_daily_emits_successful_report_records(requests_mock):
    _register_token(requests_mock)
    requests_mock.get(_CAMPAIGNS_URL, json={"data": [{"id": "campaign-1"}]})
    requests_mock.post(
        f"{_API_URL}/reports/campaigns/campaign-1/keywords",
        json={
            "data": {
                "reportingDataResponse": {
                    "row": [
                        {
                            "metadata": {
                                "campaignId": "campaign-1",
                                "keywordId": "keyword-1",
                                "countryOrRegion": "US",
                            },
                            "total": {"impressions": 5},
                        }
                    ]
                }
            }
        },
    )

    output = _read_stream("keywords_report_daily", sync_mode=SyncMode.incremental)

    assert output.errors == []
    assert len(output.records) == 1
    assert output.records[0].record.data["total"] == {"impressions": 5}
