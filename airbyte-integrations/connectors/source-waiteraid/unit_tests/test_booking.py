# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from urllib.parse import parse_qs, urlencode

import pytest
from conftest import get_source

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, SyncMode, Type


@pytest.mark.parametrize("booking_ids", [[9001, 9002], []], ids=["two_bookings", "empty_bookings"])
def test_booking_read(requests_mock, booking_ids):
    config = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "42"}
    params = {"date": config["start_date"], "auth_hash": config["auth_hash"], "restid": config["restid"]}
    bookings = [
        {"id": booking_id, "date": "2026-09-03", "amount": 2, "guest": {"id": booking_id + 100, "name": "Test Guest"}}
        for booking_id in booking_ids
    ]
    request = requests_mock.post(
        f"https://app.waiteraid.com/wa-api/searchBooking?{urlencode(params)}",
        complete_qs=True,
        json={"status": "OK", "bookings": bookings},
    )
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="booking", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode="append",
            )
        ]
    )
    source = get_source(config, catalog)
    messages = list(source.read(logging.getLogger("test"), config, catalog, state=[]))
    assert request.call_count == 1
    assert request.last_request.method == "POST"
    assert request.last_request.path == "/wa-api/searchBooking"
    assert parse_qs(request.last_request.query) == {key: [value] for key, value in params.items()}
    records = [message.record.data for message in messages if message.type == Type.RECORD]
    assert len(records) == len(bookings)
    assert [record["id"] for record in records] == booking_ids
    assert records == bookings
