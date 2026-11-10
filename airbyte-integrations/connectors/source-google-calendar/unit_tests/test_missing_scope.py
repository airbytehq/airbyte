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
_TOKEN_RESPONSE = HttpResponse(json.dumps({"access_token": "at", "expires_in": 3600}))
_INSUFFICIENT_SCOPE = HttpResponse(
    json.dumps(
        {
            "error": {
                "code": 403,
                "message": "Request had insufficient authentication scopes.",
                "errors": [{"message": "Insufficient Permission", "domain": "global", "reason": "insufficientPermissions"}],
                "status": "PERMISSION_DENIED",
                "details": [{"@type": "type.googleapis.com/google.rpc.ErrorInfo", "reason": "ACCESS_TOKEN_SCOPE_INSUFFICIENT"}],
            }
        }
    ),
    status_code=403,
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


@pytest.mark.parametrize("stream, path", [("settings", "users/me/settings"), ("colors", "colors")])
def test_base_requester_reports_a_missing_scope(stream, path):
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(f"{_BASE_URL}/{path}"), _INSUFFICIENT_SCOPE)

        _assert_missing_scope_error(_read(http_mocker, stream))


@freezegun.freeze_time("2026-10-07T12:00:00Z")
def test_freebusy_reports_a_missing_scope():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/calendars/primary"), HttpResponse(json.dumps({"kind": "calendar#calendar", "id": "me@x.com"}))
        )
        http_mocker.post(
            HttpRequest(
                f"{_BASE_URL}/freeBusy",
                body=json.dumps({"timeMin": "2026-09-07T12:00:00Z", "timeMax": "2026-11-21T12:00:00Z", "items": [{"id": "me@x.com"}]}),
            ),
            _INSUFFICIENT_SCOPE,
        )

        _assert_missing_scope_error(_read(http_mocker, "freebusy"))


def test_plain_403_keeps_the_access_message():
    with HttpMocker() as http_mocker:
        forbidden = {"error": {"code": 403, "message": "Forbidden", "errors": [{"reason": "forbidden", "domain": "global"}]}}
        http_mocker.get(HttpRequest(f"{_BASE_URL}/users/me/settings"), HttpResponse(json.dumps(forbidden), status_code=403))

        output = _read(http_mocker, "settings")

        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert "lacks access to this calendar" in error.message
