# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import WaiteraidRequestBuilder


def _read_booking(http_mocker: HttpMocker, bookings: list):
    config = ConfigBuilder().build()
    request = (
        WaiteraidRequestBuilder.booking_endpoint()
        .with_query_param("date", "2026-09-03")
        .with_query_param("auth_hash", "test-auth-hash")
        .with_query_param("restid", "12345")
        .build()
    )
    http_mocker.post(request, HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200))
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    output = read(get_source(config), config=config, catalog=catalog)
    http_mocker.assert_number_of_calls(request, 1)
    return output


@HttpMocker()
def test_full_refresh_emits_individual_bookings(http_mocker: HttpMocker = None):
    bookings = [
        {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "firstname": "Ada"}},
        {"id": 9002, "date": "2026-09-03", "amount": 4, "guest": {"id": 102, "firstname": "Grace"}},
        {"id": 9003, "date": "2026-09-03", "amount": 1, "guest": {"id": 103, "firstname": "Linus"}},
    ]
    output = _read_booking(http_mocker, bookings)
    records = [message.record.data for message in output.records]

    assert len(records) == 3
    assert {record["id"] for record in records} == {9001, 9002, 9003}
    assert {record["id"]: record for record in records} == {booking["id"]: booking for booking in bookings}
    assert all("status" not in record and "bookings" not in record for record in records)
    assert all(message.record.stream == "booking" for message in output.records)


@HttpMocker()
def test_empty_bookings_emits_no_records(http_mocker: HttpMocker = None):
    output = _read_booking(http_mocker, [])

    assert len(output.records) == 0
    assert not any(log.log.level == "ERROR" for log in output.logs)
