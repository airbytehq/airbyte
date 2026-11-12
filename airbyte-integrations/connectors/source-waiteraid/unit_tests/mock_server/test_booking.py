# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"auth_hash": "test-hash", "restid": "1234", "start_date": "2026-09-01"}


def booking(booking_id: int, date: str, amount: int) -> dict:
    return {
        "id": booking_id,
        "date": date,
        "amount": amount,
        "status": "confirmed",
        "guest": {"id": booking_id * 10, "firstname": "Ada", "lastname": "Lovelace"},
    }


def test_booking_read_emits_one_record_per_booking() -> None:
    bookings = [booking(9001, "2026-09-03", 2), booking(9002, "2026-09-04", 4)]
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=[],
    )

    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(
                "https://app.waiteraid.com/wa-api/searchBooking",
                query_params={"date": "2026-09-01", "auth_hash": "test-hash", "restid": "1234"},
            ),
            HttpResponse(json.dumps({"status": "OK", "bookings": bookings})),
        )
        output = read(source, config=CONFIG, catalog=catalog)

    # The API wraps bookings in {"status": ..., "bookings": [...]}; each booking must be its own record.
    assert [record.record.data for record in output.records] == bookings
