#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime
from urllib.parse import parse_qs

import pytest
from facebook_business import FacebookAdsApi
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStreamStateSerializer, FailureType, SyncMode

from .config import ACCOUNT_ID
from .utils import config, read_output


@freeze_time("2023-01-10")
@pytest.mark.parametrize("stream_name", ["ads_insights", "custom_ad_insights"])
def test_interrupted_lookback_preserves_cursor(requests_mock, stream_name: str) -> None:
    base_url = f"https://graph.facebook.com/{FacebookAdsApi.API_VERSION}"
    requests_mock.get(f"{base_url}/act_{ACCOUNT_ID}/", json={"account_id": ACCOUNT_ID, "timezone_name": "Etc/UTC"})
    requests_mock.get(
        f"{base_url}/act_{ACCOUNT_ID}/insights",
        json={},
        headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
    )
    created_dates = []
    fail_download = False

    def start_report(request, context):
        interval = json.loads(parse_qs(request.text)["time_range"][0])
        assert interval["since"] == interval["until"]
        created_dates.append(interval["since"])
        return {"report_run_id": interval["since"]}

    def poll_reports(request, context):
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

    def download_report(request, context):
        report_date = request.path.split("/")[-2]
        if fail_download and report_date == "2023-01-04":
            context.status_code = 400
            return {"error": {"code": 190, "message": "Invalid OAuth access token"}}
        return {"data": [{"ad_id": report_date, "date_start": report_date, "date_stop": report_date, "account_id": ACCOUNT_ID}]}

    requests_mock.post(f"{base_url}/act_{ACCOUNT_ID}/insights", json=start_report)
    requests_mock.post(f"{base_url}/", json=poll_reports)
    for day in range(1, 7):
        requests_mock.get(f"{base_url}/2023-01-{day:02}/insights", json=download_report)

    config_builder = config().with_start_date(datetime(2023, 1, 1)).with_end_date(datetime(2023, 1, 5))
    config_builder.build()["insights_lookback_window"] = 2
    fields = ["ad_id", "date_start", "date_stop", "account_id"]
    if stream_name == "custom_ad_insights":
        config_builder.build()["custom_insights"] = [{"name": "AdInsights", "fields": fields, "insights_lookback_window": 2}]
    schema = {"type": "object", "properties": {field: {"type": "string"} for field in fields}}

    def read(state=None, expecting_exception=False):
        return read_output(
            config_builder, stream_name, SyncMode.incremental, state=state, expecting_exception=expecting_exception, json_schema=schema
        )

    initial = read()
    assert [record.record.data["ad_id"] for record in initial.records] == [f"2023-01-{day:02}" for day in range(1, 6)]
    assert AirbyteStreamStateSerializer.dump(initial.most_recent_state)["stream_state"][ACCOUNT_ID]["date_start"] == "2023-01-05"

    config_builder.with_end_date(datetime(2023, 1, 6))
    state = [initial.state_messages[-1].state]
    expected_dates = [f"2023-01-{day:02}" for day in range(3, 7)]
    fail_download = True
    for _ in range(2):
        created_dates.clear()
        interrupted = read(state=state, expecting_exception=True)
        assert created_dates == expected_dates
        assert [record.record.data["ad_id"] for record in interrupted.records] == ["2023-01-03"]
        assert interrupted.errors[0].trace.error.failure_type == FailureType.config_error
        assert AirbyteStreamStateSerializer.dump(interrupted.most_recent_state)["stream_state"][ACCOUNT_ID]["date_start"] == "2023-01-05"
        state = [interrupted.state_messages[-1].state]

    created_dates.clear()
    fail_download = False
    resumed = read(state=state)
    assert created_dates == expected_dates
    assert [record.record.data["ad_id"] for record in resumed.records] == expected_dates
    assert AirbyteStreamStateSerializer.dump(resumed.most_recent_state)["stream_state"][ACCOUNT_ID]["date_start"] == "2023-01-06"
