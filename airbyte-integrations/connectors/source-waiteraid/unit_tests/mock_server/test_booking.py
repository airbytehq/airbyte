# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from ..conftest import get_source


CONFIG = {"auth_hash": "test-auth-hash", "restid": "1234", "start_date": "2026-09-01"}


def _search_booking_request() -> HttpRequest:
    return HttpRequest(
        "https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": "2026-09-01", "auth_hash": "test-auth-hash", "restid": "1234"},
    )


@pytest.mark.parametrize(
    "bookings",
    [
        pytest.param(
            [
                {"id": 9001, "date": "2026-09-03", "amount": 2, "status": "confirmed", "guest": {"id": 1, "name": "Ada"}},
                {"id": 9002, "date": "2026-09-04", "amount": 4, "status": "cancelled", "guest": {"id": 2, "name": "Linus"}},
            ],
            id="multiple_bookings",
        ),
        pytest.param([], id="no_bookings"),
    ],
)
def test_booking_emits_one_record_per_booking(bookings: list) -> None:
    with HttpMocker() as mocker:
        expected_request = _search_booking_request()
        mocker.post(expected_request, HttpResponse(json.dumps({"status": "OK", "bookings": bookings}), 200))

        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        output = read(get_source(CONFIG), CONFIG, catalog)

        assert [message.record.data for message in output.records] == bookings
        assert output.errors == []
        mocker.assert_number_of_calls(expected_request, 1)
