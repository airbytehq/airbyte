# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"auth_hash": "test-hash", "restid": "1234", "start_date": "2026-09-01"}
MANIFEST = Path(__file__).parents[2] / "manifest.yaml"


def booking(booking_id: int, date: str) -> dict:
    return {
        "id": booking_id,
        "date": date,
        "amount": 2,
        "status": "booked",
        "guest": {"id": booking_id * 10, "firstname": "Ada", "lastname": "Lovelace"},
    }


def test_booking_read_emits_one_record_per_booking_from_bookings_array(http_mocker: HttpMocker) -> None:
    bookings = [booking(9001, "2026-09-03"), booking(9002, "2026-09-04"), booking(9003, "2026-09-05")]
    http_mocker.post(
        HttpRequest(
            "https://app.waiteraid.com/wa-api/searchBooking",
            query_params={"date": "2026-09-01", "auth_hash": "test-hash", "restid": "1234"},
        ),
        HttpResponse(json.dumps({"status": "OK", "bookings": bookings}), 200),
    )
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST), config=CONFIG, catalog=catalog, state=None)

    output = read(source, config=CONFIG, catalog=catalog)

    assert not output.errors
    assert [record.record.data for record in output.records] == bookings
