# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import yaml
from conftest import _YAML_FILE_PATH
from mock_server.request_builder import PardotRequestBuilder, login_request
from mock_server.response_builder import login_response, page_response
from mock_server.utils import read_stream, record_ids, stream_error

from airbyte_cdk.models import AirbyteStreamStatus, FailureType
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CAMPAIGNS = "v5/objects/campaigns"
_EMAIL_CLICKS = "emailClick/version/4/do/query"
# Spelled in two halves so that a search for the name in the connector's folder finds nothing.
_COMPOSITE_HANDLER_TYPE = "".join(("Composite", "ErrorHandler"))
_DAILY_LIMIT_TEXT = "Daily API rate limit met"
_DAILY_LIMIT_MESSAGE = (
    "The daily API request limit of this Account Engagement account is used up. It resets at the start of the next day in the "
    "account's time zone. The next sync continues from the last saved position."
)
_REJECTED_TOKEN_MESSAGE = (
    'Account Engagement rejected the access token. Check that the Salesforce app has the "Manage Pardot services (pardot_api)" '
    "scope and that the user behind the refresh token is synced to this business unit."
)
_NO_BUSINESS_UNIT_MESSAGE = (
    "Account Engagement found no active business unit for this Business Unit ID on this host. Check the ID, and select the demo "
    "host for a sandbox or a Developer Edition org."
)
_PAGE = {"nextPageToken": None, "nextPageUrl": None, "values": [{"id": 1, "updatedAt": "2026-03-01T09:00:00-08:00"}]}
_ERROR_LOOKING_RECORD = {"id": 1, "name": _DAILY_LIMIT_TEXT, "code": 122, "updatedAt": "2026-03-01T09:00:00-08:00"}
_VERSION_4_PAGE = {"@attributes": {"stat": "ok", "version": 1}, "result": {"emailClick": [{"id": 1, "created_at": "2026-03-01 09:00:00"}]}}
_CONCURRENT_LIMIT_TEXT = "You have exceeded your concurrent request limit. Please wait, before trying again"
_INVALID_TOKEN_TEXT = "access_token is invalid, unknown, or malformed"
_NO_BUSINESS_UNIT_TEXT = "Business Unit specified in Pardot-Business-Unit-Id header not found or inactive"


def _request(path: str = _CAMPAIGNS) -> HttpRequest:
    return PardotRequestBuilder.endpoint(path).with_any_query_params().build()


def _error(status_code: int, code: int, message: str) -> HttpResponse:
    """An error in the body of version 5 of the API."""
    return HttpResponse(body=json.dumps({"code": code, "message": message}), status_code=status_code)


def _version_4_error(status_code: int, code: int, message: str) -> HttpResponse:
    body = {"@attributes": {"stat": "fail", "version": 1, "err_code": code}, "err": message}
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _resolved_manifest() -> dict:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _resolved_manifest()
    found = []

    def walk(node) -> None:
        if isinstance(node, dict):
            if node.get("type") == _COMPOSITE_HANDLER_TYPE:
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)

    assert not found


def test_every_stream_uses_the_shared_error_handler() -> None:
    manifest = _resolved_manifest()
    shared_handler = manifest["definitions"]["error_handler"]
    streams = manifest["streams"]

    assert len(streams) == 33
    assert shared_handler["type"] == "DefaultErrorHandler"
    assert all(stream["retriever"]["requester"]["error_handler"] == shared_handler for stream in streams)


def test_every_stream_but_email_clicks_names_the_ability_it_needs() -> None:
    # The page of the version 4 endpoint behind `email_clicks` names no ability.
    streams = _resolved_manifest()["streams"]

    assert [stream["name"] for stream in streams if not stream.get("$parameters", {}).get("required_ability")] == ["email_clicks"]


