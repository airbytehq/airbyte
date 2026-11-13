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


_STREAM = "creative_performance"


def _request(region: str, day: str) -> HttpRequest:
    return HttpRequest(
        url=f"{BASE_URL}/advertisers/{ADVERTISER_ID}/reports/creative",
        query_params={"startDate": day, "endDate": day, "region": region, "dateType": "transaction", "timezone": "UTC"},
    )


def _response(rows: list) -> HttpResponse:
    return HttpResponse(body=json.dumps(rows), status_code=200)


def _row(region: str, creative_id: int) -> dict:
    return {"creativeId": creative_id, "publisherId": 777, "region": region, "clicks": 5}


@freezegun.freeze_time("2024-01-02T12:00:00Z")
class TestCreativePerformanceStream(TestCase):
    @HttpMocker()
    def test_requests_one_report_per_region_and_day(self, http_mocker: HttpMocker) -> None:
        for creative_id, (region, day) in enumerate(
            [("GB", "2024-01-01"), ("GB", "2024-01-02"), ("US", "2024-01-01"), ("US", "2024-01-02")], start=1
        ):
            http_mocker.get(_request(region, day), _response([_row(region, creative_id)]))
        config = ConfigBuilder().with_regions(["GB", "US"]).build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()

        output = read(get_source(config=config, catalog=catalog), config, catalog)

        assert not output.errors
        assert sorted((r.record.data["region"], r.record.data["date"], r.record.data["creativeId"]) for r in output.records) == [
            ("GB", "2024-01-01", 1),
            ("GB", "2024-01-02", 2),
            ("US", "2024-01-01", 3),
            ("US", "2024-01-02", 4),
        ]

    @HttpMocker()
    def test_sends_no_requests_when_no_regions_are_configured(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()

        output = read(get_source(config=config, catalog=catalog), config, catalog)

        assert not output.errors
        assert output.records == []

    @HttpMocker()
    def test_records_carry_the_requested_region(self, http_mocker: HttpMocker) -> None:
        for region in ("GB", "US"):
            http_mocker.get(_request(region, "2024-01-02"), _response([{"creativeId": 1, "publisherId": 777, "clicks": 5}]))
        config = ConfigBuilder().with_start_date("2024-01-02").with_regions(["GB", "US"]).build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()

        output = read(get_source(config=config, catalog=catalog), config, catalog)

        assert not output.errors
        assert sorted((r.record.data["region"], r.record.data["creativeId"]) for r in output.records) == [("GB", 1), ("US", 1)]

    @HttpMocker()
    def test_second_read_resumes_every_region_from_the_emitted_state_minus_lookback(self, http_mocker: HttpMocker) -> None:
        for creative_id, (region, day) in enumerate(
            [(region, day) for region in ("GB", "US") for day in ("2024-01-01", "2024-01-02", "2024-01-03")], start=1
        ):
            http_mocker.get(_request(region, day), _response([_row(region, creative_id)]))
        config = ConfigBuilder().with_lookback_days(1).with_regions(["GB", "US"]).build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()

        first = read(get_source(config=config, catalog=catalog), config, catalog)
        state = StateBuilder().with_stream_state(_STREAM, first.most_recent_state.stream_state.__dict__).build()
        with freezegun.freeze_time("2024-01-03T12:00:00Z"):
            second = read(get_source(config=config, catalog=catalog, state=state), config, catalog, state)

        assert not first.errors and not second.errors
        assert first.most_recent_state.stream_state.__dict__["state"] == {"date": "2024-01-02"}
        # lookback_days=1: the second read starts every region one day before the emitted state.
        assert sorted((r.record.data["region"], r.record.data["date"]) for r in second.records) == [
            ("GB", "2024-01-01"),
            ("GB", "2024-01-02"),
            ("GB", "2024-01-03"),
            ("US", "2024-01-01"),
            ("US", "2024-01-02"),
            ("US", "2024-01-03"),
        ]
        assert second.most_recent_state.stream_state.__dict__["state"] == {"date": "2024-01-03"}

    @HttpMocker()
    def test_region_with_no_rows_is_not_reread_from_start_date_on_next_sync(self, http_mocker: HttpMocker) -> None:
        def response(region: str) -> HttpResponse:
            return _response([] if region == "IT" else [_row(region, 1)])

        it_start_day = _request("IT", "2024-01-01")
        http_mocker.get(it_start_day, response("IT"))
        http_mocker.get(_request("GB", "2024-01-01"), response("GB"))
        for region in ("GB", "IT"):
            http_mocker.get(_request(region, "2024-01-02"), [response(region), response(region)])
            http_mocker.get(_request(region, "2024-01-03"), response(region))
        config = ConfigBuilder().with_regions(["GB", "IT"]).build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()

        first = read(get_source(config=config, catalog=catalog), config, catalog)
        state = StateBuilder().with_stream_state(_STREAM, first.most_recent_state.stream_state.__dict__).build()
        with freezegun.freeze_time("2024-01-03T12:00:00Z"):
            second = read(get_source(config=config, catalog=catalog, state=state), config, catalog, state)

        assert not first.errors and not second.errors
        assert sorted((r.record.data["region"], r.record.data["date"]) for r in second.records) == [
            ("GB", "2024-01-02"),
            ("GB", "2024-01-03"),
        ]
        http_mocker.assert_number_of_calls(it_start_day, 1)
