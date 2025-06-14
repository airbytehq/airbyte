#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import copy
import json
import logging

import pytest

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .conftest import get_source


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


@pytest.mark.parametrize(
    "response, status_code, check_passed",
    [
        pytest.param(
            {"tags": [{"count": 10, "name": "Testing"}], "links": {"next": None}, "meta": {"has_more": False}},
            200,
            True,
            id="test_check_successful",
        ),
        pytest.param({}, 403, False, id="test_403_error_fails_check"),
    ],
)
def test_check(response, status_code, check_passed):
    config = copy.deepcopy(TEST_CONFIG)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest("https://sandbox.zendesk.com/api/v2/tags?page%5Bsize%5D=100"),
            HttpResponse(body=json.dumps(response), status_code=status_code),
        )
        ok, _ = get_source(config=config, state=None).check_connection(logger=logging.Logger(name="airbyte"), config=config)
        assert check_passed == ok


@pytest.mark.parametrize(
    "ticket_forms_response, status_code, expected_n_streams, expected_warnings, reason",
    [
        pytest.param('{"ticket_forms": [{"id": 1, "updated_at": "2021-07-08T00:05:45Z"}]}', 200, 41, [], None, id="forms_accessible"),
        # todo: Filtering inaccessible streams based on an API request is not supported in the low-code CDK
        #  at this moment, once this is supported, these tests can be added back
        # pytest.param(
        #     '{"error": "Not sufficient permissions"}',
        #     403,
        #     38,
        #     [
        #         "An exception occurred while trying to access TicketForms stream: Forbidden. You don't have permission to access this resource.. Skipping this stream."
        #     ],
        #     None,
        #     id="forms_inaccessible",
        # ),
        # pytest.param(
        #     "",
        #     404,
        #     38,
        #     [
        #         "An exception occurred while trying to access TicketForms stream: Not found. The requested resource was not found on the server.. Skipping this stream."
        #     ],
        #     "Not Found",
        #     id="forms_not_exists",
        # ),
    ],
)
def test_full_access_streams(caplog, requests_mock, ticket_forms_response, status_code, expected_n_streams, expected_warnings, reason):
    requests_mock.get("/api/v2/ticket_forms", status_code=status_code, text=ticket_forms_response, reason=reason)
    result = get_source(config=TEST_CONFIG, state=None).streams(config=TEST_CONFIG)
    assert len(result) == expected_n_streams
    logged_warnings = (record for record in caplog.records if record.levelname == "WARNING")
    for msg in expected_warnings:
        assert msg in next(logged_warnings).message
