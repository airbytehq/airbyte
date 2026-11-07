# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the authenticated request path on `source-applovin-ads`.

Verifies that every HTTP request carries the Report Key as the `api_key`
request parameter and that a rejected key surfaces as a config error.
"""

from datetime import datetime, timezone
from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_BASE_URL = "https://r.applovin.com"
_CONFIG = {
    "api_key": "test-report-key",
    "start_date": datetime.now(timezone.utc).date().isoformat(),
}


def _read_stream(stream_name: str, expecting_exception: bool = False):
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, _CONFIG, catalog, expecting_exception=expecting_exception)


def test_api_key_is_sent_as_request_parameter():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/assetAnalyticsReport",
            json={
                "results": [
                    {
                        "asset_id": "123",
                        "campaign_id": "campaign-1",
                        "creative_set_id": "creative-set-1",
                        "impressions": "10",
                    }
                ]
            },
        )
        output = _read_stream("asset_report_daily")

    assert mocker.called
    for request in mocker.request_history:
        assert request.qs.get("api_key") == ["test-report-key"]
    assert len(output.records) >= 1


@pytest.mark.parametrize(
    ("stream_name", "endpoint"),
    [
        ("advertiser_report_hourly", "/report"),
        ("web_report_hourly", "/webReport"),
    ],
)
def test_hourly_streams_request_hour_breakdown_in_cohort_mode(stream_name, endpoint):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}{endpoint}",
            json={
                "results": [
                    {
                        "day": _CONFIG["start_date"],
                        "hour": "13",
                        "campaign_id_external": "campaign-1",
                        "creative_set_id": "creative-set-1",
                        "country": "us",
                        "platform": "web",
                        "placement_type": "BANNER",
                        "impressions": "10",
                    }
                ]
            },
        )
        output = _read_stream(stream_name)

    assert mocker.called
    for request in mocker.request_history:
        columns = request.qs["columns"][0].split(",")
        assert "day" in columns
        assert "hour" in columns
        assert request.qs["sort_hour"] == ["asc"]
        # Cohort mode, same as the daily streams.
        assert request.qs["day_column"] == ["day"]
    assert len(output.records) >= 1


def test_rejected_api_key_fails_as_config_error():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/assetAnalyticsReport", status_code=401, json={})
        output = _read_stream("asset_report_daily", expecting_exception=True)

    assert output.errors
    assert any(
        error.trace.error.failure_type == FailureType.config_error and "Report Key" in (error.trace.error.message or "")
        for error in output.errors
    )
