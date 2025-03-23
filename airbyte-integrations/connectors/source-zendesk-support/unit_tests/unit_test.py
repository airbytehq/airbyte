#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import copy
import json
import logging
from datetime import datetime

import pytest
from source_zendesk_support.source import BasicApiTokenAuthenticator, SourceZendeskSupport

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"

# raw config
TEST_CONFIG = {
    "subdomain": "sandbox",
    "start_date": "2021-06-01T00:00:00Z",
    "credentials": {"credentials": "api_token", "email": "integration-test@airbyte.io", "api_token": "api_token"},
}

TEST_CONFIG_WITHOUT_START_DATE = {
    "subdomain": "sandbox",
    "credentials": {"credentials": "api_token", "email": "integration-test@airbyte.io", "api_token": "api_token"},
}


# raw config oauth
TEST_CONFIG_OAUTH = {
    "subdomain": "sandbox",
    "start_date": "2021-06-01T00:00:00Z",
    "credentials": {"credentials": "oauth2.0", "access_token": "test_access_token"},
}


def test_token_authenticator():
    # we expect base64 from creds input
    expected = "dGVzdEBhaXJieXRlLmlvL3Rva2VuOmFwaV90b2tlbg=="
    result = BasicApiTokenAuthenticator("test@airbyte.io", "api_token")
    assert result._token == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        (TEST_CONFIG, "aW50ZWdyYXRpb24tdGVzdEBhaXJieXRlLmlvL3Rva2VuOmFwaV90b2tlbg=="),
        (TEST_CONFIG_OAUTH, "test_access_token"),
    ],
    ids=["api_token", "oauth"],
)
def test_get_authenticator(config, expected):
    # we expect base64 from creds input
    result = SourceZendeskSupport(config=config, catalog=None, state=None).get_authenticator(config=config)
    assert result._token == expected


@pytest.mark.parametrize(
    "response, start_date, check_passed",
    [({"active_features": {"organization_access_enabled": True}}, "2020-01-01T00:00:00Z", True), ({}, "2020-01-01T00:00:00Z", False)],
    ids=["check_successful", "invalid_start_date"],
)
def test_check(response, start_date, check_passed):
    config = copy.deepcopy(TEST_CONFIG)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest("https://sandbox.zendesk.com/api/v2/account/settings.json"),
            HttpResponse(json.dumps({"settings": response})),
        )
        ok, _ = SourceZendeskSupport(config=config, catalog=None, state=None).check_connection(logger=logging.Logger, config=config)
        assert check_passed == ok


@pytest.mark.parametrize(
    "ticket_forms_response, status_code, expected_n_streams, expected_warnings, reason",
    [
        ('{"ticket_forms": [{"id": 1, "updated_at": "2021-07-08T00:05:45Z"}]}', 200, 40, [], None),
        (
            '{"error": "Not sufficient permissions"}',
            403,
            37,
            [
                "An exception occurred while trying to access TicketForms stream: Forbidden. You don't have permission to access this resource.. Skipping this stream."
            ],
            None,
        ),
        (
            "",
            404,
            37,
            [
                "An exception occurred while trying to access TicketForms stream: Not found. The requested resource was not found on the server.. Skipping this stream."
            ],
            "Not Found",
        ),
    ],
    ids=["forms_accessible", "forms_inaccessible", "forms_not_exists"],
)
def test_full_access_streams(caplog, requests_mock, ticket_forms_response, status_code, expected_n_streams, expected_warnings, reason):
    requests_mock.get("/api/v2/ticket_forms", status_code=status_code, text=ticket_forms_response, reason=reason)
    result = SourceZendeskSupport(config=TEST_CONFIG, catalog=None, state=None).streams(config=TEST_CONFIG)
    assert len(result) == expected_n_streams
    logged_warnings = (record for record in caplog.records if record.levelname == "WARNING")
    for msg in expected_warnings:
        assert msg in next(logged_warnings).message
