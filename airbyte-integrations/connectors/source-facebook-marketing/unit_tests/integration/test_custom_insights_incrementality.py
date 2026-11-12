#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from urllib.parse import parse_qs

import freezegun
import pytest
from facebook_business.api import FacebookAdsApi

from airbyte_cdk.models import SyncMode

from .config import ACCOUNT_ID
from .utils import config, read_output


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level,per_insight,enabled",
    [(True, None, True), (False, True, True), (False, None, False), (True, False, True)],
)
@pytest.mark.parametrize("empty", [False, True])
def test_custom_insight_incrementality_request(requests_mock, top_level, per_insight, enabled, empty):
    config_builder = config()
    custom_insight = {"name": "Incrementality", "fields": ["actions"], "breakdowns": [], "action_breakdowns": []}
    if per_insight is not None:
        custom_insight["include_incrementality"] = per_insight
    config_builder.build().update(include_incrementality=top_level, custom_insights=[custom_insight])
    record = {
        "date_start": "2023-01-01",
        "date_stop": "2023-01-01",
        "actions": [{"action_type": "purchase", "value": "2", "incrementality": "1"}],
    }
    records = [] if empty else [record]
    base_url = f"https://graph.facebook.com/{FacebookAdsApi.API_VERSION}/"
    insights_url = f"{base_url}act_{ACCOUNT_ID}/insights"
    requests_mock.get(f"{base_url}act_{ACCOUNT_ID}/", json={"id": f"act_{ACCOUNT_ID}", "timezone_name": "Etc/UTC"})
    requests_mock.get(
        insights_url,
        json={"data": []},
        headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
    )
    requests_mock.post(insights_url, json={"report_run_id": "report"})
    requests_mock.post(
        base_url,
        json=[
            {"body": json.dumps({"id": "job", "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100})}
        ],
    )
    requests_mock.get(f"{base_url}job/insights", json={"data": records})

    output = read_output(config_builder, "custom_incrementality", SyncMode.full_refresh)

    job_requests = [request for request in requests_mock.request_history if request.method == "POST" and "/insights?" in request.url]
    assert len(job_requests) == 1
    params = parse_qs(job_requests[0].body)
    windows = json.loads(params["action_attribution_windows"][0])
    expected_windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if enabled:
        expected_windows.append("incrementality")
    assert windows == expected_windows
    assert len(output.records) == len(records)
    if records:
        assert output.records[0].record.data["actions"] == [{"action_type": "purchase", "value": 2.0, "incrementality": 1.0}]
