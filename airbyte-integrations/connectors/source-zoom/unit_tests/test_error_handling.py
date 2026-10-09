# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for source-zoom per-resource error handling.

Zoom returns business errors as JSON bodies (`code`/`message`), often on
non-2xx statuses:

* code 3161 on `GET /users/{id}/meetings` when a user is not licensed to host
  meetings — the sync should skip that user's partition instead of failing.
* code 3001 on `GET /meetings/{id}` and `GET /report/webinars/{uuid}` when the
  resource was deleted — the sync should skip the resource.
* Webinar UUIDs can contain `/` and `//`, which Zoom requires to be double
  URL-encoded in the report/past-webinar paths.

Other errors (e.g. missing OAuth scopes, code 4700) must still fail the sync.
"""

import json
from typing import Any, Dict
from unittest import TestCase

import pytest

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_BASE_URL = "https://api.zoom.us/v2"

_CONFIG = {
    "account_id": "test_account_id",
    "client_id": "test_client_id",
    "client_secret": "test_client_secret",
    "authorization_endpoint": "https://zoom.us/oauth/token",
}

_TOKEN_REQUEST = HttpRequest(
    url="https://zoom.us/oauth/token",
    query_params={"grant_type": "account_credentials", "account_id": "test_account_id"},
)

_USERS_REQUEST = HttpRequest(url=f"{_BASE_URL}/users", query_params={"page_size": "30"})
_USERS_RESPONSE = HttpResponse(json.dumps({"users": [{"id": "u1"}, {"id": "u2"}], "next_page_token": ""}))
_ONE_USER_RESPONSE = HttpResponse(json.dumps({"users": [{"id": "u1"}], "next_page_token": ""}))


def _zoom_error(code: int, message: str, status_code: int = 400) -> HttpResponse:
    return HttpResponse(json.dumps({"code": code, "message": message}), status_code=status_code)


def _user_meetings_request(user_id: str) -> HttpRequest:
    return HttpRequest(url=f"{_BASE_URL}/users/{user_id}/meetings", query_params={"page_size": "30"})


def _user_webinars_request(user_id: str) -> HttpRequest:
    return HttpRequest(url=f"{_BASE_URL}/users/{user_id}/webinars", query_params={"page_size": "30"})


def _read(stream_name: str) -> EntrypointOutput:
    config = dict(_CONFIG)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


def _mock_token(http_mocker: HttpMocker) -> None:
    # Every requester in a stream's parent chain fetches its own token, so the
    # call count depends on the stream - never assert on it.
    http_mocker.post(_TOKEN_REQUEST, HttpResponse(json.dumps({"access_token": "test_access_token", "expires_in": 3599})))


def _mock_users(http_mocker: HttpMocker) -> None:
    http_mocker.get(_USERS_REQUEST, _USERS_RESPONSE)


class TestMeetings(TestCase):
    _STREAM = "meetings"

    @HttpMocker()
    def test_meetings_skips_user_not_allowed_to_host_3161(self, http_mocker: HttpMocker):
        """A user partition returning code 3161 is skipped; other partitions still sync."""
        _mock_token(http_mocker)
        _mock_users(http_mocker)
        http_mocker.get(
            _user_meetings_request("u1"),
            HttpResponse(json.dumps({"meetings": [{"id": 1, "uuid": "aaa=="}], "next_page_token": ""})),
        )
        http_mocker.get(
            _user_meetings_request("u2"),
            _zoom_error(3161, "Your user account is not allowed meeting hosting and scheduling capabilities."),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/meetings/1"),
            HttpResponse(json.dumps({"id": 1, "uuid": "aaa==", "topic": "t"})),
        )

        output = _read(self._STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(self._STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1
        assert output.is_in_logs("Zoom returned code 3161")

    @HttpMocker()
    def test_meetings_does_not_ignore_missing_scope_4700(self, http_mocker: HttpMocker):
        """Guardrail: a missing-scope error (code 4700) must still fail the sync."""
        _mock_token(http_mocker)
        http_mocker.get(_USERS_REQUEST, _ONE_USER_RESPONSE)
        http_mocker.get(
            _user_meetings_request("u1"),
            _zoom_error(4700, "Invalid access token, does not contain scopes:[meeting:read:admin]."),
        )

        output = _read(self._STREAM)

        assert output.errors != []
        assert AirbyteStreamStatus.COMPLETE not in output.get_stream_statuses(self._STREAM)

    @HttpMocker()
    def test_meetings_skips_deleted_meeting_3001(self, http_mocker: HttpMocker):
        """A meeting deleted between listing and fetching (code 3001) is skipped."""
        _mock_token(http_mocker)
        _mock_users(http_mocker)
        http_mocker.get(
            _user_meetings_request("u1"),
            HttpResponse(json.dumps({"meetings": [{"id": 1, "uuid": "aaa=="}, {"id": 2, "uuid": "bbb=="}], "next_page_token": ""})),
        )
        http_mocker.get(
            _user_meetings_request("u2"),
            HttpResponse(json.dumps({"meetings": [{"id": 2, "uuid": "bbb=="}], "next_page_token": ""})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/meetings/1"),
            HttpResponse(json.dumps({"id": 1, "uuid": "aaa==", "topic": "t"})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/meetings/2"),
            _zoom_error(3001, "Meeting does not exist: 2.", status_code=404),
        )

        output = _read(self._STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(self._STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1
        assert output.is_in_logs("Zoom returned code 3001")


class TestReportWebinars(TestCase):
    _STREAM = "report_webinars"

    # GET /users/{id}/webinars returns these two webinar records; their UUIDs are
    # used as the report path partition and must be double URL-encoded.
    _WEBINARS_PAGE = HttpResponse(
        json.dumps(
            {
                "webinars": [
                    {"id": 11, "uuid": "wPUYIy/pR2mPs5r9no2GmA=="},
                    {"id": 12, "uuid": "/abc//d=="},
                ],
                "next_page_token": "",
            }
        )
    )
    _WEBINARS_PAGE_U2 = HttpResponse(json.dumps({"webinars": [{"id": 12, "uuid": "/abc//d=="}], "next_page_token": ""}))
    _ENCODED_UUID_1 = "wPUYIy%252FpR2mPs5r9no2GmA%253D%253D"
    _ENCODED_UUID_2 = "%252Fabc%252F%252Fd%253D%253D"

    @HttpMocker()
    def test_report_webinars_double_encodes_uuid_and_skips_3001(self, http_mocker: HttpMocker):
        _mock_token(http_mocker)
        _mock_users(http_mocker)
        http_mocker.get(_user_webinars_request("u1"), self._WEBINARS_PAGE)
        http_mocker.get(_user_webinars_request("u2"), self._WEBINARS_PAGE_U2)

        report_request_1 = HttpRequest(url=f"{_BASE_URL}/report/webinars/{self._ENCODED_UUID_1}")
        report_request_2 = HttpRequest(url=f"{_BASE_URL}/report/webinars/{self._ENCODED_UUID_2}")
        http_mocker.get(
            report_request_1,
            HttpResponse(json.dumps({"id": 11, "uuid": "wPUYIy/pR2mPs5r9no2GmA==", "topic": "t"})),
        )
        http_mocker.get(
            report_request_2,
            _zoom_error(3001, "Meeting does not exist.", status_code=404),
        )

        output = _read(self._STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(self._STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert len(output.records) == 1
        assert output.records[0].record.data["uuid"] == "wPUYIy/pR2mPs5r9no2GmA=="
        assert output.records[0].record.data["webinar_uuid"] == "wPUYIy/pR2mPs5r9no2GmA=="
        assert output.is_in_logs("Zoom returned code 3001")
        http_mocker.assert_number_of_calls(report_request_1, 1)
        http_mocker.assert_number_of_calls(report_request_2, 2)


class TestReportWebinarParticipants(TestCase):
    _STREAM = "report_webinar_participants"
    _WEBINARS_PAGE = TestReportWebinars._WEBINARS_PAGE
    _WEBINARS_PAGE_U2 = TestReportWebinars._WEBINARS_PAGE_U2
    _ENCODED_UUID_1 = TestReportWebinars._ENCODED_UUID_1
    _ENCODED_UUID_2 = TestReportWebinars._ENCODED_UUID_2

    @HttpMocker()
    def test_report_webinar_participants_double_encodes_uuid(self, http_mocker: HttpMocker):
        _mock_token(http_mocker)
        _mock_users(http_mocker)
        http_mocker.get(_user_webinars_request("u1"), self._WEBINARS_PAGE)
        http_mocker.get(_user_webinars_request("u2"), self._WEBINARS_PAGE_U2)

        participants_request_1 = HttpRequest(
            url=f"{_BASE_URL}/report/webinars/{self._ENCODED_UUID_1}/participants",
            query_params={"page_size": "30"},
        )
        participants_request_2 = HttpRequest(
            url=f"{_BASE_URL}/report/webinars/{self._ENCODED_UUID_2}/participants",
            query_params={"page_size": "30"},
        )
        http_mocker.get(
            participants_request_1,
            HttpResponse(json.dumps({"participants": [{"id": "p1", "user_id": "x"}], "next_page_token": ""})),
        )
        http_mocker.get(
            participants_request_2,
            _zoom_error(3001, "Meeting does not exist.", status_code=404),
        )

        output = _read(self._STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(self._STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "p1"
        assert output.is_in_logs("Zoom returned code 3001")
        http_mocker.assert_number_of_calls(participants_request_1, 1)
        http_mocker.assert_number_of_calls(participants_request_2, 2)


# The manifest inlines the parent chain into every stream, so each stream below reads its own copy of the
# requester that carries the 3161 / 3001 filter or the double-encoded UUID path.
@pytest.mark.parametrize(
    "stream_name",
    [
        "meeting_registrants",
        "meeting_polls",
        "meeting_poll_results",
        "meeting_registration_questions",
        "report_meetings",
        "report_meeting_participants",
    ],
)
def test_meeting_child_streams_skip_user_not_allowed_to_host_3161(stream_name):
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(_USERS_REQUEST, _ONE_USER_RESPONSE)
        http_mocker.get(
            _user_meetings_request("u1"),
            _zoom_error(3161, "Your user account is not allowed meeting hosting and scheduling capabilities."),
        )

        output = _read(stream_name)

    assert output.errors == []
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE


@pytest.mark.parametrize(
    "stream_name, parent_resource, child_path",
    [
        ("meeting_registrants", "meetings", "/meetings/1/registrants"),
        ("meeting_polls", "meetings", "/meetings/1/polls"),
        ("meeting_registration_questions", "meetings", "/meetings/1/registrants/questions"),
        ("webinar_registration_questions", "webinars", "/webinars/1/registrants/questions"),
        ("webinar_tracking_sources", "webinars", "/webinars/1/tracking_sources"),
    ],
)
def test_child_streams_skip_deleted_resource_3001(stream_name, parent_resource, child_path):
    # 404, not 400: several of these requesters already ignore every 400.
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(_USERS_REQUEST, _ONE_USER_RESPONSE)
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/users/u1/{parent_resource}", query_params={"page_size": "30"}),
            HttpResponse(json.dumps({parent_resource: [{"id": 1, "uuid": "aaa=="}], "next_page_token": ""})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}{child_path}", query_params=ANY_QUERY_PARAMS),
            _zoom_error(3001, "Meeting does not exist: 1.", status_code=404),
        )

        output = _read(stream_name)

    assert output.errors == []
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE


@pytest.mark.parametrize(
    "stream_name, path, body",
    [
        ("webinar_absentees", "/past_webinars/{}/absentees", {"registrants": [], "next_page_token": ""}),
        ("webinar_poll_results", "/past_webinars/{}/polls", {"questions": []}),
        ("webinar_qna_results", "/past_webinars/{}/qa", {"questions": []}),
    ],
)
def test_past_webinar_streams_double_encode_uuid(stream_name, path, body):
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(_USERS_REQUEST, _ONE_USER_RESPONSE)
        http_mocker.get(
            _user_webinars_request("u1"),
            HttpResponse(json.dumps({"webinars": [{"id": 12, "uuid": "/abc//d=="}], "next_page_token": ""})),
        )
        child_request = HttpRequest(url=_BASE_URL + path.format(TestReportWebinars._ENCODED_UUID_2), query_params=ANY_QUERY_PARAMS)
        http_mocker.get(child_request, HttpResponse(json.dumps(body)))

        output = _read(stream_name)

    assert output.errors == []
    http_mocker.assert_number_of_calls(child_request, 1)
