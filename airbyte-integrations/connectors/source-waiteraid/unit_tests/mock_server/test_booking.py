# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


@pytest.mark.parametrize(
    "bookings",
    [
        [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "name": "Guest One"}, "status": "confirmed"},
            {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 102, "name": "Guest Two"}, "status": "cancelled"},
        ],
        [{"id": 9003, "date": "2026-09-05", "amount": 1, "guest": {"id": 103, "name": "Guest Three"}, "status": "confirmed"}],
        [],
    ],
    ids=["multiple-bookings", "single-booking", "no-bookings"],
)
def test_read_emits_individual_bookings(bookings: list[dict], requests_mock: requests_mock.Mocker) -> None:
    config = {"auth_hash": "test-auth-hash", "restid": "1234", "start_date": "2026-09-01"}
    manifest_path = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    if not manifest_path.exists():
        manifest_path = Path(__file__).resolve().parents[2] / "manifest.yaml"
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=config)
    logger = logging.getLogger("test_waiteraid")
    stream = source.discover(logger, config).streams[0]
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=stream,
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )
    requests_mock.post(
        "https://app.waiteraid.com/wa-api/searchBooking?date=2026-09-01&auth_hash=test-auth-hash&restid=1234",
        complete_qs=True,
        json={"status": "OK", "bookings": bookings},
    )

    messages = list(source.read(logger, config, catalog))
    records = [message.record for message in messages if message.type == Type.RECORD]

    assert [record.data for record in records] == bookings
    assert all(record.stream == "booking" for record in records)
    assert not [message for message in messages if message.type == Type.TRACE and message.trace.error]
    assert requests_mock.call_count == 1
