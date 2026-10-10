# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinars` stream.

For every webinar listed by `GET /users/{userId}/webinars` (paginated with
`next_page_token`), the stream fetches the full object from
`GET /webinars/{webinarId}` and emits the whole response body as the record.
The detail endpoint has no paginator.
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


_STREAM = "webinars"


class TestWebinars(TestCase):
    @HttpMocker()
    def test_reads_webinar_details_for_every_listed_webinar(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        request_1 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_1['id']}")
        request_2 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_2['id']}")
        http_mocker.get(request_1, json_response({**WEBINAR_1, "agenda": "First agenda", "duration": 60, "type": 5}))
        http_mocker.get(request_2, json_response({**WEBINAR_2, "agenda": "Second agenda", "duration": 30, "type": 5}))

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["id"]: record for record in record_data(output)}
        assert set(records) == {WEBINAR_1["id"], WEBINAR_2["id"]}
        assert records[WEBINAR_1["id"]]["uuid"] == WEBINAR_1["uuid"]
        assert records[WEBINAR_1["id"]]["agenda"] == "First agenda"
        assert records[WEBINAR_2["id"]]["uuid"] == WEBINAR_2["uuid"]
        assert records[WEBINAR_2["id"]]["duration"] == 30
        http_mocker.assert_number_of_calls(request_1, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_follows_next_page_token_on_the_webinar_list(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(ZoomRequestBuilder.token(), json_response({"access_token": "test_access_token", "expires_in": 3599}))
        http_mocker.get(ZoomRequestBuilder.users(), json_response({"users": [{"id": USER_ID}], "next_page_token": ""}))
        list_page_1 = ZoomRequestBuilder.user_webinars(USER_ID)
        list_page_2 = ZoomRequestBuilder.user_webinars(USER_ID, next_page_token="list_page_2")
        http_mocker.get(list_page_1, json_response({"webinars": [WEBINAR_1], "next_page_token": "list_page_2"}))
        http_mocker.get(list_page_2, json_response({"webinars": [WEBINAR_2], "next_page_token": ""}))
        http_mocker.get(ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_1['id']}"), json_response(WEBINAR_1))
        http_mocker.get(ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_2['id']}"), json_response(WEBINAR_2))

        output = read_stream(_STREAM)

        assert output.errors == []
        assert {record["id"] for record in record_data(output)} == {WEBINAR_1["id"], WEBINAR_2["id"]}
        http_mocker.assert_number_of_calls(list_page_1, 1)
        http_mocker.assert_number_of_calls(list_page_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
