#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any
from urllib.parse import parse_qs

import pytest
from facebook_business import FacebookAdsApi
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode

from .config import ACCESS_TOKEN, ConfigBuilder
from .utils import read_output


@freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "global_enabled,custom_enabled,expected_enabled",
    [
        pytest.param(True, None, True, id="inherit-global-without-custom-setting"),
        pytest.param(True, False, True, id="inherit-global-with-custom-false"),
        pytest.param(True, True, True, id="both-enabled"),
        pytest.param(False, True, True, id="custom-only"),
        pytest.param(None, True, True, id="custom-without-global-setting"),
        pytest.param(False, False, False, id="both-disabled"),
        pytest.param(False, None, False, id="global-disabled"),
        pytest.param(None, False, False, id="custom-disabled"),
        pytest.param(None, None, False, id="default-disabled"),
    ],
)
def test_custom_insights_incrementality_requests(
    requests_mock: Mocker, global_enabled: bool | None, custom_enabled: bool | None, expected_enabled: bool
) -> None:
    account_ids = ["111111111111111", "222222222222222"]
    config_builder = ConfigBuilder().with_account_ids(account_ids)
    config = config_builder.build()
    insight: dict[str, str | bool | list[str]] = {
        "name": "Attribution",
        "fields": ["actions"],
        "breakdowns": [],
        "action_breakdowns": [],
    }
    if custom_enabled is not None:
        insight["include_incrementality"] = custom_enabled
    config["custom_insights"] = [insight]
    if global_enabled is not None:
        config["include_incrementality"] = global_enabled

    base_url = f"https://graph.facebook.com/{FacebookAdsApi.API_VERSION}"
    expected_records = []
    for index, account_id in enumerate(account_ids):
        report_id = str(1000 + index)
        requests_mock.get(
            f"{base_url}/act_{account_id}/",
            json={"account_id": account_id, "id": f"act_{account_id}", "timezone_name": "Etc/UTC"},
        )
        requests_mock.get(
            f"{base_url}/act_{account_id}/insights",
            json={},
            headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
        )
        requests_mock.post(f"{base_url}/act_{account_id}/insights", json={"report_run_id": report_id})
        record = {
            "account_id": account_id,
            "ad_id": str(2000 + index),
            "date_start": "2023-01-01",
            "date_stop": "2023-01-01",
            "actions": [{"action_type": "purchase", "value": "10", "incrementality": "2"}],
        }
        expected_records.append({**record, "actions": [{"action_type": "purchase", "value": 10.0, "incrementality": 2.0}]})
        requests_mock.get(f"{base_url}/{report_id}/insights", json={"data": [record]})

    def completed_reports(request: Any, context: Any) -> list[dict[str, int | str]]:
        batch = json.loads(parse_qs(request.text)["batch"][0])
        return [
            {
                "code": 200,
                "body": json.dumps(
                    {"id": item["relative_url"].rstrip("/"), "async_status": "Job Completed", "async_percent_completion": 100}
                ),
            }
            for item in batch
        ]

    requests_mock.post(f"{base_url}/", json=completed_reports)
    output = read_output(config_builder, "custom_attribution", SyncMode.incremental)
    output.raise_if_errors()

    job_requests = [request for request in requests_mock.request_history if request.method == "POST" and request.path.endswith("/insights")]
    assert len(job_requests) == 2
    expected_windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if expected_enabled:
        expected_windows.append("incrementality")
    for request, account_id in zip(sorted(job_requests, key=lambda request: request.path), account_ids):
        assert request.url == f"{base_url}/act_{account_id}/insights?access_token={ACCESS_TOKEN}"
        assert parse_qs(request.text) == {
            "level": ["ad"],
            "action_breakdowns": ["[]"],
            "breakdowns": ["[]"],
            "fields": ['["actions"]'],
            "time_increment": ["1"],
            "action_attribution_windows": [json.dumps(expected_windows, separators=(",", ":"))],
            "time_range": ['{"since":"2023-01-01","until":"2023-01-01"}'],
        }
    records = []
    for message in output.records:
        assert message.record is not None
        records.append(message.record.data)
    assert sorted(records, key=lambda record: record["account_id"]) == expected_records
