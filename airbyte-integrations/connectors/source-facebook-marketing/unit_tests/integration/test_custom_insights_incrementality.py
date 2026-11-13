#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from urllib.parse import parse_qs, urlparse

import freezegun
import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import read

from .config import ACCESS_TOKEN
from .utils import catalog, config, source


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize("source_enabled", [None, False, True], ids=["source_omitted", "source_disabled", "source_enabled"])
@pytest.mark.parametrize("custom_enabled", [None, False, True], ids=["custom_omitted", "custom_disabled", "custom_enabled"])
def test_custom_insights_request_incrementality(requests_mock: Mocker, source_enabled: bool | None, custom_enabled: bool | None) -> None:
    account_ids = ["111111111111111", "222222222222222"]
    fields = ["account_id", "ad_id", "date_start", "date_stop", "actions"]
    custom_insight = {"name": "Lift", "fields": fields, "time_increment": 1}
    connector_config = config().with_account_ids(account_ids).build()
    connector_config["custom_insights"] = [custom_insight]
    if source_enabled is not None:
        connector_config["include_incrementality"] = source_enabled
    if custom_enabled is not None:
        custom_insight["include_incrementality"] = custom_enabled

    windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if source_enabled or custom_enabled:
        windows.append("incrementality")
    job_body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": fields,
        "time_increment": 1,
        "action_attribution_windows": windows,
        "time_range": {"since": "2023-01-01", "until": "2023-01-01"},
    }
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}"
    expected_records = []
    for account_id in account_ids:
        report_id = f"report_{account_id}"
        requests_mock.get(
            f"{base_url}/act_{account_id}/",
            json={"account_id": account_id, "id": f"act_{account_id}", "timezone_name": "Etc/UTC"},
        )
        requests_mock.get(
            f"{base_url}/act_{account_id}/insights",
            json={},
            headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
        )
        requests_mock.post(
            f"{base_url}/act_{account_id}/insights",
            json={"report_run_id": report_id},
        )
        action = {"action_type": "purchase", "value": "10"}
        if source_enabled or custom_enabled:
            action["incrementality"] = "2"
        record = {
            "account_id": account_id,
            "ad_id": f"ad_{account_id}",
            "date_start": "2023-01-01",
            "date_stop": "2023-01-01",
            "actions": [action],
        }
        expected_action = {"action_type": "purchase", "value": 10.0}
        if source_enabled or custom_enabled:
            expected_action["incrementality"] = 2.0
        expected_records.append({**record, "actions": [expected_action]})
        requests_mock.get(
            f"{base_url}/{report_id}/insights",
            json={"data": [record]},
        )

    def completed_jobs(request, context):
        return [
            {"body": json.dumps({"id": job["relative_url"].rstrip("/"), "async_status": "Job Completed", "async_percent_completion": 100})}
            for job in json.loads(parse_qs(request.text)["batch"][0])
        ]

    requests_mock.post(f"{base_url}/", json=completed_jobs)
    output = read(source(), connector_config, catalog("custom_lift", SyncMode.incremental, {}))

    job_requests = [request for request in requests_mock.request_history if request.method == "POST" and "/act_" in request.path]
    assert sorted(request.path for request in job_requests) == [
        f"/{FacebookAdsApi.API_VERSION}/act_{account_id}/insights" for account_id in account_ids
    ]
    for request in job_requests:
        assert parse_qs(urlparse(request.url).query) == {"access_token": [ACCESS_TOKEN]}
        body = {key: values[0] for key, values in parse_qs(request.text).items()}
        decoded_body = {key: value if key == "level" else json.loads(value) for key, value in body.items()}
        assert decoded_body == job_body
    assert sorted((message.record.data for message in output.records), key=lambda record: record["account_id"]) == expected_records
