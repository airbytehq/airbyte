# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinars` stream (`acceptance-test-config.yml` `empty_streams`).

`GET /webinars/{webinarId}` for every webinar returned by `GET /users/{userId}/webinars`.
Keyed on the webinar `id`, not paginated, the whole response body is the record (no injected parent field).
"""

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .zoom_mocks import (
    MISSING_SCOPE,
    WEBINAR_1,
    WEBINAR_2,
    WEBINARS,
    assert_completed_without_errors,
    assert_parent_400_is_skipped,
    assert_parent_unhandled_403_fails_with_config_error,
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

    @freezegun.freeze_time("2026-10-20T12:00:00Z")
    def test_incremental_sync_uses_created_at_lookback(self):
        with HttpMocker() as http_mocker:
            mock_webinar_parents(http_mocker)
            for webinar in WEBINARS:
                http_mocker.get(_WEBINAR_REQUESTS[webinar["id"]], json_response(_webinar_details(webinar)))
            first = read_stream(_STREAM, sync_mode=SyncMode.incremental)

        assert_completed_without_errors(first, _STREAM)
        self.assertEqual(len(records_data(first)), 2)

        with HttpMocker() as http_mocker:
            mock_webinar_parents(http_mocker)
            http_mocker.get(
                _WEBINAR_REQUESTS[WEBINAR_1["id"]],
                json_response(_webinar_details(WEBINAR_1)),
            )
            http_mocker.get(_WEBINAR_REQUESTS[WEBINAR_2["id"]], json_response(_webinar_details(WEBINAR_2)))
            state = StateBuilder().with_stream_state(_STREAM, first.most_recent_state.stream_state.__dict__).build()
            second = read_stream(_STREAM, sync_mode=SyncMode.incremental, state=state)

        assert_completed_without_errors(second, _STREAM)
        self.assertEqual(len(records_data(second)), 1)
        self.assertEqual(records_data(second)[0]["created_at"], WEBINAR_2["created_at"])
        http_mocker.assert_number_of_calls(_WEBINAR_REQUESTS[WEBINAR_1["id"]], 0)

    def test_parent_400_yields_no_records(self):
        assert_parent_400_is_skipped(_STREAM)

    def test_parent_400_missing_scope_is_silently_skipped(self):
        # Known gap (airbytehq/airbyte-internal-issues#17524): the parent ignores every 400, so a token without
        # `webinar:read:admin` (code 4711) ends in an empty COMPLETE sync instead of a config error.
        assert_parent_400_is_skipped(_STREAM, MISSING_SCOPE)

    def test_parent_unhandled_403_fails_with_config_error(self):
        assert_parent_unhandled_403_fails_with_config_error(_STREAM)
