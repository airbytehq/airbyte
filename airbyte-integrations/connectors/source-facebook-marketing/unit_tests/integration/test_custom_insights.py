#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from urllib.parse import parse_qs

import freezegun
import pytest

from airbyte_cdk.models import SyncMode

from .config import ACCOUNT_ID
from .request_builder import API_VERSION
from .utils import config, read_output


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize("include_incrementality", [True, False])
def test_custom_insights_inherit_top_level_incrementality(requests_mock, include_incrementality):
    config_builder = config()
    config_builder.build().update(
        {
            "include_incrementality": include_incrementality,
            "custom_insights": [{"name": "Incrementality", "fields": ["account_id", "date_start", "date_stop"], "breakdowns": []}],
        }
    )
    api_url = f"https://graph.facebook.com/{API_VERSION}/"
    requests_mock.get(f"{api_url}act_{ACCOUNT_ID}/", json={"id": f"act_{ACCOUNT_ID}", "timezone_name": "UTC"})
    insights_url = f"{api_url}act_{ACCOUNT_ID}/insights"
    requests_mock.get(
        insights_url,
        json={},
        headers={
            "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"})
        },
    )
    job_request = requests_mock.post(insights_url, json={"report_run_id": "report_run"})
    requests_mock.post(
        api_url,
        json=[
            {"body": json.dumps({"id": "job", "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100})}
        ],
    )
    requests_mock.get(f"{api_url}job/insights", json={"data": []})

    output = read_output(config_builder, "custom_incrementality", SyncMode.full_refresh)

    assert not output.records
    assert job_request.call_count == 1
    body = parse_qs(job_request.last_request.text)
    attribution_windows = json.loads(body["action_attribution_windows"][0])
    assert ("incrementality" in attribution_windows) is include_incrementality
