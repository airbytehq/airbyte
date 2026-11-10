# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import NylasRequestBuilder


class TestEvents(TestCase):
    @HttpMocker()
    def test_skips_inaccessible_calendar_and_reads_other_calendar(self, http_mocker: HttpMocker):
        http_mocker.get(
            NylasRequestBuilder("grants").build(),
            HttpResponse(body=json.dumps({"data": [{"id": "grant-1"}]})),
        )
        http_mocker.get(
            NylasRequestBuilder("grants/grant-1/calendars").build(),
            HttpResponse(body=json.dumps({"data": [{"id": "calendar-A"}, {"id": "calendar-B"}]})),
        )
        requests = {
            calendar: (
                NylasRequestBuilder("grants/grant-1/events")
                .with_query_param("calendar_id", calendar)
                .with_query_param("start", "1788220800")
                .with_query_param("end", "1788393600")
                .build()
            )
            for calendar in ("calendar-A", "calendar-B")
        }
        http_mocker.get(
            requests["calendar-A"],
            HttpResponse(status_code=404, body=json.dumps({"error": {"type": "general", "message": "Not Found"}})),
        )
        http_mocker.get(
            requests["calendar-B"],
            HttpResponse(body=json.dumps({"data": [{"id": "event-B", "updated_at": 1788307200}]})),
        )

        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
        output = read(get_source(config), config=config, catalog=catalog)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["event-B"]
        assert not [message for message in output.logs if message.log.level == Level.ERROR]
        http_mocker.assert_number_of_calls(requests["calendar-A"], 1)
        http_mocker.assert_number_of_calls(requests["calendar-B"], 1)
