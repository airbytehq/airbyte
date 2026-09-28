# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import base_config, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
_TOKEN_REQUEST_BODY = "grant_type=refresh_token&refresh_token=test-refresh-token"
_ADS_URL = "https://ads-api.reddit.com/api/v3/ad_accounts/a2_abc123/ads"


def _mock_token(http_mocker: HttpMocker, response: HttpResponse | None = None) -> HttpRequest:
    request = HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY)
    http_mocker.post(
        request,
        response or HttpResponse(body='{"access_token":"test-access-token","expires_in":3600}', status_code=200),
    )
    return request


def _read_ads(response: HttpResponse, token_response: HttpResponse | None = None):
    config = base_config()
    catalog = CatalogBuilder().with_stream("ad", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        token_request = _mock_token(http_mocker, token_response)
        ads_request = HttpRequest(_ADS_URL)
        http_mocker.get(ads_request, response)
        output = read(get_source(config, catalog), config, catalog)
    return output, http_mocker, token_request, ads_request


def _first_error(output):
    assert output.errors, "expected an error trace"
    return output.errors[0].trace.error


@pytest.mark.parametrize(
    "status_code,body,expected_failure_type,expected_message",
    [
        (
            403,
            '{"success":false,"error":{"reason":"UNAUTHORIZED","explanation":"Insufficient authentication scopes"}}',
            FailureType.config_error,
            "Reddit denied access to ad account 'a2_abc123' (HTTP 403: insufficient authentication scopes). "
            "Re-authorize the refresh token with the adsread scope, using a Reddit user who has access to this ad account.",
        ),
        (
            404,
            '{"error":{"code":404,"message":"The specified resource was not found"}}',
            FailureType.config_error,
            "Reddit could not find ad account 'a2_abc123' (HTTP 404). Check the Ad Account ID in the source settings; "
            "it is shown in Reddit Ads Manager (for example a2_abc123).",
        ),
        (
            400,
            '{"error":{"code":400,"message":"invalid ad_account identifier"}}',
            FailureType.config_error,
            "Reddit rejected the ad account ID 'a2_abc123': invalid ad_account identifier. Check the Ad Account ID "
            "in the source settings; it is shown in Reddit Ads Manager (for example a2_abc123).",
        ),
        (
            400,
            '{"success":false,"error":{"reason":"BAD_REQUEST","explanation":"Unknown Ad Account"}}',
            FailureType.config_error,
            "Reddit rejected the ad account ID 'a2_abc123': Unknown Ad Account. Check the Ad Account ID in the source "
            "settings; it is shown in Reddit Ads Manager (for example a2_abc123).",
        ),
        (
            400,
            '{"error":{"code":400,"message":"invalid field: campaign_name"}}',
            FailureType.system_error,
            "Reddit rejected the request as invalid (HTTP 400): invalid field: campaign_name.",
        ),
        (
            400,
            "[1,2]",
            FailureType.system_error,
            "Reddit rejected the request as invalid (HTTP 400): no error message returned.",
        ),
    ],
)
def test_http_errors_are_classified(
    status_code: int,
    body: str,
    expected_failure_type: FailureType,
    expected_message: str,
) -> None:
    output, http_mocker, token_request, ads_request = _read_ads(HttpResponse(body=body, status_code=status_code))
    error = _first_error(output)

    assert error.failure_type == expected_failure_type
    assert error.message == expected_message
    http_mocker.assert_number_of_calls(token_request, 1)
    http_mocker.assert_number_of_calls(ads_request, 1)


def test_normal_page_with_ad_account_id_fields_syncs() -> None:
    response = HttpResponse(
        body=json.dumps(
            {
                "data": [
                    {
                        "id": "ad-1",
                        "modified_at": "2026-09-27T00:00:00Z",
                        "ad_account_id": "a2_abc123",
                    }
                ]
            }
        ),
        status_code=200,
    )
    output, http_mocker, _, ads_request = _read_ads(response)

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["ad-1"]
    http_mocker.assert_number_of_calls(ads_request, 1)


def test_invalid_grant_from_token_endpoint_is_config_error() -> None:
    token_response = HttpResponse(body='{"error":"invalid_grant"}', status_code=400)
    output, http_mocker, token_request, ads_request = _read_ads(HttpResponse(body='{"data":[]}', status_code=200), token_response)
    error = _first_error(output)

    assert error.failure_type == FailureType.config_error
    assert "Refresh token was rejected by the OAuth provider" in error.message
    http_mocker.assert_number_of_calls(token_request, 1)
    http_mocker.assert_number_of_calls(ads_request, 0)


def test_numeric_401_token_error_does_not_match_invalid_grant_handler() -> None:
    token_response = HttpResponse(body='{"message":"Unauthorized","error":401}', status_code=401)
    output, _, _, _ = _read_ads(HttpResponse(body='{"data":[]}', status_code=200), token_response)

    error = _first_error(output)
    assert error.failure_type == FailureType.system_error
    assert "HTTPError" in error.message
    assert "401" in error.internal_message
