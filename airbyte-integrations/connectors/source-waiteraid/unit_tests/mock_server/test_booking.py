# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


MANIFEST_PATH = Path(__file__).parents[2] / "manifest.yaml"
CONFIG = {"auth_hash": "test-hash", "restid": "1234", "start_date": "2026-09-01"}


def _search_booking_request() -> HttpRequest:
    return HttpRequest(
        "https://app.waiteraid.com/wa-api/searchBooking",
        query_params={"date": "2026-09-01", "auth_hash": "test-hash", "restid": "1234"},
    )


def _booking(booking_id: int, date: str, amount: int) -> dict:
    return {"id": booking_id, "date": date, "amount": amount, "guest": {"id": booking_id * 10, "name": f"Guest {booking_id}"}}


def test_full_refresh_emits_one_record_per_booking() -> None:
    bookings = [_booking(9001, "2026-09-03", 2), _booking(9002, "2026-09-04", 4)]
    with HttpMocker() as http_mocker:
        http_mocker.post(
            _search_booking_request(),
            HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200),
        )
        source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=CONFIG, catalog=None, state=None)
        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        output = read(source, CONFIG, catalog)

    # searchBooking wraps bookings in {"status": ..., "bookings": [...]}; each booking must be its own record.

    assert [record.record.data for record in output.records] == bookings
