# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime
from urllib.parse import parse_qs, urlparse

import pytest
import yaml

from .conftest import _YAML_FILE_PATH


def _load_manifest():
    with open(_YAML_FILE_PATH) as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize(
    "cursor_name,expected_step",
    [
        pytest.param("report_daily_incremental_sync", "P30D", id="default_daily_cursor_P30D"),
        pytest.param("report_daily_single_day_incremental_sync", "P1D", id="single_day_cursor_P1D"),
        pytest.param("report_hourly_incremental_sync", "P1D", id="hourly_cursor_P1D"),
    ],
)
def test_cursor_step_values(cursor_name, expected_step):
    manifest = _load_manifest()
    cursor_def = manifest["definitions"][cursor_name]
    assert cursor_def["step"] == expected_step


@pytest.mark.parametrize(
    "stream_name,expected_cursor_ref",
    [
        pytest.param(
            "ads_reports_daily_stream",
            "#/definitions/report_daily_single_day_incremental_sync",
            id="ads_reports_daily_uses_P1D",
        ),
        pytest.param(
            "ads_reports_by_country_daily_stream",
            "#/definitions/report_daily_single_day_incremental_sync",
            id="ads_reports_by_country_daily_uses_P1D",
        ),
    ],
)
def test_high_metric_streams_use_single_day_cursor(stream_name, expected_cursor_ref):
    manifest = _load_manifest()
    stream_def = manifest["definitions"][stream_name]
    assert "incremental_sync" in stream_def, f"{stream_name} must override incremental_sync"
    assert stream_def["incremental_sync"]["$ref"] == expected_cursor_ref


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("ad_groups_reports_daily_stream", id="ad_groups_reports_daily"),
        pytest.param("campaigns_reports_daily_stream", id="campaigns_reports_daily"),
        pytest.param("advertisers_reports_daily_stream", id="advertisers_reports_daily"),
    ],
)
def test_other_daily_streams_do_not_override_cursor(stream_name):
    manifest = _load_manifest()
    stream_def = manifest["definitions"][stream_name]
    assert "incremental_sync" not in stream_def, f"{stream_name} should not override incremental_sync (inherits P30D from base)"


def test_ads_reports_daily_requests_single_day_slices():
    config = {
        "access_token": "TOKEN",
        "start_date": "2024-01-01",
        "end_date": "2024-01-05",
        "environment": {"advertiser_id": "12345"},
    }

    import requests_mock as rm

    from airbyte_cdk.models import SyncMode
    from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
    from airbyte_cdk.test.catalog_builder import CatalogBuilder

    catalog = CatalogBuilder().with_stream("ads_reports_daily", SyncMode.incremental).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=[])

    with rm.Mocker() as m:
        m.get(
            "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
            json={
                "code": 0,
                "message": "ok",
                "data": {
                    "list": [],
                    "page_info": {"page": 1, "page_size": 1000, "total_page": 1, "total_number": 0},
                },
            },
        )
        list(source.read(logger=None, config=config, catalog=catalog, state=[]))

        report_requests = [h for h in m.request_history if "report/integrated/get" in h.path]
        assert len(report_requests) > 0, "Expected at least one report API request"

        for req in report_requests:
            params = parse_qs(urlparse(req.url).query)
            start = params.get("start_date", [None])[0]
            end = params.get("end_date", [None])[0]
            if start and end:
                start_dt = datetime.strptime(start, "%Y-%m-%d")
                end_dt = datetime.strptime(end, "%Y-%m-%d")
                delta = (end_dt - start_dt).days
                assert delta <= 2, f"Date range {start} to {end} spans {delta} days; expected <=2 days (P1D step)"


def test_error_40067_handler_in_manifest():
    manifest = _load_manifest()
    error_handler = manifest["definitions"]["requester"]["error_handler"]
    filters = error_handler["response_filters"]
    error_40067_filters = [f for f in filters if "40067" in f.get("predicate", "")]
    assert len(error_40067_filters) == 1, "Expected exactly one error handler for code 40067"
    handler = error_40067_filters[0]
    assert handler["action"] == "FAIL"
    assert "query size limit" in handler["error_message"].lower()
