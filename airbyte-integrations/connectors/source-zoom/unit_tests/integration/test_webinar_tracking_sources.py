# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_tracking_sources` stream.

`GET /webinars/{webinarId}/tracking_sources` is called once per webinar
returned by `GET /users/{userId}/webinars`; records are extracted from
`tracking_sources` and get the parent webinar `id` injected as `webinar_id`.
The stream has no paginator.
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


_STREAM = "webinar_tracking_sources"


class TestWebinarTrackingSources(TestCase):
    @HttpMocker()
    def test_reads_tracking_sources_for_every_webinar_and_injects_webinar_id(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        request_1 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_1['id']}/tracking_sources")
        request_2 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_2['id']}/tracking_sources")
        http_mocker.get(
            request_1,
            json_response(
                {
                    "total_records": 2,
                    "next_page_token": "ignored",
                    "tracking_sources": [
                        {
                            "id": "ts1",
                            "source_name": "Newsletter",
                            "tracking_url": "https://example.com/1",
                            "registration_count": 4,
                            "visitor_count": 10,
                        },
                        {
                            "id": "ts2",
                            "source_name": "Social",
                            "tracking_url": "https://example.com/2",
                            "registration_count": 1,
                            "visitor_count": 3,
                        },
                    ],
                }
            ),
        )
        http_mocker.get(
            request_2,
            json_response(
                {"total_records": 1, "tracking_sources": [{"id": "ts3", "source_name": "Ads", "registration_count": 0, "visitor_count": 1}]}
            ),
        )

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["id"]: record for record in record_data(output)}
        assert set(records) == {"ts1", "ts2", "ts3"}
        assert records["ts1"]["visitor_count"] == 10
        assert records["ts1"]["webinar_id"] == WEBINAR_1["id"]
        assert records["ts2"]["webinar_id"] == WEBINAR_1["id"]
        assert records["ts3"]["webinar_id"] == WEBINAR_2["id"]
        http_mocker.assert_number_of_calls(request_1, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
