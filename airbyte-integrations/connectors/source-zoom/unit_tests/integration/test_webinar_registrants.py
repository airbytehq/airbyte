# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_registrants` stream.

`GET /webinars/{webinarId}/registrants` is called for every webinar returned by
`GET /users/{userId}/webinars` and paginated with `page_size=30` and
`next_page_token` until Zoom returns an empty token. Records are extracted
from `registrants` and get the parent webinar `id` injected as `webinar_id`.
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


_STREAM = "webinar_registrants"


class TestWebinarRegistrants(TestCase):
    @HttpMocker()
    def test_paginates_registrants_for_every_webinar_and_injects_webinar_id(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        path_1 = f"/webinars/{WEBINAR_1['id']}/registrants"
        path_2 = f"/webinars/{WEBINAR_2['id']}/registrants"
        request_1_page_1 = ZoomRequestBuilder.endpoint(path_1, paginated=True)
        request_1_page_2 = ZoomRequestBuilder.endpoint(path_1, paginated=True, next_page_token="registrants_page_2")
        request_2 = ZoomRequestBuilder.endpoint(path_2, paginated=True)
        http_mocker.get(
            request_1_page_1,
            json_response(
                {
                    "next_page_token": "registrants_page_2",
                    "registrants": [{"id": "r1", "email": "r1@example.com", "first_name": "Reg", "status": "approved"}],
                }
            ),
        )
        http_mocker.get(
            request_1_page_2,
            json_response({"next_page_token": "", "registrants": [{"id": "r2", "email": "r2@example.com", "status": "pending"}]}),
        )
        http_mocker.get(
            request_2,
            json_response({"next_page_token": "", "registrants": [{"id": "r3", "email": "r3@example.com", "status": "approved"}]}),
        )

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["id"]: record for record in record_data(output)}
        assert set(records) == {"r1", "r2", "r3"}
        assert records["r1"]["email"] == "r1@example.com"
        assert records["r1"]["webinar_id"] == WEBINAR_1["id"]
        assert records["r2"]["webinar_id"] == WEBINAR_1["id"]
        assert records["r3"]["webinar_id"] == WEBINAR_2["id"]
        http_mocker.assert_number_of_calls(request_1_page_1, 1)
        http_mocker.assert_number_of_calls(request_1_page_2, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
