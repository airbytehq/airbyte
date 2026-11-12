#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any
from urllib.parse import parse_qs

import freezegun
import pytest
from facebook_business import FacebookAdsApi
from requests import PreparedRequest
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode

from .config import ACCESS_TOKEN, ACCOUNT_ID, ConfigBuilder
from .utils import encode_request_body, read_output


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "global_flag,custom_flag,expected_windows",
    [
        pytest.param(True, None, ["1d_click", "7d_click", "28d_click", "1d_view", "incrementality"], id="global_only"),
        pytest.param(True, False, ["1d_click", "7d_click", "28d_click", "1d_view", "incrementality"], id="global_with_custom_false"),
        pytest.param(False, True, ["1d_click", "7d_click", "28d_click", "1d_view", "incrementality"], id="custom_only"),
        pytest.param(True, True, ["1d_click", "7d_click", "28d_click", "1d_view", "incrementality"], id="both_enabled"),
        pytest.param(False, False, ["1d_click", "7d_click", "28d_click", "1d_view"], id="both_disabled"),
        pytest.param(None, None, ["1d_click", "7d_click", "28d_click", "1d_view"], id="defaults"),
    ],
)
def test_custom_insights_incrementality_requests(
    requests_mock: Mocker, global_flag: bool | None, custom_flag: bool | None, expected_windows: list[str]
) -> None:
    account_ids = [ACCOUNT_ID, "222222222222222"]
    fields = ["account_id", "ad_id", "actions", "date_start", "date_stop"]
    custom_insight: dict[str, Any] = {"name": "Attribution", "fields": fields, "breakdowns": [], "action_breakdowns": []}
    if custom_flag is not None:
        custom_insight["include_incrementality"] = custom_flag
    config = ConfigBuilder().with_account_ids(account_ids)
    config.build()["custom_insights"] = [custom_insight]
    if global_flag is not None:
        config.build()["include_incrementality"] = global_flag

    base_url = f"https://graph.facebook.com/{FacebookAdsApi.API_VERSION}/"

    def job_status(request: PreparedRequest, context: Any) -> list[dict]:
        batch = json.loads(parse_qs(request.body)["batch"][0])
        return [
            {
                "code": 200,
                "body": json.dumps(
                    {
                        "id": job["relative_url"].strip("/"),
                        "async_status": "Job Completed",
                        "async_percent_completion": 100,
                    }
                ),
            }
            for job in batch
        ]

    requests_mock.post(base_url, json=job_status)
    job_requests = []
    for account_id in account_ids:
        requests_mock.get(
            f"{base_url}act_{account_id}/",
            json={"account_id": account_id, "id": f"act_{account_id}", "timezone_name": "Etc/UTC"},
        )
        requests_mock.get(
            f"{base_url}act_{account_id}/insights",
            json={"data": []},
            headers={
                "x-fb-ads-insights-throttle": json.dumps(
                    {"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}
                )
            },
        )
        job_requests.append(requests_mock.post(f"{base_url}act_{account_id}/insights", json={"report_run_id": f"report_{account_id}"}))
        requests_mock.get(
            f"{base_url}report_{account_id}/insights",
            json={
                "data": [
                    {
                        "account_id": account_id,
                        "ad_id": f"ad_{account_id}",
                        "date_start": "2023-01-01",
                        "date_stop": "2023-01-01",
                        "actions": [{"action_type": "purchase", "value": "5"}],
                    }
                ]
            },
        )

    output = read_output(config, "custom_attribution", SyncMode.incremental)

    ad_ids = []
    for record in output.records:
        assert record.record is not None
        ad_ids.append(record.record.data["ad_id"])
    assert sorted(ad_ids) == [f"ad_{account_id}" for account_id in account_ids]
    for account_id, job_request in zip(account_ids, job_requests):
        assert job_request.call_count == 1
        request = job_request.last_request
        assert request is not None
        assert request.path == f"/{FacebookAdsApi.API_VERSION}/act_{account_id}/insights"
        assert request.qs == {"access_token": [ACCESS_TOKEN]}
        expected_body = {
            "level": "ad",
            "action_breakdowns": [],
            "breakdowns": [],
            "fields": fields,
            "time_increment": 1,
            "action_attribution_windows": expected_windows,
            "time_range": {"since": "2023-01-01", "until": "2023-01-01"},
        }
        assert parse_qs(request.body) == parse_qs(encode_request_body(expected_body))
