# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_panelists` stream.

`GET /webinars/{webinarId}/panelists` is called once per webinar returned by
`GET /users/{userId}/webinars`; records are extracted from `panelists` and get
the parent webinar `id` injected as `webinar_id`. The stream has no paginator.
"""

from unittest import TestCase

from airbyte_cdk.models import AirbyteStreamStatus
from airbyte_cdk.test.mock_http import HttpMocker

from .helpers import (
    WEBINAR_1,
    WEBINAR_2,
    assert_parent_400_skips_stream,
    assert_parent_403_fails_stream_with_config_error,
    mock_parents,
    read_stream,
    record_data,
)
from .request_builder import ZoomRequestBuilder, json_response


_STREAM = "webinar_panelists"


class TestWebinarPanelists(TestCase):
    @HttpMocker()
    def test_reads_panelists_for_every_webinar_and_injects_webinar_id(self, http_mocker: HttpMocker) -> None:
        mock_parents(http_mocker)
        request_1 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_1['id']}/panelists")
        request_2 = ZoomRequestBuilder.endpoint(f"/webinars/{WEBINAR_2['id']}/panelists")
        # A `next_page_token` in the body must not trigger a second request: this endpoint is not paginated.
        http_mocker.get(
            request_1,
            json_response(
                {
                    "total_records": 2,
                    "next_page_token": "ignored",
                    "panelists": [
                        {"id": "pa1", "email": "pa1@example.com", "name": "Panelist One"},
                        {"id": "pa2", "email": "pa2@example.com", "name": "Panelist Two"},
                    ],
                }
            ),
        )
        http_mocker.get(
            request_2,
            json_response({"total_records": 1, "panelists": [{"id": "pa3", "email": "pa3@example.com", "name": "Panelist Three"}]}),
        )

        output = read_stream(_STREAM)

        assert output.errors == []
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        records = {record["id"]: record for record in record_data(output)}
        assert set(records) == {"pa1", "pa2", "pa3"}
        assert records["pa1"]["email"] == "pa1@example.com"
        assert records["pa1"]["webinar_id"] == WEBINAR_1["id"]
        assert records["pa2"]["webinar_id"] == WEBINAR_1["id"]
        assert records["pa3"]["webinar_id"] == WEBINAR_2["id"]
        http_mocker.assert_number_of_calls(request_1, 1)
        http_mocker.assert_number_of_calls(request_2, 1)

    @HttpMocker()
    def test_parent_400_user_not_licensed_completes_with_no_records(self, http_mocker: HttpMocker) -> None:
        assert_parent_400_skips_stream(http_mocker, _STREAM)

    @HttpMocker()
    def test_parent_403_fails_with_config_error(self, http_mocker: HttpMocker) -> None:
        assert_parent_403_fails_stream_with_config_error(http_mocker, _STREAM)
