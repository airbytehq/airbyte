# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"
if not MANIFEST_PATH.exists():
    MANIFEST_PATH = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")

CONFIG = {"auth_hash": "test-auth-hash", "restid": "1234", "start_date": "2026-09-01"}
BOOKINGS = [
    {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 1001, "name": "Test Guest"}, "status": "1"},
    {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 1002, "name": "Another Guest"}, "status": "2"},
]


@pytest.mark.parametrize("use_definition", [False, True], ids=["runtime-stream", "stream-definition"])
@pytest.mark.parametrize("bookings", [BOOKINGS, BOOKINGS[:1], []], ids=["multiple-bookings", "single-booking", "no-bookings"])
def test_booking_records_are_extracted_from_response(
    bookings: list[dict], use_definition: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    manifest_path = MANIFEST_PATH
    if use_definition:
        manifest = yaml.safe_load(MANIFEST_PATH.read_text())
        manifest["streams"] = [manifest["definitions"]["streams"]["booking"]]
        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(yaml.safe_dump(manifest))
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=CONFIG)
    catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as http:
        request = http.post(
            "https://app.waiteraid.com/wa-api/searchBooking?date=2026-09-01&auth_hash=test-auth-hash&restid=1234",
            complete_qs=True,
            json={"status": "OK", "bookings": bookings},
        )
        output = read(source, CONFIG, catalog)

    assert not output.errors
    assert request.call_count == 1
    records = []
    for message in output.records:
        assert message.record is not None
        records.append(message.record.data)
    assert records == bookings
