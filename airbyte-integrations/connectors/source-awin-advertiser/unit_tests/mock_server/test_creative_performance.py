# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ADVERTISER_ID, BASE_URL, ConfigBuilder


_STREAM = "creative_performance"


@freezegun.freeze_time("2024-01-02T12:00:00Z")
class TestCreativePerformanceStream(TestCase):
    @HttpMocker()
    def test_requests_one_report_per_region_and_day(self, http_mocker: HttpMocker) -> None:
        for creative_id, (region, day) in enumerate(
            [("GB", "2024-01-01"), ("GB", "2024-01-02"), ("US", "2024-01-01"), ("US", "2024-01-02")], start=1
        ):
            http_mocker.get(
                HttpRequest(
                    url=f"{BASE_URL}/advertisers/{ADVERTISER_ID}/reports/creative",
                    query_params={
                        "startDate": day,
                        "endDate": day,
                        "region": region,
                        "dateType": "transaction",
                        "timezone": "UTC",
                    },
                ),
                HttpResponse(
                    body=json.dumps([{"creativeId": creative_id, "publisherId": 777, "region": region, "clicks": 5}]),
                    status_code=200,
                ),
            )
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
