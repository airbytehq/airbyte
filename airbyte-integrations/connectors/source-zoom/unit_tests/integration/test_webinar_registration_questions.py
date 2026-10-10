# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_registration_questions` stream.

`GET /webinars/{webinarId}/registrants/questions` is called once per webinar
returned by `GET /users/{userId}/webinars`; the whole response body
(`questions` and `custom_questions`) is one record, with the parent webinar
`id` injected as `webinar_id`. The stream has no paginator.
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


_STREAM = "webinar_registration_questions"


class TestWebinarRegistrationQuestions(TestCase):
    @HttpMocker()
    def test_reads_one_record_per_webinar_and_injects_webinar_id(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        request_1 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_1['id']}/registrants/questions")
        request_2 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_2['id']}/registrants/questions")
        questions_1 = [{"field_name": "last_name", "required": True}]
        custom_questions_1 = [{"title": "How did you hear about us?", "type": "short", "required": False, "answers": []}]
        http_mocker.get(request_1, json_response({"questions": questions_1, "custom_questions": custom_questions_1}))
        http_mocker.get(request_2, json_response({"questions": [{"field_name": "city", "required": False}], "custom_questions": []}))

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["webinar_id"]: record for record in record_data(output)}
        assert set(records) == {WEBINAR_1["id"], WEBINAR_2["id"]}
        assert records[WEBINAR_1["id"]]["questions"] == questions_1
        assert records[WEBINAR_1["id"]]["custom_questions"] == custom_questions_1
        assert records[WEBINAR_2["id"]]["custom_questions"] == []
        http_mocker.assert_number_of_calls(request_1, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
