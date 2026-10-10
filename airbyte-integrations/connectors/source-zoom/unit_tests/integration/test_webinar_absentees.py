# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_absentees` stream.

`GET /past_webinars/{webinarUUID}/absentees` is called for every webinar
returned by `GET /users/{userId}/webinars`, with the UUID double URL-encoded
in the path (Zoom requires it for UUIDs that start with `/` or contain `//`).
It is paginated with `page_size=30` and `next_page_token`; records are
extracted from `registrants` and get the parent UUID injected as `webinar_uuid`.
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


_STREAM = "webinar_absentees"


class TestWebinarAbsentees(TestCase):
    @HttpMocker()
    def test_paginates_absentees_with_double_encoded_uuid_and_injects_webinar_uuid(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        path_1 = f"/past_webinars/{ENCODED_UUID_1}/absentees"
        path_2 = f"/past_webinars/{ENCODED_UUID_2}/absentees"
        request_1_page_1 = ZoomRequestBuilder.endpoint(path_1, paginated=True)
        request_1_page_2 = ZoomRequestBuilder.endpoint(path_1, paginated=True, next_page_token="absentees_page_2")
        request_2 = ZoomRequestBuilder.endpoint(path_2, paginated=True)
        http_mocker.get(
            request_1_page_1,
            json_response({"next_page_token": "absentees_page_2", "registrants": [{"id": "a1", "email": "a1@example.com"}]}),
        )
        http_mocker.get(request_1_page_2, json_response({"next_page_token": "", "registrants": [{"id": "a2", "email": "a2@example.com"}]}))
        http_mocker.get(request_2, json_response({"next_page_token": "", "registrants": [{"id": "a3", "email": "a3@example.com"}]}))

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["id"]: record for record in record_data(output)}
        assert set(records) == {"a1", "a2", "a3"}
        assert records["a1"]["email"] == "a1@example.com"
        assert records["a1"]["webinar_uuid"] == WEBINAR_1["uuid"]
        assert records["a2"]["webinar_uuid"] == WEBINAR_1["uuid"]
        assert records["a3"]["webinar_uuid"] == WEBINAR_2["uuid"]
        http_mocker.assert_number_of_calls(request_1_page_1, 1)
        http_mocker.assert_number_of_calls(request_1_page_2, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
