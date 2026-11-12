# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize(
    "bookings",
    [
        pytest.param(
            [
                {
                    "id": 9001,
                    "date": "2026-09-03",
                    "amount": 2,
                    "guest": {"id": 101, "name": "Test Guest A"},
                    "status": "confirmed",
                },
                {
                    "id": 9002,
                    "date": "2026-09-04",
                    "amount": 4,
                    "guest": {"id": 102, "name": "Test Guest B"},
                    "status": "arrived",
                },
            ],
            id="multiple_bookings",
        ),
        pytest.param([], id="empty_bookings"),
    ],
)
def test_read_emits_bookings_not_response_envelope(bookings: list[dict]) -> None:
    config = {"auth_hash": "test-auth-hash", "restid": "1234", "start_date": "2026-09-01"}
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(
                url="https://app.waiteraid.com/wa-api/searchBooking",
                query_params={"auth_hash": config["auth_hash"], "restid": config["restid"], "date": config["start_date"]},
            ),
            HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings})),
        )

        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)

    assert [message.record.data for message in output.records] == bookings
    assert not any(message.log.level == "ERROR" for message in output.logs)
