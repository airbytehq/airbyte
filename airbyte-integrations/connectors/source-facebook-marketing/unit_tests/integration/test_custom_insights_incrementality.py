#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from urllib.parse import parse_qs

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode

from .config import ACCESS_TOKEN
from .utils import config, read_output


@pytest.mark.parametrize(
    "source_enabled,custom_enabled,expected_enabled",
    [
        pytest.param(True, None, True, id="source_enabled_custom_omitted"),
        pytest.param(True, False, True, id="source_enabled_custom_false"),
        pytest.param(True, True, True, id="both_enabled"),
        pytest.param(False, True, True, id="custom_enabled"),
        pytest.param(False, False, False, id="both_disabled"),
        pytest.param(False, None, False, id="source_disabled_custom_omitted"),
    ],
)
@freeze_time("2023-01-10T00:00:00Z")
def test_custom_insights_incrementality_requests(
    requests_mock: Mocker, source_enabled: bool, custom_enabled: bool | None, expected_enabled: bool
) -> None:
    account_ids = ["123", "456"]
    custom_insight = {"name": "Incrementality", "fields": ["ad_id", "actions"], "breakdowns": [], "action_breakdowns": []}
    if custom_enabled is not None:
        custom_insight["include_incrementality"] = custom_enabled
    config_builder = config().with_account_ids(account_ids)
    config_builder.build().update(include_incrementality=source_enabled, custom_insights=[custom_insight])
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}"

    requests_mock.post(
        f"{base_url}/",
        json=lambda request, context: [
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
            for job in json.loads(parse_qs(request.text)["batch"][0])
        ],
    )
    for account_id in account_ids:
        requests_mock.get(
            f"{base_url}/act_{account_id}/",
            json={"id": f"act_{account_id}", "account_id": account_id, "timezone_name": "Etc/UTC"},
        )
        requests_mock.get(
            f"{base_url}/act_{account_id}/insights",
            json={"data": []},
            headers={"x-fb-ads-insights-throttle": '{"app_id_util_pct":0,"acc_id_util_pct":0}'},
        )
        requests_mock.post(f"{base_url}/act_{account_id}/insights", json={"report_run_id": f"report_{account_id}"})
        requests_mock.get(
            f"{base_url}/report_{account_id}/insights",
            json={
                "data": [
                    {
                        "account_id": account_id,
                        "ad_id": f"ad_{account_id}",
                        "date_start": "2023-01-01",
                        "date_stop": "2023-01-01",
                        "actions": [{"action_type": "purchase", "value": "10"}],
                    }
                ]
            },
        )

    output = read_output(config_builder, "custom_incrementality", SyncMode.incremental)

    job_requests = [request for request in requests_mock.request_history if request.method == "POST" and request.path.endswith("/insights")]
    assert sorted(request.path for request in job_requests) == [
        f"/{FacebookAdsApi.API_VERSION}/act_{account_id}/insights" for account_id in account_ids
    ]
    expected_windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if expected_enabled:
        expected_windows.append("incrementality")
    for request in job_requests:
        assert request.qs == {"access_token": [ACCESS_TOKEN]}
        assert parse_qs(request.text) == {
            "level": ["ad"],
            "fields": ['["ad_id","actions"]'],
            "breakdowns": ["[]"],
            "action_breakdowns": ["[]"],
            "time_increment": ["1"],
            "action_attribution_windows": [json.dumps(expected_windows, separators=(",", ":"))],
            "time_range": ['{"since":"2023-01-01","until":"2023-01-01"}'],
        }
    assert sorted((record.record.data["account_id"], record.record.data["ad_id"]) for record in output.records) == [
        (account_id, f"ad_{account_id}") for account_id in account_ids
    ]
