#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from urllib.parse import parse_qs

import freezegun
import pytest
from facebook_business import FacebookAdsApi, FacebookSession

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import read

from .config import NOW, ConfigBuilder
from .utils import catalog, encode_request_body, source


@freezegun.freeze_time(NOW.isoformat())
@pytest.mark.parametrize("global_incrementality", [None, False, True], ids=["global-default", "global-off", "global-on"])
@pytest.mark.parametrize("custom_incrementality", [None, False, True], ids=["custom-default", "custom-off", "custom-on"])
def test_custom_insights_read_includes_incrementality_when_enabled_at_either_level(
    requests_mock, global_incrementality, custom_incrementality
) -> None:
    config = ConfigBuilder().build()
    config["account_ids"] = ["123", "456"]
    insight = {"name": "Attribution", "level": "account", "fields": ["account_id", "actions"], "breakdowns": [], "action_breakdowns": []}
    if global_incrementality is not None:
        config["include_incrementality"] = global_incrementality
    if custom_incrementality is not None:
        insight["include_incrementality"] = custom_incrementality
    config["custom_insights"] = [insight]

    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}"
    job_requests = []

    def complete_jobs(request, context):
        batch = json.loads(parse_qs(request.text)["batch"][0])
        return [
            {
                "code": 200,
                "body": json.dumps(
                    {
                        "id": entry["relative_url"].strip("/"),
                        "async_status": "Job Completed",
                        "async_percent_completion": 100,
                    }
                ),
            }
            for entry in batch
        ]

    requests_mock.post(f"{base_url}/", json=complete_jobs)
    for account_id in config["account_ids"]:
        requests_mock.get(
            f"{base_url}/act_{account_id}/",
            json={"account_id": account_id, "id": f"act_{account_id}", "timezone_name": "Etc/UTC"},
        )
        requests_mock.get(
            f"{base_url}/act_{account_id}/insights",
            json={},
            headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
        )
        job_requests.append(requests_mock.post(f"{base_url}/act_{account_id}/insights", json={"report_run_id": f"report_{account_id}"}))
        requests_mock.get(
            f"{base_url}/report_{account_id}/insights",
            json={"data": [{"account_id": account_id, "date_start": "2023-01-01", "date_stop": "2023-01-01", "actions": []}]},
        )

    output = read(source(), config, catalog("custom_attribution", SyncMode.incremental, {}))

    assert sorted(record.record.data["account_id"] for record in output.records) == ["123", "456"]
    expected_windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if global_incrementality or custom_incrementality:
        expected_windows.append("incrementality")
    expected_body = {
        "level": "account",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["account_id", "actions"],
        "time_increment": 1,
        "action_attribution_windows": expected_windows,
        "time_range": {"since": "2023-01-01", "until": "2023-01-01"},
    }
    for account_id, job_request in zip(config["account_ids"], job_requests):
        assert job_request.call_count == 1
        request = job_request.last_request
        assert request.path == f"/{FacebookAdsApi.API_VERSION}/act_{account_id}/insights"
        assert request.qs == {"access_token": [config["access_token"]]}
        assert parse_qs(request.text) == parse_qs(encode_request_body(expected_body))
