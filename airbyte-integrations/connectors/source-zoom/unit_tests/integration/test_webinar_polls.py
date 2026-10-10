# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_polls` stream.

`GET /webinars/{webinarId}/polls` is called once per webinar returned by
`GET /users/{userId}/webinars`; records are extracted from `polls` and get the
parent webinar `id` injected as `webinar_id`. The stream has no paginator.
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


_STREAM = "webinar_polls"


class TestWebinarPolls(TestCase):
    @HttpMocker()
    def test_reads_polls_for_every_webinar_and_injects_webinar_id(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        request_1 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_1['id']}/polls")
        request_2 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_2['id']}/polls")
        question = {"name": "Favourite colour?", "type": "single", "answers": ["red", "blue"]}
        http_mocker.get(
            request_1,
            json_response(
                {
                    "total_records": 2,
                    "next_page_token": "ignored",
                    "polls": [
                        {"id": "poll1", "title": "Poll one", "status": "notstart", "anonymous": False, "questions": [question]},
                        {"id": "poll2", "title": "Poll two", "status": "ended", "anonymous": True, "questions": []},
                    ],
                }
            ),
        )
        http_mocker.get(
            request_2, json_response({"total_records": 1, "polls": [{"id": "poll3", "title": "Poll three", "status": "started"}]})
        )

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["id"]: record for record in record_data(output)}
        assert set(records) == {"poll1", "poll2", "poll3"}
        assert records["poll1"]["questions"] == [question]
        assert records["poll1"]["webinar_id"] == WEBINAR_1["id"]
        assert records["poll2"]["webinar_id"] == WEBINAR_1["id"]
        assert records["poll3"]["webinar_id"] == WEBINAR_2["id"]
        http_mocker.assert_number_of_calls(request_1, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
