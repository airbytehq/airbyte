# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import copy
import json
from datetime import datetime
from urllib.parse import parse_qs

import pytest
from facebook_business import FacebookAdsApi
from freezegun import freeze_time
from source_facebook_marketing.api import API
from source_facebook_marketing.streams import AdsInsights
from source_facebook_marketing.streams.async_job_manager import APILimit

from airbyte_cdk.models import SyncMode


@pytest.fixture
def insights_api(requests_mock):
    graph = f"https://graph.facebook.com/{FacebookAdsApi.API_VERSION}"
    requests_mock.get(f"{graph}/act_123/", json={"id": "act_123", "timezone_name": "UTC"})
    requests_mock.get(
        f"{graph}/act_123/insights",
        json={"data": []},
        headers={"x-fb-ads-insights-throttle": '{"acc_id_util_pct": 0, "app_id_util_pct": 0}'},
    )

    def create_report(request, context):
        interval = json.loads(parse_qs(request.text)["time_range"][0])
        return {"report_run_id": interval["since"].replace("-", "")}

    requests_mock.post(f"{graph}/act_123/insights", json=create_report)
    for day in range(18, 23):
        report_id = f"202609{day}"
        requests_mock.get(
            f"{graph}/{report_id}/",
            json={"id": report_id, "async_status": "Job Completed", "async_percent_completion": 100},
        )
        requests_mock.get(
            f"{graph}/{report_id}/insights",
            json={"data": [{"ad_id": report_id, "date_start": f"2026-09-{day}", "date_stop": f"2026-09-{day}"}]},
        )
    return API(access_token="test-token", page_size=100)


@freeze_time("2026-09-23")
@pytest.mark.parametrize("stream_name", [None, "custom_ad_insights"])
@pytest.mark.parametrize("state_format", ["legacy", "multi_account"])
def test_interrupted_lookback_preserves_checkpoint(insights_api, requests_mock, stream_name, state_format):
    account_state = {"date_start": "2026-09-20", "slices": []}
    if state_format == "legacy":
        saved_state = {**account_state, "time_increment": 1}
        account_ids = ["123"]
    else:
        saved_state = {"123": account_state, "456": {"date_start": "2026-09-21", "slices": []}, "time_increment": 1}
        account_ids = ["123", "456"]

    def restore(state):
        stream = AdsInsights(
            api=insights_api,
            account_ids=account_ids,
            start_date=datetime(2026, 9, 1),
            end_date=datetime(2026, 9, 22),
            insights_lookback_window=2,
            name=stream_name,
            fields=["ad_id"],
        )
        stream.state = state
        jobs = {job.interval.start.day: job for job in stream._generate_async_jobs(stream.request_params(), "123")}
        assert list(jobs) == [18, 19, 20, 21, 22]
        return stream, jobs

    def read_slice(stream, jobs, day):
        job = jobs[day]
        job.start(APILimit(insights_api, "123"))
        job.update_job()
        return stream.read_records(SyncMode.incremental, stream_slice={"account_id": "123", "insight_job": job})

    stream, jobs = restore(saved_state)
    assert list(read_slice(stream, jobs, 19)) == [
        {"ad_id": "20260919", "date_start": "2026-09-19", "date_stop": "2026-09-19", "account_id": "123"}
    ]
    assert stream.state["123"] == {"date_start": "2026-09-20", "slices": ["2026-09-19"]}
    list(read_slice(stream, jobs, 18))
    assert stream.state["123"] == {"date_start": "2026-09-20", "slices": []}

    # Interrupt after a record but before the report's completion checkpoint.
    interrupted = read_slice(stream, jobs, 20)
    assert next(interrupted)["ad_id"] == "20260920"
    interrupted.close()
    saved_state = copy.deepcopy(stream.state)
    assert saved_state["123"] == {"date_start": "2026-09-20", "slices": []}

    for _ in range(2):
        stream, jobs = restore(saved_state)
        list(read_slice(stream, jobs, 18))
        saved_state = copy.deepcopy(stream.state)
        assert saved_state["123"] == {"date_start": "2026-09-20", "slices": []}

    stream, jobs = restore(saved_state)
    records = []
    for day in [22, 21, 20, 19, 18]:
        records.extend(read_slice(stream, jobs, day))
        assert stream.state["123"]["date_start"] == ("2026-09-22" if day == 18 else "2026-09-20")
    assert [record["ad_id"] for record in records] == ["20260922", "20260921", "20260920", "20260919", "20260918"]
    assert stream.state["123"] == {"date_start": "2026-09-22", "slices": []}
    if state_format == "multi_account":
        assert stream.state["456"] == {"date_start": "2026-09-21", "slices": []}

    requests = [request for request in requests_mock.request_history if request.method == "POST"]
    assert [json.loads(parse_qs(request.text)["time_range"][0]) for request in requests] == [
        {"since": f"2026-09-{day}", "until": f"2026-09-{day}"} for day in [19, 18, 20, 18, 18, 22, 21, 20, 19, 18]
    ]
