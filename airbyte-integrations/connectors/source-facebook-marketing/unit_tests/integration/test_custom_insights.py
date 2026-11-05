#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from urllib.parse import parse_qs, urlparse

import freezegun
import pytest
from facebook_business import FacebookAdsApi
from requests_mock import Mocker
from source_facebook_marketing import SourceFacebookMarketing

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import read

from .config import ACCESS_TOKEN, ConfigBuilder
from .utils import catalog, encode_request_body


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "source_incrementality,custom_incrementality,expected_incrementality",
    [
        (None, None, False),
        (None, False, False),
        (None, True, True),
        (False, None, False),
        (False, False, False),
        (False, True, True),
        (True, None, True),
        (True, False, True),
        (True, True, True),
    ],
)
def test_custom_insights_read_inherits_incrementality(
    requests_mock: Mocker,
    source_incrementality: bool | None,
    custom_incrementality: bool | None,
    expected_incrementality: bool,
) -> None:
    account_ids = ["111111111111111", "222222222222222"]
    config = ConfigBuilder().with_account_ids(account_ids).build()
    insight = {"name": "Attribution", "fields": ["ad_id", "actions"], "breakdowns": [], "action_breakdowns": []}
    if source_incrementality is not None:
        config["include_incrementality"] = source_incrementality
    if custom_incrementality is not None:
        insight["include_incrementality"] = custom_incrementality
    config["custom_insights"] = [insight]
    api_url = f"https://graph.facebook.com/{FacebookAdsApi.API_VERSION}"

    def job_status_response(request, context):
        batch = json.loads(parse_qs(request.text)["batch"][0])
        return [
            {"body": json.dumps({"id": job["relative_url"].strip("/"), "async_status": "Job Completed", "async_percent_completion": 100})}
            for job in batch
        ]

    requests_mock.post(f"{api_url}/", json=job_status_response)
    for account_id in account_ids:
        requests_mock.get(
            f"{api_url}/act_{account_id}/",
            json={"account_id": account_id, "id": f"act_{account_id}", "timezone_name": "Etc/UTC"},
        )
        requests_mock.get(
            f"{api_url}/act_{account_id}/insights",
            json={},
            headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
        )
        requests_mock.post(f"{api_url}/act_{account_id}/insights", json={"report_run_id": f"report_{account_id}"})
        requests_mock.get(
            f"{api_url}/report_{account_id}/insights",
            json={"data": [{"account_id": account_id, "ad_id": f"ad_{account_id}", "date_start": "2023-01-01", "date_stop": "2023-01-01"}]},
        )

    output = read(SourceFacebookMarketing(), config, catalog("custom_attribution", SyncMode.incremental, {}))

    job_requests = [request for request in requests_mock.request_history if request.method == "POST" and request.path.endswith("/insights")]
    assert sorted(request.path for request in job_requests) == [
        f"/{FacebookAdsApi.API_VERSION}/act_{account_id}/insights" for account_id in account_ids
    ]
    expected_windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if expected_incrementality:
        expected_windows.append("incrementality")
    for request in job_requests:
        assert parse_qs(urlparse(request.url).query) == {"access_token": [ACCESS_TOKEN]}
        expected_body = {
            "level": "ad",
            "action_breakdowns": [],
            "breakdowns": [],
            "fields": ["ad_id", "actions"],
            "time_increment": 1,
            "action_attribution_windows": expected_windows,
            "time_range": {"since": "2023-01-01", "until": "2023-01-01"},
        }
        assert parse_qs(request.text) == parse_qs(encode_request_body(expected_body))
    assert sorted((message.record.data["account_id"], message.record.data["ad_id"]) for message in output.records) == [
        (account_id, f"ad_{account_id}") for account_id in account_ids
    ]
