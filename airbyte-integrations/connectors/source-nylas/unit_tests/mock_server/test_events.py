# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import NylasRequestBuilder


def test_events_skips_inaccessible_calendar():
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    grants = NylasRequestBuilder.endpoint("/v3/grants").build()
    calendars = NylasRequestBuilder.endpoint("/v3/grants/grant-1/calendars").build()
    primary_events = (
        NylasRequestBuilder.endpoint("/v3/grants/grant-1/events")
        .with_query_param("calendar_id", "primary")
        .with_query_param("start", "1788220800")
        .with_query_param("end", "1788393600")
        .build()
    )
    holiday_events = (
        NylasRequestBuilder.endpoint("/v3/grants/grant-1/events")
        .with_query_param("calendar_id", "holiday")
        .with_query_param("start", "1788220800")
        .with_query_param("end", "1788393600")
        .build()
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(grants, HttpResponse(body=json.dumps({"data": [{"id": "grant-1"}]})))
        http_mocker.get(
            calendars,
            HttpResponse(body=json.dumps({"data": [{"id": "primary", "is_primary": True}, {"id": "holiday", "read_only": True}]})),
        )
        http_mocker.get(
            primary_events,
            HttpResponse(body=json.dumps({"data": [{"id": "primary-event", "updated_at": 1788220800}]})),
        )
        http_mocker.get(
            holiday_events,
            HttpResponse(
                body=json.dumps({"request_id": "request-404", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )

        output = read(get_source(config), config=config, catalog=catalog)

        http_mocker.assert_number_of_calls(primary_events, 1)
        http_mocker.assert_number_of_calls(holiday_events, 1)

    assert [record.record.data["id"] for record in output.records] == ["primary-event"]
    assert output.errors == []
    assert AirbyteStreamStatus.INCOMPLETE not in output.get_stream_statuses("events")
    assert output.get_stream_statuses("events")[-1] == AirbyteStreamStatus.COMPLETE
