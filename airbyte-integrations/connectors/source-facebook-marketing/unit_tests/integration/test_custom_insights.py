#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from urllib.parse import parse_qs

import freezegun
import pytest
from facebook_business import FacebookAdsApi
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode

from .config import ACCESS_TOKEN, NOW
from .utils import config, encode_request_body, read_output


@pytest.mark.parametrize(
    "top_level,custom,expected_incrementality",
    [
        pytest.param(True, None, True, id="inherit_when_omitted"),
        pytest.param(True, False, True, id="inherit_when_false"),
        pytest.param(True, True, True, id="both_enabled"),
        pytest.param(False, True, True, id="custom_only"),
        pytest.param(False, False, False, id="both_disabled"),
        pytest.param(None, None, False, id="defaults"),
    ],
)
@freezegun.freeze_time(NOW.isoformat())
def test_custom_insights_incrementality_requests(
    requests_mock: Mocker, top_level: bool | None, custom: bool | None, expected_incrementality: bool
) -> None:
    account_ids = ["111111111111111", "222222222222222"]
    config_builder = config().with_account_ids(account_ids)
    custom_insight = {"name": "IncrementalityInsights", "fields": ["account_id", "date_start", "actions"], "breakdowns": []}
    if custom is not None:
        custom_insight["include_incrementality"] = custom
    config_builder.build()["custom_insights"] = [custom_insight]
    if top_level is not None:
        config_builder.build()["include_incrementality"] = top_level

    base_url = f"https://graph.facebook.com/{FacebookAdsApi.API_VERSION}"
    for account_id in account_ids:
        requests_mock.get(
            f"{base_url}/act_{account_id}/",
            json={"account_id": account_id, "id": f"act_{account_id}", "timezone_name": "Etc/UTC"},
        )
        requests_mock.get(
            f"{base_url}/act_{account_id}/insights",
            json={},
            headers={
                "x-fb-ads-insights-throttle": json.dumps(
                    {"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}
                )
            },
        )
        requests_mock.post(f"{base_url}/act_{account_id}/insights", json={"report_run_id": account_id})
        requests_mock.get(
            f"{base_url}/{account_id}/insights",
            json={
                "data": [
                    {
                        "account_id": account_id,
                        "date_start": "2023-01-01",
                        "date_stop": "2023-01-01",
                        "actions": [{"action_type": "purchase", "value": "3"}],
                    }
                ]
            },
        )

    def completed_jobs(request, context):
        batch = json.loads(parse_qs(request.text)["batch"][0])
        return [
            {
                "body": json.dumps(
                    {
                        "id": item["relative_url"].strip("/"),
                        "account_id": item["relative_url"].strip("/"),
                        "async_status": "Job Completed",
                        "async_percent_completion": 100,
                    }
                )
            }
            for item in batch
        ]

    requests_mock.post(base_url + "/", json=completed_jobs)
    output = read_output(config_builder, "custom_incrementality_insights", SyncMode.incremental)

    creation_requests = [
        request for request in requests_mock.request_history if request.method == "POST" and request.path.endswith("/insights")
    ]
    assert sorted(request.path for request in creation_requests) == [
        f"/{FacebookAdsApi.API_VERSION}/act_{account_id}/insights" for account_id in account_ids
    ]
    expected_windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if expected_incrementality:
        expected_windows.append("incrementality")
    expected_body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["account_id", "date_start", "actions"],
        "time_increment": 1,
        "action_attribution_windows": expected_windows,
        "time_range": {"since": "2023-01-01", "until": "2023-01-01"},
    }
    for request in creation_requests:
        assert parse_qs(request.query) == {"access_token": [ACCESS_TOKEN]}
        body = parse_qs(request.text)
        assert json.loads(body["action_attribution_windows"][0]) == expected_windows
        assert body == parse_qs(encode_request_body(expected_body))
    assert sorted(record.record.data["account_id"] for record in output.records) == account_ids