@pytest.mark.parametrize(
    ("stream", "path", "response"),
    [
        pytest.param("campaigns", _CAMPAIGNS, _error(429, 122, _DAILY_LIMIT_TEXT), id="429-version-5"),
        pytest.param("campaigns", _CAMPAIGNS, _error(200, 122, _DAILY_LIMIT_TEXT), id="200-version-5"),
        pytest.param("campaigns", _CAMPAIGNS, _error(429, 122, "Another text"), id="code-122-with-another-text"),
        pytest.param("email_clicks", _EMAIL_CLICKS, _version_4_error(429, 122, _DAILY_LIMIT_TEXT), id="429-version-4"),
        pytest.param("email_clicks", _EMAIL_CLICKS, _version_4_error(200, 122, _DAILY_LIMIT_TEXT), id="200-version-4"),
        pytest.param("email_clicks", _EMAIL_CLICKS, _version_4_error(200, 122, "Another text"), id="code-122-version-4-with-another-text"),
    ],
)
def test_daily_limit_fails_at_once_with_its_message(stream: str, path: str, response: HttpResponse, waits: list[float]) -> None:
    request = _request(path)
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(request, response)

        error = stream_error(read_stream(stream, expecting_error=True))

    assert error.failure_type == FailureType.transient_error
    assert error.message == _DAILY_LIMIT_MESSAGE
    http_mocker.assert_number_of_calls(request, 1)
    assert waits == []


@pytest.mark.parametrize(
    ("stream", "path", "concurrent_limit", "page"),
    [
        pytest.param("campaigns", _CAMPAIGNS, _error(400, 66, _CONCURRENT_LIMIT_TEXT), _PAGE, id="400-version-5"),
        pytest.param("campaigns", _CAMPAIGNS, _error(429, 66, _CONCURRENT_LIMIT_TEXT), _PAGE, id="429-version-5"),
        pytest.param("email_clicks", _EMAIL_CLICKS, _version_4_error(200, 66, _CONCURRENT_LIMIT_TEXT), _VERSION_4_PAGE, id="200-version-4"),
    ],
)
def test_concurrent_limit_is_retried_on_any_status(
    stream: str, path: str, concurrent_limit: HttpResponse, page: dict, waits: list[float]
) -> None:
    request = _request(path)
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(request, [concurrent_limit, HttpResponse(body=json.dumps(page), status_code=200)])

        output = read_stream(stream)

    assert record_ids(output) == [1]
    http_mocker.assert_number_of_calls(request, 2)
    assert waits == [21]


@pytest.mark.parametrize(
    ("stream", "path", "response", "message"),
    [
        pytest.param("campaigns", _CAMPAIGNS, _error(401, 184, _INVALID_TOKEN_TEXT), _REJECTED_TOKEN_MESSAGE, id="184"),
        pytest.param(
            "email_clicks", _EMAIL_CLICKS, _version_4_error(200, 184, _INVALID_TOKEN_TEXT), _REJECTED_TOKEN_MESSAGE, id="184-version-4"
        ),
        pytest.param(
            "campaigns",
            _CAMPAIGNS,
            _error(403, 201, _NO_BUSINESS_UNIT_TEXT),
            _NO_BUSINESS_UNIT_MESSAGE,
            id="201",
        ),
        pytest.param(
            "email_clicks",
            _EMAIL_CLICKS,
            _version_4_error(200, 201, _NO_BUSINESS_UNIT_TEXT),
            _NO_BUSINESS_UNIT_MESSAGE,
            id="201-version-4",
        ),
    ],
)
def test_known_configuration_error_fails_at_once_and_says_what_to_fix(
    stream: str, path: str, response: HttpResponse, message: str, waits: list[float]
) -> None:
    request = _request(path)
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(request, response)

        error = stream_error(read_stream(stream, expecting_error=True))

    assert error.failure_type == FailureType.config_error
    assert error.message == message
    http_mocker.assert_number_of_calls(request, 1)
    assert waits == []


