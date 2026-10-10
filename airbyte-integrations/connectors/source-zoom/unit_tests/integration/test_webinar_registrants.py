# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_registrants` stream (`acceptance-test-config.yml` `empty_streams`).

`GET /webinars/{webinarId}/registrants` for every webinar returned by `GET /users/{userId}/webinars`.
Keyed on the webinar `id`, paginated with `page_size=30` and `next_page_token`, records under `registrants`,
injects `webinar_id`.
"""

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker

from .zoom_mocks import (
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


_STREAM = "webinar_registrants"
_NEXT_PAGE_TOKEN = "registrants-page-2"


def _registrants_request(webinar_id, next_page_token=None):
    return request(f"/webinars/{webinar_id}/registrants", paginated_query(next_page_token))


def _registrant(registrant_id):
    return {"id": registrant_id, "email": f"{registrant_id}@example.com", "first_name": "Jill", "last_name": "Chill", "status": "approved"}


class TestWebinarRegistrants(TestCase):
    @HttpMocker()
    def test_follows_next_page_token_and_injects_webinar_id(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        webinar_1_page_1 = _registrants_request(WEBINAR_1["id"])
        webinar_1_page_2 = _registrants_request(WEBINAR_1["id"], _NEXT_PAGE_TOKEN)
        webinar_2_page_1 = _registrants_request(WEBINAR_2["id"])
        http_mocker.get(webinar_1_page_1, json_response({"registrants": [_registrant("r1")], "next_page_token": _NEXT_PAGE_TOKEN}))
        http_mocker.get(webinar_1_page_2, json_response({"registrants": [_registrant("r2")], "next_page_token": ""}))
        http_mocker.get(webinar_2_page_1, json_response({"registrants": [_registrant("r3")], "next_page_token": ""}))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(records_data(output), key=lambda r: r["id"]) == [
            {**_registrant("r1"), "webinar_id": WEBINAR_1["id"]},
            {**_registrant("r2"), "webinar_id": WEBINAR_1["id"]},
            {**_registrant("r3"), "webinar_id": WEBINAR_2["id"]},
        ]
        for paged_request in (webinar_1_page_1, webinar_1_page_2, webinar_2_page_1):
            http_mocker.assert_number_of_calls(paged_request, 1)

    def test_parent_400_yields_no_records(self):
        assert_parent_400_is_skipped(_STREAM)

    def test_parent_403_fails_with_config_error(self):
        assert_parent_403_fails_with_config_error(_STREAM)
