#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from copy import deepcopy
from typing import Iterable
from unittest.mock import Mock

import pytest
import requests
from components import GoogleSheetsOAuthAuthenticator, ValidateGoogleSheetsConfig

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.utils import AirbyteTracedException
from unit_tests.conftest import _YAML_FILE_PATH
from unit_tests.integration.conftest import AUTH_BODY, AuthBuilder, GoogleSheetsBaseTest, oauth_credentials, service_account_credentials
from unit_tests.integration.conftest.request_builder import RequestBuilder


@pytest.fixture
def http_mocker() -> Iterable[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker


@pytest.mark.parametrize(
    "value",
    [
        "a_spreadsheet_id",
        " a_spreadsheet_id ",
        "https://docs.google.com/spreadsheets/d/a_spreadsheet_id",
        "https://docs.google.com/spreadsheets/d/a_spreadsheet_id/edit?usp=sharing#gid=0",
    ],
)
def test_check_normalizes_spreadsheet_link(value: str, http_mocker: HttpMocker) -> None:
    GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "check_succeeded_meta")
    GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "check_succeeded_range")
    output = GoogleSheetsBaseTest._check({"spreadsheet_id": value, "credentials": oauth_credentials}, expecting_exception=False)
    assert output.logs[-1].log.message == "Check succeeded"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        None,
        123,
        "not an id",
        "id?secret=do-not-echo",
        "https://example.com/spreadsheets/d/abc/edit",
        "https://docs.google.com.evil.test/spreadsheets/d/abc/edit",
        "https://user:password@docs.google.com/spreadsheets/d/abc/edit",
        "https://docs.google.com/document/d/abc/edit",
        "https://docs.google.com/spreadsheets/d/",
        "http://docs.google.com/spreadsheets/d/abc/edit",
        "https://[invalid/spreadsheets/d/abc/edit",
        "https://docs.google.com/spreadsheets/d/abc%2Fdef/edit",
    ],
)
def test_rejects_malformed_link_before_requests(value: str) -> None:
    with pytest.raises(AirbyteTracedException) as error:
        YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), config={"spreadsheet_id": value, "credentials": oauth_credentials})
    assert error.value.failure_type == FailureType.config_error
    assert "Enter a spreadsheet ID" in error.value.message
    assert "do-not-echo" not in error.value.message


@pytest.mark.parametrize("value", ["not-json", "{}", "[]", "null", '{"private_key": "secret"}'])
def test_invalid_service_account_json(value: str) -> None:
    config = {"spreadsheet_id": "a_spreadsheet_id", "credentials": {"auth_type": "Service", "service_account_info": value}}
    with pytest.raises(AirbyteTracedException) as error:
        YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), config=config)
    assert error.value.failure_type == FailureType.config_error
    assert "complete service-account JSON key" in error.value.message
    assert "secret" not in error.value.message


def test_valid_service_account_and_invalid_private_key() -> None:
    config = {"spreadsheet_id": "a_spreadsheet_id", "credentials": deepcopy(service_account_credentials)}
    ValidateGoogleSheetsConfig().transform(config)
    account = json.loads(config["credentials"]["service_account_info"])
    account["private_key"] = "secret-invalid-key"
    config["credentials"]["service_account_info"] = json.dumps(account)
    with pytest.raises(AirbyteTracedException) as error:
        ValidateGoogleSheetsConfig().transform(config)
    assert error.value.failure_type == FailureType.config_error
    assert "secret-invalid-key" not in error.value.message


@pytest.mark.parametrize(
    "status,body,hint",
    [
        (
            403,
            {"error": {"code": 403, "message": "Google Sheets API has not been used in project 123 before or it is disabled."}},
            "Enable the Google Sheets API",
        ),
        (
            403,
            {"error": {"code": 403, "message": "Google Drive API has not been used in project 123 before or it is disabled."}},
            "Enable the Google Sheets API",
        ),
        (
            403,
            {"error": {"code": 403, "message": "Permission denied", "details": [{"reason": "SERVICE_DISABLED"}]}},
            "Enable the Google Sheets API",
        ),
        (
            403,
            {"error": {"code": 403, "message": "Access Not Configured", "errors": [{"reason": "accessNotConfigured"}]}},
            "Enable the Google Sheets API",
        ),
        (403, {"error": {"code": 403, "message": "The caller does not have permission"}}, "Share the spreadsheet"),
        (404, {"error": {"code": 404, "message": "Requested entity was not found"}}, "not found or is inaccessible"),
        (401, {"error": {"code": 401, "message": "Invalid Credentials"}}, "Re-authenticate"),
        (403, {}, "Share the spreadsheet"),
        (404, {}, "not found or is inaccessible"),
    ],
)
@pytest.mark.parametrize("stage", ["metadata", "headers"])
def test_check_api_failures(status: int, body: dict, hint: str, stage: str, http_mocker: HttpMocker) -> None:
    if stage == "headers":
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "check_succeeded_meta")
        request = RequestBuilder().with_spreadsheet_id("a_spreadsheet_id").with_include_grid_data(True).with_ranges("a_stream_name!1:1")
    else:
        GoogleSheetsBaseTest.authorize(http_mocker)
        request = RequestBuilder().with_spreadsheet_id("a_spreadsheet_id").with_include_grid_data(False)
    http_mocker.get(
        request.with_alt("json").build(),
        HttpResponse(json.dumps(body), status),
    )
    output = GoogleSheetsBaseTest._check({"spreadsheet_id": "a_spreadsheet_id", "credentials": oauth_credentials})
    assert output.errors[-1].trace.error.failure_type == FailureType.config_error
    assert hint in output.errors[-1].trace.error.message


@pytest.mark.parametrize(
    "status,body",
    [
        (400, {"error": "invalid_grant", "error_description": "Token has been expired or revoked."}),
        (401, {"error": "invalid_client"}),
        (403, {}),
    ],
)
def test_check_token_failures(status: int, body: dict, http_mocker: HttpMocker) -> None:
    http_mocker.post(AuthBuilder.get_token_endpoint().with_body(AUTH_BODY).build(), HttpResponse(json.dumps(body), status))
    output = GoogleSheetsBaseTest._check({"spreadsheet_id": "a_spreadsheet_id", "credentials": oauth_credentials})
    assert output.errors[-1].trace.error.failure_type == FailureType.config_error
    assert "Re-authenticate" in output.errors[-1].trace.error.message


def test_oauth_preserves_unexpected_http_errors() -> None:
    authenticator = GoogleSheetsOAuthAuthenticator(
        config={}, parameters={}, client_id="client", client_secret="secret", refresh_token="token"
    )
    response = requests.Response()
    response.status_code = 404
    error = requests.HTTPError(response=response)
    authenticator._make_handled_request = Mock(side_effect=error)
    with pytest.raises(requests.HTTPError) as result:
        authenticator.refresh_access_token()
    assert result.value is error


def test_check_revoked_service_account_key(requests_mock) -> None:
    requests_mock.post("https://oauth2.googleapis.com/token", status_code=400, json={"error": "invalid_grant"})
    credentials = deepcopy(service_account_credentials)
    credentials["service_account_info"] = credentials["service_account_info"].decode()
    output = GoogleSheetsBaseTest._check({"spreadsheet_id": "a_spreadsheet_id", "credentials": credentials})
    assert output.errors[-1].trace.error.failure_type == FailureType.config_error
    assert "replace the service-account JSON key" in output.errors[-1].trace.error.message