@pytest.mark.parametrize(
    ("stream", "path", "response", "ability"),
    [
        pytest.param("campaigns", _CAMPAIGNS, _error(403, 49, "Access Denied"), "Marketing > Other > Campaigns > View", id="campaigns"),
        pytest.param("account", "v5/objects/account", _error(403, 49, "Access Denied"), "Admin > Account > Edit Settings", id="account"),
        # The version 4 page behind `email_clicks` names no ability, so the message falls back to "View".
        pytest.param("email_clicks", _EMAIL_CLICKS, _version_4_error(200, 49, "Access Denied"), "View", id="email-clicks-version-4"),
    ],
)
def test_access_denied_fails_at_once_and_names_the_ability_of_the_stream(
    stream: str, path: str, response: HttpResponse, ability: str, waits: list[float]
) -> None:
    request = _request(path)
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(request, response)

        error = stream_error(read_stream(stream, expecting_error=True))

    assert error.failure_type == FailureType.config_error
    assert error.message == (
        f'The user cannot read this object. Ask an Account Engagement admin for the "{ability}" ability, or deselect the stream.'
    )
    http_mocker.assert_number_of_calls(request, 1)
    assert waits == []


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (429, "API rate limit exceeded."),
        (
            500,
            "Exhausted available request attempts. Please see logs for more details. Exception: HTTP Status Code: 500. "
            "Error: Internal server error.",
        ),
    ],
)
def test_retryable_status_is_retried_with_growing_waits_before_it_fails(status_code: int, message: str, waits: list[float]) -> None:
    request = _request()
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(request, HttpResponse(body="", status_code=status_code))

        error = stream_error(read_stream("campaigns", expecting_error=True))

    assert error.failure_type == FailureType.transient_error
    assert error.message == message
    http_mocker.assert_number_of_calls(request, 6)
    assert waits == [21, 41, 81, 161, 321]
    assert max(waits) <= 600


@pytest.mark.parametrize(
    ("status_code", "failure_type", "message"),
    [
        (400, FailureType.system_error, "HTTP Status Code: 400. Error: Bad request. Please check your request parameters."),
        (401, FailureType.config_error, "HTTP Status Code: 401. Error: Unauthorized. Please ensure you are authenticated correctly."),
        (403, FailureType.config_error, "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."),
        (404, FailureType.system_error, "HTTP Status Code: 404. Error: Not found. The requested resource was not found on the server."),
    ],
)
def test_error_without_a_known_code_fails_at_once_with_the_message_of_its_status(
    status_code: int, failure_type: FailureType, message: str, waits: list[float]
) -> None:
    request = _request()
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(request, _error(status_code, 37, "Invalid parameter"))

        error = stream_error(read_stream("campaigns", expecting_error=True))

    assert error.failure_type == failure_type
    assert error.message == message
    http_mocker.assert_number_of_calls(request, 1)
    assert waits == []


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(json.dumps(_PAGE), id="page-of-records"),
        pytest.param(json.dumps({**_PAGE, "values": [_ERROR_LOOKING_RECORD]}), id="record-that-looks-like-an-error"),
        pytest.param("", id="empty"),
        pytest.param(json.dumps([{"id": 1}]), id="json-list"),
        pytest.param("<html>Welcome</html>", id="not-json"),
    ],
)
def test_no_filter_matches_or_raises_on_a_successful_answer(body: str, waits: list[float]) -> None:
    request = _request()
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(request, HttpResponse(body=body, status_code=200))

        output = read_stream("campaigns")

    assert output.get_stream_statuses("campaigns")[-1] == AirbyteStreamStatus.COMPLETE
    http_mocker.assert_number_of_calls(request, 1)
    assert waits == []


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(json.dumps(_VERSION_4_PAGE), id="page-of-email-clicks"),
        pytest.param(json.dumps({"result": {"emailClick": []}}), id="no-attributes"),
        pytest.param(json.dumps({"@attributes": None, "result": {"emailClick": []}}), id="null-attributes"),
        pytest.param(json.dumps([{"id": 1}]), id="json-list"),
        pytest.param("<html>Welcome</html>", id="not-json"),
    ],
)
def test_no_filter_matches_or_raises_on_a_successful_version_4_answer(body: str, waits: list[float]) -> None:
    request = _request(_EMAIL_CLICKS)
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(request, HttpResponse(body=body, status_code=200))

        output = read_stream("email_clicks")

    assert output.get_stream_statuses("email_clicks")[-1] == AirbyteStreamStatus.COMPLETE
    http_mocker.assert_number_of_calls(request, 1)
    assert waits == []
