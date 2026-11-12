# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"auth_hash": "test_auth_hash", "restid": "1234", "start_date": "2026-09-01"}


def _booking(booking_id: int, date: str, amount: int) -> dict[str, Any]:
    return {
        "id": booking_id,
        "date": date,
        "amount": amount,
        "status": "confirmed",
        "guest": {"id": booking_id * 10, "firstname": "Test", "lastname": f"Guest{booking_id}"},
    }


@pytest.mark.parametrize(
    "bookings",
    [
        pytest.param(
            [_booking(9001, "2026-09-03", 2), _booking(9002, "2026-09-04", 4), _booking(9003, "2026-09-05", 6)],
            id="several_bookings",
        ),
        pytest.param([], id="no_bookings"),
    ],
)
def test_read_emits_one_record_per_booking(bookings: list[dict[str, Any]]) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(
                url="https://app.waiteraid.com/wa-api/searchBooking",
                query_params={"date": "2026-09-01", "auth_hash": "test_auth_hash", "restid": "1234"},
            ),
            HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200),
        )

        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

    assert [record.record.data for record in output.records] == bookings
    assert not any(log.log.level == "ERROR" for log in output.logs)
