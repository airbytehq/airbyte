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
    def test_events_skips_inaccessible_subscribed_calendar(self, http_mocker: HttpMocker) -> None:
        config = {
            "api_key": "k",
            "api_server": "us",
            "start_date": "2026-09-01T00:00:00Z",
            "end_date": "2026-09-03T00:00:00Z",
        }
        base_url = "https://api.us.nylas.com/v3/grants"
        http_mocker.get(
            HttpRequest(base_url, query_params={"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": "grant-1"}]}), 200),
        )
        http_mocker.get(
            HttpRequest(f"{base_url}/grant-1/calendars", query_params={"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": "holidays", "read_only": True}, {"id": "normal", "read_only": False}]}), 200),
        )
        requests = {
            calendar_id: HttpRequest(
                f"{base_url}/grant-1/events",
                query_params={"calendar_id": calendar_id, "limit": "50", "start": "1788220800", "end": "1788393600"},
            )
            for calendar_id in ("holidays", "normal")
        }
        http_mocker.get(
            requests["holidays"],
            HttpResponse(json.dumps({"request_id": "request-1", "error": {"type": "general", "message": "Not Found"}}), 404),
        )
        http_mocker.get(
            requests["normal"],
            HttpResponse(json.dumps({"data": [{"id": "event-1", "calendar_id": "normal", "updated_at": 1788307200}]}), 200),
        )

        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream("events", SyncMode.incremental).build(),
        )

        assert [message.record.data["id"] for message in output.records] == ["event-1"]
        for request in requests.values():
            http_mocker.assert_number_of_calls(request, 1)
        assert output.errors == []
        assert AirbyteStreamStatus.INCOMPLETE not in output.get_stream_statuses("events")
        assert AirbyteStreamStatus.COMPLETE in output.get_stream_statuses("events")
