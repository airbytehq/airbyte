#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import re
from datetime import date, datetime, timedelta
from urllib.parse import parse_qs

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStreamStateSerializer, SyncMode

from .config import ACCOUNT_ID, ConfigBuilder
from .utils import read_output


@freeze_time("2026-02-03")
@pytest.mark.parametrize("stream_name", ["ads_insights", "custom_ad_insights"])
@pytest.mark.parametrize("empty_results", [False, True], ids=["records", "empty-reports"])
def test_interrupted_lookback_preserves_checkpoint(requests_mock, stream_name: str, empty_results: bool) -> None:
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}"
    jobs = {}
    requested_intervals = []
    fail_on = None

    def start_job(request, context):
        params = parse_qs(request.text)
        interval = json.loads(params["time_range"][0])
        requested_intervals.append(interval)
        job_id = interval["since"].replace("-", "")
        jobs[job_id] = interval["since"]
        return {"report_run_id": job_id}

    def job_status(request, context):
        batch = json.loads(parse_qs(request.text)["batch"][0])
        return [
            {
                "code": 200,
                "body": json.dumps(
                    {
                        "id": item["relative_url"].strip("/"),
                        "async_status": "Job Completed",
                        "async_percent_completion": 100,
                    }
                ),
            }
            for item in batch
        ]

    def results(request, context):
        job_id = request.path.split("/")[-2]
        day = jobs[job_id]
        if day == fail_on:
            context.status_code = 400
            return {"error": {"message": "Interrupted report download", "type": "OAuthException", "code": 190}}
        return {"data": ([] if empty_results else [{"ad_id": job_id, "account_id": ACCOUNT_ID, "date_start": day, "date_stop": day}])}

    requests_mock.get(f"{base_url}/act_{ACCOUNT_ID}/", json={"id": f"act_{ACCOUNT_ID}", "timezone_name": "UTC"})
    requests_mock.get(
        f"{base_url}/act_{ACCOUNT_ID}/insights",
        json={"data": []},
        headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
    )
    requests_mock.post(f"{base_url}/act_{ACCOUNT_ID}/insights", json=start_job)
    requests_mock.post(base_url + "/", json=job_status)
    requests_mock.get(re.compile(re.escape(base_url) + r"/\d+/insights"), json=results)

    def read(state=None, expecting_exception=False, end_date: datetime = datetime(2026, 2, 1)):
        config = ConfigBuilder().with_start_date(datetime(2026, 1, 1)).with_end_date(end_date)
        if stream_name == "custom_ad_insights":
            config.build()["custom_insights"] = [{"name": "AdInsights", "fields": ["ad_id", "date_start", "date_stop"]}]
        return read_output(config, stream_name, SyncMode.incremental, state=state, expecting_exception=expecting_exception)

    def intervals(first: date, last: date):
        return [
            {"since": (first + timedelta(days=i)).isoformat(), "until": (first + timedelta(days=i)).isoformat()}
            for i in range((last - first).days + 1)
        ]

    initial = read()
    assert not initial.errors
    assert requested_intervals == intervals(date(2026, 1, 1), date(2026, 2, 1))
    assert AirbyteStreamStateSerializer.dump(initial.most_recent_state)["stream_state"][ACCOUNT_ID]["date_start"] == "2026-02-01"

    # Interrupt after the first report in the 28-day refresh window was consumed.
    requested_intervals.clear()
    fail_on = "2026-01-05"
    interrupted = read(state=[initial.state_messages[-1].state], expecting_exception=True)
    assert interrupted.errors
    assert requested_intervals == intervals(date(2026, 1, 4), date(2026, 2, 1))
    if not empty_results:
        assert [message.record.data["date_start"] for message in interrupted.records] == ["2026-01-04"]
    assert AirbyteStreamStateSerializer.dump(interrupted.most_recent_state)["stream_state"][ACCOUNT_ID]["date_start"] == "2026-02-01"

    requested_intervals.clear()
    fail_on = None
    resumed = read(state=[interrupted.state_messages[-1].state], end_date=datetime(2026, 2, 2))
    assert not resumed.errors
    assert requested_intervals == intervals(date(2026, 1, 4), date(2026, 2, 2))
    assert [message.record.data["date_start"] for message in resumed.records] == (
        [] if empty_results else [interval["since"] for interval in requested_intervals]
    )
    assert AirbyteStreamStateSerializer.dump(resumed.most_recent_state)["stream_state"][ACCOUNT_ID]["date_start"] == "2026-02-02"
