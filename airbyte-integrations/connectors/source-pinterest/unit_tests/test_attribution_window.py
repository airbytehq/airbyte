#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import read_from_stream


_FROZEN_NOW = "2026-10-15 12:00:00+00:00"
_NOW = datetime(2026, 10, 15, tzinfo=timezone.utc)


def _date(days_ago: int) -> str:
    return (_NOW - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def _read_analytics_start_date(requests_mock, config, stream_name, state) -> str:
    requests_mock.get("https://api.pinterest.com/v5/ad_accounts", json={"items": [{"id": 123}]})
    requests_mock.get("https://api.pinterest.com/v5/ad_accounts/123/analytics", json=[])

    read_from_stream(config, stream_name, SyncMode.incremental, state=state)

    analytics_requests = [request for request in requests_mock.request_history if request.path.endswith("/analytics")]
    assert analytics_requests
    return analytics_requests[0].qs["start_date"][0]


def _read_report_start_dates(requests_mock, config, stream_name, state) -> list:
    report_download_url = "https://download.report"
    report_request_url = "https://api.pinterest.com/v5/ad_accounts/123/reports"
    request_bodies = []

    def match_json_body(request):
        raw = request.body.decode() if isinstance(request.body, (bytes, bytearray)) else request.body
        request_bodies.append(json.loads(raw))
        return True

    requests_mock.get("https://api.pinterest.com/v5/ad_accounts", json={"items": [{"id": 123}]})
    requests_mock.post(
        report_request_url,
        json={"report_status": "IN_PROGRESS", "token": "token", "message": ""},
        additional_matcher=match_json_body,
    )
    requests_mock.get(report_request_url, json={"report_status": "FINISHED", "url": report_download_url})
    requests_mock.get(report_download_url, json={"campaign_id": [{"metric": 1}]})

    read_from_stream(config, stream_name, SyncMode.incremental, state=state)

    assert request_bodies
    return [body["start_date"] for body in request_bodies]


@freeze_time(_FROZEN_NOW)
def test_analytics_stream_attribution_window_re_reads_past_days(requests_mock, test_config):
    test_config["attribution_window"] = 7
    state = StateBuilder().with_stream_state("ad_account_analytics", {"DATE": _date(10)}).build()

    first_slice_start = _read_analytics_start_date(requests_mock, test_config, "ad_account_analytics", state)

    assert first_slice_start == _date(17)


@pytest.mark.parametrize("attribution_window", [None, 0], ids=["absent", "zero"])
@freeze_time(_FROZEN_NOW)
def test_analytics_stream_without_attribution_window_starts_at_state(requests_mock, test_config, attribution_window):
    if attribution_window is not None:
        test_config["attribution_window"] = attribution_window
    state = StateBuilder().with_stream_state("ad_account_analytics", {"DATE": _date(10)}).build()

    first_slice_start = _read_analytics_start_date(requests_mock, test_config, "ad_account_analytics", state)

    assert first_slice_start == _date(10)


@freeze_time(_FROZEN_NOW)
def test_analytics_stream_attribution_window_clamped_to_stream_start_limit(requests_mock, test_config):
    test_config["attribution_window"] = 60
    state = StateBuilder().with_stream_state("ad_account_analytics", {"DATE": _date(85)}).build()

    first_slice_start = _read_analytics_start_date(requests_mock, test_config, "ad_account_analytics", state)

    assert first_slice_start >= _date(89)


@freeze_time(_FROZEN_NOW)
def test_report_stream_attribution_window_re_reads_past_days(requests_mock, test_config):
    test_config["attribution_window"] = 30
    state = StateBuilder().with_stream_state("campaign_analytics_report", {"DATE": _date(40)}).build()

    start_dates = _read_report_start_dates(requests_mock, test_config, "campaign_analytics_report", state)

    assert min(start_dates) == _date(70)


@freeze_time(_FROZEN_NOW)
def test_custom_report_attribution_window_re_reads_past_days(requests_mock, test_config):
    config = copy.deepcopy(test_config)
    config["attribution_window"] = 30
    config["custom_reports"] = [
        {
            "name": "ad_performance_report",
            "level": "AD_GROUP",
            "granularity": "DAY",
            "columns": ["ADVERTISER_ID", "AD_ACCOUNT_ID", "AD_GROUP_ID", "SPEND_IN_DOLLAR"],
            "click_window_days": 30,
            "engagement_window_days": 30,
            "view_window_days": 30,
            "conversion_report_time": "TIME_OF_AD_ACTION",
            "attribution_types": ["INDIVIDUAL"],
            "start_date": "2026-01-01",
        }
    ]
    state = StateBuilder().with_stream_state("custom_ad_performance_report", {"DATE": _date(40)}).build()

    start_dates = _read_report_start_dates(requests_mock, config, "custom_ad_performance_report", state)

    assert min(start_dates) == _date(70)


def test_spec_defines_attribution_window():
    manifest = yaml.safe_load((Path(__file__).parent.parent / "manifest.yaml").read_text())

    attribution_window = manifest["spec"]["connection_specification"]["properties"]["attribution_window"]

    assert attribution_window["type"] == "integer"
    assert attribution_window["default"] == 0
    assert attribution_window["minimum"] == 0
    assert attribution_window["maximum"] == 60
    assert "attribution_window" not in manifest["spec"]["connection_specification"].get("required", [])
