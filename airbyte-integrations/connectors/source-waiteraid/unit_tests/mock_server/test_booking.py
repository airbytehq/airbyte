# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import get_source
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.request_builder import WaiteraidRequestBuilder
from unit_tests.mock_server.response_builder import WaiteraidResponseBuilder


@pytest.mark.parametrize(
    "bookings",
    [
        [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 101, "firstname": "Alex"}},
            {"id": 9002, "date": "2026-09-04", "amount": 4, "guest": {"id": 102, "firstname": "Sam"}},
        ],
        [],
    ],
    ids=["multiple-bookings", "empty-bookings"],
)
def test_read_emits_bookings_not_response_envelope(bookings: list[dict]) -> None:
    config = ConfigBuilder().build()
    request = (
        WaiteraidRequestBuilder.booking()
        .with_query_param("date", "2026-09-03")
        .with_query_param("auth_hash", "test-auth-hash")
        .with_query_param("restid", "42")
        .build()
    )
    with HttpMocker() as http_mocker:
        http_mocker.post(request, WaiteraidResponseBuilder().with_records(bookings).build())
        catalog = CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build()

        output = read(get_source(config), config=config, catalog=catalog)

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
        records = [message.record.data for message in output.records]
        assert [record.get("id") for record in records] == [booking["id"] for booking in bookings]
        assert len(records) == len(bookings)
        assert records == bookings
