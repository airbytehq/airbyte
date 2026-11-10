# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ADVERTISER_ID, BASE_URL, ConfigBuilder


_STREAM = "publisher_performance"


def _request(day: str) -> HttpRequest:
    return HttpRequest(
        url=f"{BASE_URL}/advertisers/{ADVERTISER_ID}/reports/publisher",
        query_params={"startDate": day, "endDate": day, "dateType": "transaction", "timezone": "UTC"},
    )


def _response(publisher_id: int) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(
            [{"publisherId": publisher_id, "publisherName": f"Publisher {publisher_id}", "region": "GB", "currency": "GBP", "clicks": 10}]
        ),
        status_code=200,
    )


@freezegun.freeze_time("2024-01-03T12:00:00Z")
class TestPublisherPerformanceStream(TestCase):
    @HttpMocker()
    def test_full_refresh_requests_one_report_per_day_and_adds_date(self, http_mocker: HttpMocker) -> None:
        for publisher_id, day in enumerate(["2024-01-01", "2024-01-02", "2024-01-03"], start=1):
            http_mocker.get(_request(day), _response(publisher_id))
        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()

        output = read(get_source(config=config, catalog=catalog), config, catalog)

        assert not output.errors
        assert sorted((r.record.data["date"], r.record.data["publisherId"]) for r in output.records) == [
            ("2024-01-01", 1),
            ("2024-01-02", 2),
            ("2024-01-03", 3),
        ]

    @HttpMocker()
    def test_incremental_read_resumes_from_state_with_lookback(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request("2024-01-02"), _response(2))
        http_mocker.get(_request("2024-01-03"), _response(3))
        config = ConfigBuilder().with_lookback_days(1).build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
        state = StateBuilder().with_stream_state(_STREAM, {"date": "2024-01-03"}).build()

        output = read(get_source(config=config, catalog=catalog, state=state), config, catalog, state)

        assert not output.errors
        assert sorted((r.record.data["date"], r.record.data["publisherId"]) for r in output.records) == [
            ("2024-01-02", 2),
            ("2024-01-03", 3),
        ]
        assert output.most_recent_state.stream_state.__dict__["date"] == "2024-01-03"
