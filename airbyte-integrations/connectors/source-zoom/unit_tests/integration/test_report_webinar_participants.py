# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `report_webinar_participants` stream (`acceptance-test-config.yml` `empty_streams`).

`GET /report/webinars/{webinarUUID}/participants` for every webinar returned by `GET /users/{userId}/webinars`.
Keyed on the webinar `uuid` (double URL-encoded in the path), paginated with `page_size=30` and
`next_page_token`, records under `participants`, injects `webinar_uuid`. A webinar with no report data
(code 3001) is skipped.
"""

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker

from .zoom_mocks import (
    ENCODED_UUIDS,
    WEBINAR_1,
    WEBINAR_2,
    assert_completed_without_errors,
    assert_parent_400_is_skipped,
    assert_parent_403_fails_with_config_error,
    json_response,
    mock_webinar_parents,
    paginated_query,
    read_stream,
    records_data,
    request,
    zoom_error,
)


_STREAM = "report_webinar_participants"
_NEXT_PAGE_TOKEN = "participants-page-2"


def _participants_request(webinar_uuid, next_page_token=None):
    return request(f"/report/webinars/{ENCODED_UUIDS[webinar_uuid]}/participants", paginated_query(next_page_token))


def _participant(participant_id):
    return {
        "id": participant_id,
        "user_id": f"user-{participant_id}",
        "name": "Jill Chill",
        "user_email": f"{participant_id}@example.com",
        "join_time": "2026-01-01T10:00:00Z",
        "leave_time": "2026-01-01T11:00:00Z",
        "duration": 3600,
        "status": "in_meeting",
    }


class TestReportWebinarParticipants(TestCase):
    @HttpMocker()
    def test_double_encodes_uuid_follows_next_page_token_and_injects_webinar_uuid(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        webinar_1_page_1 = _participants_request(WEBINAR_1["uuid"])
        webinar_1_page_2 = _participants_request(WEBINAR_1["uuid"], _NEXT_PAGE_TOKEN)
        webinar_2_page_1 = _participants_request(WEBINAR_2["uuid"])
        http_mocker.get(webinar_1_page_1, json_response({"participants": [_participant("p1")], "next_page_token": _NEXT_PAGE_TOKEN}))
        http_mocker.get(webinar_1_page_2, json_response({"participants": [_participant("p2")], "next_page_token": ""}))
        http_mocker.get(webinar_2_page_1, json_response({"participants": [_participant("p3")], "next_page_token": ""}))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(records_data(output), key=lambda r: r["id"]) == [
            {**_participant("p1"), "webinar_uuid": WEBINAR_1["uuid"]},
            {**_participant("p2"), "webinar_uuid": WEBINAR_1["uuid"]},
            {**_participant("p3"), "webinar_uuid": WEBINAR_2["uuid"]},
        ]
        for paged_request in (webinar_1_page_1, webinar_1_page_2, webinar_2_page_1):
            http_mocker.assert_number_of_calls(paged_request, 1)

    @HttpMocker()
    def test_skips_webinar_without_report_3001(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        http_mocker.get(
            _participants_request(WEBINAR_1["uuid"]),
            json_response({"participants": [_participant("p1")], "next_page_token": ""}),
        )
        http_mocker.get(_participants_request(WEBINAR_2["uuid"]), zoom_error(3001, "Meeting does not exist.", status_code=404))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert records_data(output) == [{**_participant("p1"), "webinar_uuid": WEBINAR_1["uuid"]}]
        assert output.is_in_logs("Zoom returned code 3001")

    def test_parent_400_yields_no_records(self):
        assert_parent_400_is_skipped(_STREAM)

    def test_parent_403_fails_with_config_error(self):
        assert_parent_403_fails_with_config_error(_STREAM)
