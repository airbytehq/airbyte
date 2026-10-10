# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `report_webinar_participants` stream.

`GET /report/webinars/{webinarUUID}/participants` is called for every webinar
returned by `GET /users/{userId}/webinars`, with the UUID double URL-encoded in
the path, and paginated with `page_size=30` and `next_page_token`. Records are
extracted from `participants` and get the parent UUID injected as
`webinar_uuid`. The code 3001 (deleted webinar) skip is covered in
`unit_tests/test_error_handling.py`.
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


_STREAM = "report_webinar_participants"


class TestReportWebinarParticipants(TestCase):
    @HttpMocker()
    def test_paginates_participants_with_double_encoded_uuid_and_injects_webinar_uuid(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        path_1 = f"/report/webinars/{ENCODED_UUID_1}/participants"
        path_2 = f"/report/webinars/{ENCODED_UUID_2}/participants"
        request_1_page_1 = ZoomRequestBuilder.endpoint(path_1, paginated=True)
        request_1_page_2 = ZoomRequestBuilder.endpoint(path_1, paginated=True, next_page_token="participants_page_2")
        request_2 = ZoomRequestBuilder.endpoint(path_2, paginated=True)
        http_mocker.get(
            request_1_page_1,
            json_response(
                {
                    "next_page_token": "participants_page_2",
                    "participants": [{"id": "p1", "name": "Participant One", "user_email": "p1@example.com", "duration": 600}],
                }
            ),
        )
        http_mocker.get(
            request_1_page_2,
            json_response({"next_page_token": "", "participants": [{"id": "p2", "name": "Participant Two", "duration": 120}]}),
        )
        http_mocker.get(request_2, json_response({"next_page_token": "", "participants": [{"id": "p3", "name": "Participant Three"}]}))

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["id"]: record for record in record_data(output)}
        assert set(records) == {"p1", "p2", "p3"}
        assert records["p1"]["user_email"] == "p1@example.com"
        assert records["p1"]["webinar_uuid"] == WEBINAR_1["uuid"]
        assert records["p2"]["webinar_uuid"] == WEBINAR_1["uuid"]
        assert records["p3"]["webinar_uuid"] == WEBINAR_2["uuid"]
        http_mocker.assert_number_of_calls(request_1_page_1, 1)
        http_mocker.assert_number_of_calls(request_1_page_2, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
