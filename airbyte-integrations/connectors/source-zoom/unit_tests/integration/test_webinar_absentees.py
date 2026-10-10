# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_absentees` stream (`acceptance-test-config.yml` `empty_streams`).

`GET /past_webinars/{webinarUUID}/absentees` for every webinar returned by `GET /users/{userId}/webinars`.
Keyed on the webinar `uuid` (double URL-encoded in the path), paginated with `page_size=30` and
`next_page_token`, records under `registrants`, injects `webinar_uuid`.
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
)


_STREAM = "webinar_absentees"
_NEXT_PAGE_TOKEN = "absentees-page-2"


def _absentees_request(webinar_uuid, next_page_token=None):
    return request(f"/past_webinars/{ENCODED_UUIDS[webinar_uuid]}/absentees", paginated_query(next_page_token))


def _absentee(absentee_id):
    return {"id": absentee_id, "email": f"{absentee_id}@example.com", "first_name": "Jill", "last_name": "Chill", "status": "approved"}


class TestWebinarAbsentees(TestCase):
    @HttpMocker()
    def test_double_encodes_uuid_follows_next_page_token_and_injects_webinar_uuid(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        webinar_1_page_1 = _absentees_request(WEBINAR_1["uuid"])
        webinar_1_page_2 = _absentees_request(WEBINAR_1["uuid"], _NEXT_PAGE_TOKEN)
        webinar_2_page_1 = _absentees_request(WEBINAR_2["uuid"])
        http_mocker.get(webinar_1_page_1, json_response({"registrants": [_absentee("a1")], "next_page_token": _NEXT_PAGE_TOKEN}))
        http_mocker.get(webinar_1_page_2, json_response({"registrants": [_absentee("a2")], "next_page_token": ""}))
        http_mocker.get(webinar_2_page_1, json_response({"registrants": [_absentee("a3")], "next_page_token": ""}))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(records_data(output), key=lambda r: r["id"]) == [
            {**_absentee("a1"), "webinar_uuid": WEBINAR_1["uuid"]},
            {**_absentee("a2"), "webinar_uuid": WEBINAR_1["uuid"]},
            {**_absentee("a3"), "webinar_uuid": WEBINAR_2["uuid"]},
        ]
        for paged_request in (webinar_1_page_1, webinar_1_page_2, webinar_2_page_1):
            http_mocker.assert_number_of_calls(paged_request, 1)

    def test_parent_400_yields_no_records(self):
        assert_parent_400_is_skipped(_STREAM)

    def test_parent_403_fails_with_config_error(self):
        assert_parent_403_fails_with_config_error(_STREAM)
