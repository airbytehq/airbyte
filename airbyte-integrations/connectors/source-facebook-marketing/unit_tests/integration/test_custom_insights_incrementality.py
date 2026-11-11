# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from urllib.parse import parse_qs

import freezegun
import pytest
from facebook_business import FacebookAdsApi, FacebookSession

from airbyte_cdk.models import SyncMode

from .config import ACCOUNT_ID, ConfigBuilder
from .utils import read_output


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level,custom_setting,expected_windows",
    [
        pytest.param(True, {}, ["1d_click", "7d_click", "28d_click", "1d_view", "incrementality"], id="inherit-top-level"),
        pytest.param(
            False, {"include_incrementality": True}, ["1d_click", "7d_click", "28d_click", "1d_view", "incrementality"], id="custom-opt-in"
        ),
        pytest.param(False, {"include_incrementality": False}, ["1d_click", "7d_click", "28d_click", "1d_view"], id="both-disabled"),
    ],
)
def test_custom_insights_incrementality_request(requests_mock, top_level, custom_setting, expected_windows):
    config = ConfigBuilder()
    config.build().update(
        {
            "include_incrementality": top_level,
            "custom_insights": [{"name": "Incrementality", "fields": ["spend"], **custom_setting}],
        }
    )
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}"
    insights_url = f"{base_url}/act_{ACCOUNT_ID}/insights"
    requests_mock.get(f"{base_url}/act_{ACCOUNT_ID}/", json={"id": f"act_{ACCOUNT_ID}", "timezone_name": "UTC"})
    requests_mock.get(
        insights_url,
        json={"data": []},
        headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
    )
    job_start = requests_mock.post(insights_url, json={"report_run_id": "report_123"})
    requests_mock.post(
        f"{base_url}/",
        json=[
            {
                "code": 200,
                "body": json.dumps(
                    {"id": "report_123", "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100}
                ),
            }
        ],
    )
    requests_mock.get(f"{base_url}/report_123/insights", json={"data": []})

    output = read_output(config, "custom_incrementality", SyncMode.incremental)

    assert not output.errors
    assert job_start.call_count == 1
    body = parse_qs(job_start.last_request.text)
    assert json.loads(body["action_attribution_windows"][0]) == expected_windows
