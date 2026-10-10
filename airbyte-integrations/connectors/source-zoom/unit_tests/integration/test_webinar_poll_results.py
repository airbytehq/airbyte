# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_poll_results` stream.

`GET /past_webinars/{webinarUUID}/polls` is called once per webinar returned by
`GET /users/{userId}/webinars`, with the UUID double URL-encoded in the path.
Records are extracted from `questions` (one per participant) and get the
parent UUID injected as `webinar_uuid`. The stream has no paginator.
"""

from unittest import TestCase

from airbyte_cdk.models import AirbyteStreamStatus
from airbyte_cdk.test.mock_http import HttpMocker

from .helpers import (
    ENCODED_UUID_1,
    ENCODED_UUID_2,
    USER_ID,
    WEBINAR_1,
    WEBINAR_2,
    assert_parent_400_skips_stream,
    assert_parent_403_fails_stream_with_config_error,
    mock_parents,
    read_stream,
    record_data,
)
from .request_builder import ZoomRequestBuilder, json_response


_STREAM = "webinar_poll_results"


class TestWebinarPollResults(TestCase):
    @HttpMocker()
    def test_reads_poll_results_with_double_encoded_uuid_and_injects_webinar_uuid(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        request_1 = ZoomRequestBuilder.endpoint(f"/past_webinars/{ENCODED_UUID_1}/polls")
        request_2 = ZoomRequestBuilder.endpoint(f"/past_webinars/{ENCODED_UUID_2}/polls")
        details = [{"question": "Favourite colour?", "answer": "blue", "polling_id": "poll1", "date_time": "2026-01-01T10:00:00Z"}]
        http_mocker.get(
            request_1,
            json_response(
                {
                    "id": WEBINAR_1["id"],
                    "uuid": WEBINAR_1["uuid"],
                    "questions": [
                        {"email": "p1@example.com", "name": "Participant One", "question_details": details},
                        {"email": "p2@example.com", "name": "Participant Two", "question_details": []},
                    ],
                }
            ),
        )
        http_mocker.get(
            request_2,
            json_response(
                {"id": WEBINAR_2["id"], "uuid": WEBINAR_2["uuid"], "questions": [{"email": "p3@example.com", "name": "Participant Three"}]}
            ),
        )

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["email"]: record for record in record_data(output)}
        assert set(records) == {"p1@example.com", "p2@example.com", "p3@example.com"}
        assert records["p1@example.com"]["question_details"] == details
        assert records["p1@example.com"]["webinar_uuid"] == WEBINAR_1["uuid"]
        assert records["p2@example.com"]["webinar_uuid"] == WEBINAR_1["uuid"]
        assert records["p3@example.com"]["webinar_uuid"] == WEBINAR_2["uuid"]
        http_mocker.assert_number_of_calls(request_1, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
