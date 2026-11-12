# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


class TestBooking(TestCase):
    @HttpMocker()
    def test_booking_emits_individual_bookings(self, http_mocker: HttpMocker):
        config = {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "123"}
        bookings = [
            {"id": 9001, "date": "2026-09-03", "amount": 2, "guest": {"id": 1}},
            {"id": 9002, "date": "2026-09-03", "amount": 3, "guest": {"id": 2}},
        ]
        http_mocker.post(
            HttpRequest(
                url="https://app.waiteraid.com/wa-api/searchBooking",
                query_params={"date": config["start_date"], "auth_hash": config["auth_hash"], "restid": config["restid"]},
            ),
            HttpResponse(body=json.dumps({"status": "OK", "bookings": bookings}), status_code=200),
        )

        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream("booking", SyncMode.full_refresh).build(),
        )

        assert output.errors == []
        records = [message.record.data for message in output.records]
        assert len(records) == 2
        assert [record["id"] for record in records] == [9001, 9002]
        assert records == bookings
        assert all("bookings" not in record and "status" not in record for record in records)
