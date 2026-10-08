# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `report_webinars` stream.

`GET /report/webinars/{webinarUUID}` is called once per webinar returned by
`GET /users/{userId}/webinars`, with the UUID double URL-encoded in the path.
The whole response body is one record, with the parent UUID injected as
`webinar_uuid`. The stream has no paginator. The code 3001 (deleted webinar)
skip is covered in `unit_tests/test_error_handling.py`.
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


_STREAM = "report_webinars"


class TestReportWebinars(TestCase):
    @HttpMocker()
    def test_reads_report_with_double_encoded_uuid_and_injects_webinar_uuid(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        request_1 = ZoomRequestBuilder.endpoint(f"/report/webinars/{ENCODED_UUID_1}")
        request_2 = ZoomRequestBuilder.endpoint(f"/report/webinars/{ENCODED_UUID_2}")
        http_mocker.get(
            request_1,
            json_response(
                {"id": WEBINAR_1["id"], "uuid": WEBINAR_1["uuid"], "topic": "Webinar one", "participants_count": 12, "duration": 60}
            ),
        )
        http_mocker.get(
            request_2,
            json_response(
                {"id": WEBINAR_2["id"], "uuid": WEBINAR_2["uuid"], "topic": "Webinar two", "participants_count": 3, "duration": 30}
            ),
        )

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["id"]: record for record in record_data(output)}
        assert set(records) == {WEBINAR_1["id"], WEBINAR_2["id"]}
        assert records[WEBINAR_1["id"]]["participants_count"] == 12
        assert records[WEBINAR_1["id"]]["webinar_uuid"] == WEBINAR_1["uuid"]
        assert records[WEBINAR_2["id"]]["webinar_uuid"] == WEBINAR_2["uuid"]
        http_mocker.assert_number_of_calls(request_1, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
