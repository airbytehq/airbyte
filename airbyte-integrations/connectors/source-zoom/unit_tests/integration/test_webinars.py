# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinars` stream (`acceptance-test-config.yml` `empty_streams`).

`GET /webinars/{webinarId}` for every webinar returned by `GET /users/{userId}/webinars`.
Keyed on the webinar `id`, not paginated, the whole response body is the record (no injected parent field).
"""

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker

from .zoom_mocks import (
    WEBINARS,
    assert_completed_without_errors,
    assert_parent_400_is_skipped,
    assert_parent_403_fails_with_config_error,
    json_response,
    mock_webinar_parents,
    read_stream,
    records_data,
    request,
)


_STREAM = "webinars"
_WEBINAR_REQUESTS = {webinar["id"]: request(f"/webinars/{webinar['id']}") for webinar in WEBINARS}


def _webinar_details(webinar):
    return {**webinar, "host_id": "u1", "type": 5, "duration": 60, "settings": {"approval_type": 2}}


class TestWebinars(TestCase):
    @HttpMocker()
    def test_reads_details_for_every_listed_webinar(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        for webinar in WEBINARS:
            http_mocker.get(_WEBINAR_REQUESTS[webinar["id"]], json_response(_webinar_details(webinar)))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(records_data(output), key=lambda r: r["id"]) == [_webinar_details(webinar) for webinar in WEBINARS]
        for webinar in WEBINARS:
            http_mocker.assert_number_of_calls(_WEBINAR_REQUESTS[webinar["id"]], 1)

    def test_parent_400_yields_no_records(self):
        assert_parent_400_is_skipped(_STREAM)

    def test_parent_403_fails_with_config_error(self):
        assert_parent_403_fails_with_config_error(_STREAM)
