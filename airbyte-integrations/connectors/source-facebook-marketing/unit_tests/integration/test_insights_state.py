#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime
from urllib.parse import parse_qs

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode

from .config import ACCOUNT_ID, ConfigBuilder
from .utils import read_output


@freeze_time("2026-01-10")
@pytest.mark.parametrize("stream_name", ["ads_insights", "custom_insights"])
def test_interrupted_lookback_preserves_cursor_and_resume_bounds(requests_mock, stream_name: str) -> None:
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}"
    requests_mock.get(f"{base_url}/act_{ACCOUNT_ID}/", json={"account_id": ACCOUNT_ID, "id": f"act_{ACCOUNT_ID}"})
    requests_mock.get(
        f"{base_url}/act_{ACCOUNT_ID}/insights",
        json={"data": []},
        headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
    )
    config = ConfigBuilder().with_start_date(datetime(2026, 1, 1)).with_end_date(datetime(2026, 1, 5))
    config.build()["insights_lookback_window"] = 2
    if stream_name == "custom_insights":
        config.build()["custom_insights"] = [{"name": "Insights", "fields": ["ad_id"], "breakdowns": [], "insights_lookback_window": 2}]

    def run(state=None, failed_date=None, delayed_date=None):
        intervals = []
        report_dates = {}
        poll_count = 0

        def start_report(request, context):
            params = parse_qs(request.text)
            interval = json.loads(params["time_range"][0])
            intervals.append(interval)
            report_id = str(len(intervals))
            report_dates[report_id] = interval["since"]
            return {"report_run_id": report_id}

        def poll_reports(request, context):
            nonlocal poll_count
            poll_count += 1
            batch = json.loads(parse_qs(request.text)["batch"][0])
            return [
                {
                    "code": 200,
                    "body": json.dumps(
                        {
                            "id": item["relative_url"].strip("/"),
                            "async_status": (
                                "Job Running"
                                if poll_count == 1 and report_dates[item["relative_url"].strip("/")] == delayed_date
                                else "Job Completed"
                            ),
                            "async_percent_completion": 100,
                        }
                    ),
                }
                for item in batch
            ]

        def download_report(request, context):
            report_id = request.path.split("/")[-2]
            report_date = report_dates[report_id]
            if report_date == failed_date:
                context.status_code = 400
                return {"error": {"code": 100, "message": "Interrupted report download"}}
            return {"data": [{"ad_id": report_date, "date_start": report_date, "date_stop": report_date, "account_id": ACCOUNT_ID}]}

        requests_mock.post(f"{base_url}/act_{ACCOUNT_ID}/insights", json=start_report)
        requests_mock.post(f"{base_url}/", json=poll_reports)
        for report_id in range(1, 8):
            requests_mock.get(f"{base_url}/{report_id}/insights", json=download_report)
        output = read_output(config, stream_name, SyncMode.incremental, state=state, expecting_exception=failed_date is not None)
        return output, intervals

    initial, intervals = run()
    assert [record.record.data["ad_id"] for record in initial.records] == [f"2026-01-{day:02}" for day in range(1, 6)]
    assert intervals == [{"since": f"2026-01-{day:02}", "until": f"2026-01-{day:02}"} for day in range(1, 6)]
    assert vars(initial.most_recent_state.stream_state) == {
        ACCOUNT_ID: {"date_start": "2026-01-05", "slices": []},
        "time_increment": 1,
    }

    config.with_end_date(datetime(2026, 1, 7))
    state = [initial.state_messages[-1].state]
    for _ in range(2):
        interrupted, intervals = run(state, failed_date="2026-01-04")
        assert [record.record.data["ad_id"] for record in interrupted.records] == ["2026-01-03"]
        assert intervals == [{"since": f"2026-01-{day:02}", "until": f"2026-01-{day:02}"} for day in range(3, 8)]
        assert vars(interrupted.most_recent_state.stream_state) == {
            ACCOUNT_ID: {"date_start": "2026-01-05", "slices": []},
            "time_increment": 1,
        }
        state = [interrupted.state_messages[-1].state]

    interrupted, intervals = run(state, failed_date="2026-01-06", delayed_date="2026-01-06")
    assert [record.record.data["ad_id"] for record in interrupted.records] == ["2026-01-03", "2026-01-04", "2026-01-05", "2026-01-07"]
    assert vars(interrupted.most_recent_state.stream_state) == {
        ACCOUNT_ID: {"date_start": "2026-01-05", "slices": ["2026-01-07"]},
        "time_increment": 1,
    }

    resumed, intervals = run([interrupted.state_messages[-1].state])
    assert intervals == [{"since": f"2026-01-{day:02}", "until": f"2026-01-{day:02}"} for day in range(3, 8)]
    assert [record.record.data["ad_id"] for record in resumed.records] == [f"2026-01-{day:02}" for day in range(3, 8)]
    assert vars(resumed.most_recent_state.stream_state) == {
        ACCOUNT_ID: {"date_start": "2026-01-07", "slices": ["2026-01-07"]},
        "time_increment": 1,
    }
