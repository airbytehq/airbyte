# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time
from unit_tests.conftest import get_source
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.request_builder import NylasRequestBuilder
from unit_tests.mock_server.response_builder import records_response

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


@pytest.mark.parametrize("event_ids", [["event-1", "event-2"], []], ids=["records", "empty"])
@freeze_time("2026-09-04T00:00:00Z")
def test_inaccessible_calendar_does_not_fail_events(event_ids):
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        http_mocker.get(NylasRequestBuilder.grants(), records_response([{"id": "grant-1"}]))
        http_mocker.get(
            NylasRequestBuilder.calendars(),
            records_response([{"id": "holiday", "name": "Public holidays"}, {"id": "normal", "name": "Work"}]),
        )
        holiday_request = NylasRequestBuilder.events("holiday")
        normal_request = NylasRequestBuilder.events("normal")
        http_mocker.get(holiday_request, HttpResponse(body='{"error":{"type":"general","message":"Not Found"}}', status_code=404))
        http_mocker.get(
            normal_request,
            records_response([{"id": event_id, "updated_at": 1788307200} for event_id in event_ids]),
        )
        catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
        output = read(get_source(config), config=config, catalog=catalog)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == event_ids
        assert not any(log.log.level == "ERROR" for log in output.logs)
        assert any(
            "The calendar_id in the request is not accessible. Skipping this calendar's events." in log.log.message for log in output.logs
        )
        http_mocker.assert_number_of_calls(holiday_request, 1)
        http_mocker.assert_number_of_calls(normal_request, 1)
