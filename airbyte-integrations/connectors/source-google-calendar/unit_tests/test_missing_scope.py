#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""A token can lack one of the requested scopes, because Google lets the user grant each scope
separately on the consent screen. Google answers such requests with 403 insufficientPermissions
(and ACCESS_TOKEN_SCOPE_INSUFFICIENT in the error details); every stream must report that as a
missing scope, not as missing calendar access or a disabled API."""

import json

import freezegun
import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://www.googleapis.com/calendar/v3"
_CONFIG = {
    "credentials": {"auth_type": "oauth2.0", "client_id": "id", "client_secret": "secret", "refresh_token": "rt"},
    "calendarid": "primary",
}
_TOKEN_REQUEST = HttpRequest(
    "https://oauth2.googleapis.com/token",
    body="grant_type=refresh_token&client_id=id&client_secret=secret&refresh_token=rt",
)
_TOKEN_RESPONSE = HttpResponse(json.dumps({"access_token": "test-access-token", "expires_in": 3600}))


def _google_error(status_code: int, reason: str = "", details_reason: str = "") -> HttpResponse:
    error = {"code": status_code, "message": "Request had insufficient authentication scopes.", "status": "PERMISSION_DENIED"}
    if reason:
        error["errors"] = [{"message": "Insufficient Permission", "domain": "global", "reason": reason}]
    if details_reason:
        error["details"] = [{"@type": "type.googleapis.com/google.rpc.ErrorInfo", "reason": details_reason}]
    return HttpResponse(json.dumps({"error": error}), status_code=status_code)


# Google sends both markers; each one alone must still be recognised.
_SCOPE_ERRORS = [
    pytest.param(_google_error(403, "insufficientPermissions", "ACCESS_TOKEN_SCOPE_INSUFFICIENT"), id="both_markers"),
    pytest.param(_google_error(403, reason="insufficientPermissions"), id="errors_reason_only"),
    pytest.param(_google_error(403, details_reason="ACCESS_TOKEN_SCOPE_INSUFFICIENT"), id="details_reason_only"),
]
_FREEBUSY_REQUEST = HttpRequest(
    f"{_BASE_URL}/freeBusy",
    body=json.dumps({"timeMin": "2026-09-07T12:00:00Z", "timeMax": "2026-11-21T12:00:00Z", "items": [{"id": "me@x.com"}]}),
)
_PLAIN_403 = HttpResponse(
    json.dumps({"error": {"code": 403, "message": "Forbidden", "errors": [{"reason": "forbidden", "domain": "global"}]}}), status_code=403
)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _read(http_mocker: HttpMocker, stream: str):
    http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    return read(get_source(dict(_CONFIG)), dict(_CONFIG), catalog)


def _assert_missing_scope_error(output) -> None:
    assert output.errors, "expected the sync to fail"
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "missing a Google Calendar OAuth scope" in error.message


def _mock_calendar(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/calendars/primary"), HttpResponse(json.dumps({"kind": "calendar#calendar", "id": "me@x.com"}))
    )


@pytest.mark.parametrize("response", _SCOPE_ERRORS)
@pytest.mark.parametrize("stream, path", [("settings", "users/me/settings"), ("colors", "colors")])
def test_base_requester_reports_a_missing_scope(stream, path, response):
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(f"{_BASE_URL}/{path}", query_params={"maxResults": "250"} if stream == "settings" else {}), response)

        _assert_missing_scope_error(_read(http_mocker, stream))


@freezegun.freeze_time("2026-10-07T12:00:00Z")
@pytest.mark.parametrize("response", _SCOPE_ERRORS)
def test_freebusy_reports_a_missing_scope(response):
    with HttpMocker() as http_mocker:
        _mock_calendar(http_mocker)
        http_mocker.post(_FREEBUSY_REQUEST, response)

        _assert_missing_scope_error(_read(http_mocker, "freebusy"))


def test_scope_marker_on_a_non_403_is_not_a_missing_scope():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/users/me/settings", query_params={"maxResults": "250"}), _google_error(400, "insufficientPermissions")
        )

        output = _read(http_mocker, "settings")

        assert output.errors, "expected the sync to fail"
        assert "missing a Google Calendar OAuth scope" not in output.errors[0].trace.error.message


def test_plain_403_keeps_the_access_message():
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(f"{_BASE_URL}/users/me/settings", query_params={"maxResults": "250"}), _PLAIN_403)

        output = _read(http_mocker, "settings")

        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert "lacks access to this calendar" in error.message


@freezegun.freeze_time("2026-10-07T12:00:00Z")
def test_freebusy_plain_403_keeps_the_access_message():
    with HttpMocker() as http_mocker:
        _mock_calendar(http_mocker)
        http_mocker.post(_FREEBUSY_REQUEST, _PLAIN_403)

        output = _read(http_mocker, "freebusy")

        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert "lacks access to free/busy" in error.message
