# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


class TestEvents(TestCase):
    @HttpMocker()
    def test_events_skips_calendar_not_found(self, http_mocker: HttpMocker):
        config = {
            "api_key": "test-api-key",
            "api_server": "us",
            "start_date": "2026-09-01T00:00:00Z",
            "end_date": "2026-09-03T00:00:00Z",
        }
        base_url = "https://api.us.nylas.com/v3/grants"
        http_mocker.get(
            HttpRequest(url=base_url, query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": "grant"}]})),
        )
        http_mocker.get(
            HttpRequest(url=f"{base_url}/grant/calendars", query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": "holiday_cal"}, {"id": "ok_cal"}]})),
        )
        holiday_request = HttpRequest(
            url=f"{base_url}/grant/events",
            query_params={"limit": "50", "calendar_id": "holiday_cal", "start": "1788220800", "end": "1788393600"},
        )
        ok_request = HttpRequest(
            url=f"{base_url}/grant/events",
            query_params={"limit": "50", "calendar_id": "ok_cal", "start": "1788220800", "end": "1788393600"},
        )
        http_mocker.get(
            holiday_request,
            HttpResponse(
                body=json.dumps({"request_id": "request-404", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http_mocker.get(
            ok_request,
            HttpResponse(
                body=json.dumps({"data": [{"id": "event-1", "updated_at": 1788220801}, {"id": "event-2", "updated_at": 1788220802}]})
            ),
        )

        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream("events", SyncMode.incremental).build(),
        )

        assert output.errors == []
        assert output.get_stream_statuses("events")[-1] == AirbyteStreamStatus.COMPLETE
        assert sorted(message.record.data["id"] for message in output.records) == ["event-1", "event-2"]
        http_mocker.assert_number_of_calls(holiday_request, 1)
        http_mocker.assert_number_of_calls(ok_request, 1)
