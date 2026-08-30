# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for Apple Search Ads error classification."""

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


def _read_stream(stream_name, requests_mock, *, expecting_exception=False):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(_CONFIG),
        config=_CONFIG,
        catalog=catalog,
        expecting_exception=expecting_exception,
    )


def _register_token(requests_mock, *, status_code=200, response_list=None):
    if response_list is not None:
        requests_mock.post(_TOKEN_URL, response_list=response_list)
    else:
        requests_mock.post(
            _TOKEN_URL,
            status_code=status_code,
            json={"access_token": "test-access-token", "token_type": "bearer", "expires_in": 3600},
        )


def test_oauth_400_invalid_client_is_configuration_error(requests_mock):
    requests_mock.post(
        _TOKEN_URL,
        status_code=400,
        json={"error": "invalid_client", "error_description": "The client authentication failed."},
    )

    output = _read_stream("campaigns", requests_mock, expecting_exception=True)

    error = output.errors[-1].trace.error
    assert error.failure_type == FailureType.config_error
    assert "HTTPError" not in error.message


def test_stream_http_error_is_configuration_error(requests_mock, caplog):
    _register_token(requests_mock)
    requests_mock.get(
        _CAMPAIGNS_URL,
        status_code=400,
        json={"error": "invalid_request"},
    )

    output = _read_stream("campaigns", requests_mock, expecting_exception=True)

    error = output.errors[-1].trace.error
    assert error.failure_type == FailureType.config_error
    assert "Apple Ads rejected the request as invalid (HTTP 400)." in caplog.text


def test_stream_http_403_is_configuration_error(requests_mock, caplog):
    _register_token(requests_mock)
    requests_mock.get(
        _CAMPAIGNS_URL,
        status_code=403,
        json={"error": "forbidden"},
    )

    output = _read_stream("campaigns", requests_mock, expecting_exception=True)

    error = output.errors[-1].trace.error
    assert error.failure_type == FailureType.config_error
    assert "Apple Ads denied access to the requested resource (HTTP 403)." in caplog.text


def test_stream_http_404_is_configuration_error(requests_mock, caplog):
    _register_token(requests_mock)
    requests_mock.get(
        _CAMPAIGNS_URL,
        status_code=404,
        json={"error": "not_found"},
    )

    output = _read_stream("campaigns", requests_mock, expecting_exception=True)

    error = output.errors[-1].trace.error
    assert error.failure_type == FailureType.config_error
    assert "Apple Ads could not find the requested resource (HTTP 404)." in caplog.text


def test_keywords_report_daily_ignores_missing_keyword_campaign(requests_mock):
    _register_token(requests_mock)
    requests_mock.get(_CAMPAIGNS_URL, json={"data": [{"id": "campaign-1"}]})
    requests_mock.post(
        f"{_API_URL}/reports/campaigns/campaign-1/keywords",
        status_code=400,
        json={"error": {"errors": [{"message": "CAMPAIGN DOES NOT CONTAIN KEYWORD"}]}},
    )

    output = _read_stream("keywords_report_daily", requests_mock)

    assert output.errors == []
    assert output.records == []


def test_401_refreshes_token_and_retries(requests_mock):
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
            {"status_code": 200, "json": {"data": [{"id": "campaign-1"}]}},
        ],
    )

    output = _read_stream("campaigns", requests_mock)

    assert len(output.records) == 1
    assert requests_mock.call_count == 4
    assert requests_mock.request_history[0].url == _TOKEN_URL
    assert requests_mock.request_history[1].url.startswith(_CAMPAIGNS_URL)
    assert requests_mock.request_history[2].url == _TOKEN_URL
    assert requests_mock.request_history[3].url.startswith(_CAMPAIGNS_URL)
