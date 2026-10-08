# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_poll_results` stream (`acceptance-test-config.yml` `empty_streams`).

`GET /past_webinars/{webinarUUID}/polls` for every webinar returned by `GET /users/{userId}/webinars`.
Keyed on the webinar `uuid` (double URL-encoded in the path), not paginated, records under `questions`,
injects `webinar_uuid`.
"""

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker

from .zoom_mocks import (
    ENCODED_UUIDS,
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


_STREAM = "webinar_poll_results"
_POLL_RESULTS_REQUESTS = {webinar["uuid"]: request(f"/past_webinars/{ENCODED_UUIDS[webinar['uuid']]}/polls") for webinar in WEBINARS}


def _poll_result(webinar_id):
    return {
        "email": f"{webinar_id}@example.com",
        "name": "Jill Chill",
        "question_details": [{"question": "Q1", "answer": "a", "date_time": "2026-01-01T10:00:00Z", "polling_id": "poll-1"}],
    }


class TestWebinarPollResults(TestCase):
    @HttpMocker()
    def test_double_encodes_uuid_and_injects_webinar_uuid(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        for webinar in WEBINARS:
            http_mocker.get(
                _POLL_RESULTS_REQUESTS[webinar["uuid"]],
                json_response({"id": webinar["id"], "uuid": webinar["uuid"], "questions": [_poll_result(webinar["id"])]}),
            )

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(records_data(output), key=lambda r: r["email"]) == [
            {**_poll_result(webinar["id"]), "webinar_uuid": webinar["uuid"]} for webinar in WEBINARS
        ]
        for webinar in WEBINARS:
            http_mocker.assert_number_of_calls(_POLL_RESULTS_REQUESTS[webinar["uuid"]], 1)

    def test_parent_400_yields_no_records(self):
        assert_parent_400_is_skipped(_STREAM)

    def test_parent_403_fails_with_config_error(self):
        assert_parent_403_fails_with_config_error(_STREAM)
