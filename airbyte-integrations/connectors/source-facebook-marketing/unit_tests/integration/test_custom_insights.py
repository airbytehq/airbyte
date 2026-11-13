#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from urllib.parse import parse_qs, urlparse

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from freezegun import freeze_time
from source_facebook_marketing import SourceFacebookMarketing

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import read

from .config import ACCESS_TOKEN, ConfigBuilder
from .utils import catalog, encode_request_body


@freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize("global_flag", [None, False, True], ids=["global-omitted", "global-off", "global-on"])
@pytest.mark.parametrize("custom_flag", [None, False, True], ids=["custom-omitted", "custom-off", "custom-on"])
def test_custom_insights_incrementality_requests(requests_mock, global_flag: bool | None, custom_flag: bool | None) -> None:
    account_ids = ["123", "456"]
    fields = ["account_id", "ad_id", "date_start", "date_stop", "actions"]
    insight = {"name": "Attribution", "fields": fields, "breakdowns": [], "action_breakdowns": ["action_type"]}
    config = ConfigBuilder().with_account_ids(account_ids).build()
    if global_flag is not None:
        config["include_incrementality"] = global_flag
    if custom_flag is not None:
        insight["include_incrementality"] = custom_flag
    config["custom_insights"] = [insight]
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}"
    expected_records = []
    expected_windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if global_flag or custom_flag:
        expected_windows.append("incrementality")

    for account_id in account_ids:
        requests_mock.get(
            f"{base_url}/act_{account_id}/",
            json={"account_id": account_id, "id": f"act_{account_id}", "timezone_name": "Etc/UTC"},
        )
        requests_mock.get(
            f"{base_url}/act_{account_id}/insights",
            json={"data": []},
            headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
        )
        requests_mock.post(f"{base_url}/act_{account_id}/insights", json={"report_run_id": f"report_{account_id}"})
        action = {"action_type": "purchase", "value": "10"}
        expected_action = {"action_type": "purchase", "value": 10.0}
        if global_flag or custom_flag:
            action["incrementality"] = "2"
            expected_action["incrementality"] = 2.0
        record = {
            "account_id": account_id,
            "ad_id": f"ad_{account_id}",
            "date_start": "2023-01-01",
            "date_stop": "2023-01-01",
            "actions": [action],
        }
        expected_records.append({**record, "actions": [expected_action]})
        requests_mock.get(f"{base_url}/report_{account_id}/insights", json={"data": [record]})

    def complete_reports(request, context):
        batch = json.loads(parse_qs(request.text)["batch"][0])
        return [
            {
                "code": 200,
                "body": json.dumps(
                    {"id": item["relative_url"].strip("/"), "async_status": "Job Completed", "async_percent_completion": 100}
                ),
            }
            for item in batch
        ]

    requests_mock.post(f"{base_url}/", json=complete_reports)
    output = read(SourceFacebookMarketing(), config, catalog("custom_attribution", SyncMode.full_refresh, {}))

    job_requests = [request for request in requests_mock.request_history if request.method == "POST" and request.path.endswith("/insights")]
    assert len(job_requests) == 2
    for account_id, request in zip(account_ids, sorted(job_requests, key=lambda request: request.path)):
        assert request.path == f"/{FacebookAdsApi.API_VERSION}/act_{account_id}/insights"
        assert parse_qs(urlparse(request.url).query) == {"access_token": [ACCESS_TOKEN]}
        expected_body = {
            "level": "ad",
            "fields": fields,
            "breakdowns": [],
            "action_breakdowns": ["action_type"],
            "time_increment": 1,
            "time_range": {"since": "2023-01-01", "until": "2023-01-01"},
            "action_attribution_windows": expected_windows,
        }
        assert parse_qs(request.text) == parse_qs(encode_request_body(expected_body))
    assert sorted((message.record.data for message in output.records), key=lambda record: record["account_id"]) == expected_records
