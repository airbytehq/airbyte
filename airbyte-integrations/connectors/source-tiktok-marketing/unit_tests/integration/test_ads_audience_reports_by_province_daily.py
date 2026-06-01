# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import re
from urllib.parse import parse_qs, urlparse

import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read

from ..conftest import get_source
from .config_builder import ConfigBuilder


def test_ads_audience_reports_by_province_daily_uses_single_day_report_windows():
    config = ConfigBuilder().with_end_date("2024-01-03").build()
    catalog = CatalogBuilder().with_stream(name="ads_audience_reports_by_province_daily", sync_mode=SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/",
            json={"code": 0, "message": "ok", "data": {"list": [{"advertiser_id": "872746382648"}]}},
        )
        mocker.get(
            re.compile(r"https://business-api\.tiktok\.com/open_api/v1\.3/report/integrated/get/.*"),
            json={"code": 0, "message": "ok", "data": {"list": []}},
        )

        output = read(get_source(config=config), config, catalog)

    assert len(output.records) == 0
    report_requests = [request for request in mocker.request_history if "report/integrated/get" in request.url]
    parsed_requests = [parse_qs(urlparse(request.url).query) for request in report_requests]
    windows = {(request["start_date"][0], request["end_date"][0]) for request in parsed_requests}

    assert len(report_requests) == 2
    assert windows == {("2024-01-01", "2024-01-01"), ("2024-01-02", "2024-01-03")}
    for request in parsed_requests:
        assert request["report_type"][0] == "AUDIENCE"
        assert request["data_level"][0] == "AUCTION_AD"
        assert json.loads(request["dimensions"][0]) == ["ad_id", "stat_time_day", "province_id"]
        assert len(json.loads(request["metrics"][0])) == 48
