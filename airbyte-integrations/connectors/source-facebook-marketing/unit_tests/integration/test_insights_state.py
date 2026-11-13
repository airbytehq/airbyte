#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime
from urllib.parse import parse_qs

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStateMessageSerializer, AirbyteStreamStateSerializer, SyncMode

from .config import ACCOUNT_ID
from .utils import config, read_output


@freeze_time("2023-01-10")
@pytest.mark.parametrize("stream_name", ["ads_insights", "custom_insights"])
@pytest.mark.parametrize("legacy_state", [False, True])
@pytest.mark.parametrize("empty_window", [False, True])
def test_interrupted_lookback_preserves_cursor(requests_mock, stream_name, legacy_state, empty_window):
    base_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}"
    requests_mock.get(
        f"{base_url}/act_{ACCOUNT_ID}/",
        json={"id": f"act_{ACCOUNT_ID}", "account_id": ACCOUNT_ID, "timezone_name": "Etc/UTC"},
    )
    requests_mock.get(
        f"{base_url}/act_{ACCOUNT_ID}/insights",
        json={"data": []},
        headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
    )

    requested_ranges = []
    interrupt = True

    def start_job(request, context):
        body = parse_qs(request.text)
        time_range = json.loads(body["time_range"][0])
        requested_ranges.append(time_range)
        return {"report_run_id": time_range["since"]}

    def poll_jobs(request, context):
        batch = json.loads(parse_qs(request.text)["batch"][0])
        return [
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
            for job in batch
        ]

    def get_results(request, context):
        day = request.path.split("/")[-2]
        if interrupt and day == "2023-01-04":
            context.status_code = 400
            return {"error": {"code": 190, "message": "Interrupted report download", "type": "OAuthException"}}
        records = [] if empty_window else [{"ad_id": day, "date_start": day, "date_stop": day, "account_id": ACCOUNT_ID}]
        return {"data": records}

    requests_mock.post(f"{base_url}/act_{ACCOUNT_ID}/insights", json=start_job)
    requests_mock.post(f"{base_url}/", json=poll_jobs)
    for day in range(1, 7):
        requests_mock.get(f"{base_url}/2023-01-{day:02}/insights", json=get_results)

    config_builder = config().with_start_date(datetime(2023, 1, 1)).with_end_date(datetime(2023, 1, 6))
    config_builder.build()["insights_lookback_window"] = 2
    if stream_name == "custom_insights":
        config_builder.build()["custom_insights"] = [
            {"name": "Insights", "fields": ["ad_id"], "breakdowns": [], "insights_lookback_window": 2}
        ]

    account_state = {"date_start": "2023-01-05", "slices": []}
    stream_state = {**account_state, "time_increment": 1} if legacy_state else {ACCOUNT_ID: account_state, "time_increment": 1}
    state = [
        AirbyteStateMessageSerializer.load(
            {"type": "STREAM", "stream": {"stream_descriptor": {"name": stream_name}, "stream_state": stream_state}}
        )
    ]
    expected_ranges = [{"since": f"2023-01-{day:02}", "until": f"2023-01-{day:02}"} for day in range(3, 7)]

    for _ in range(2):
        requested_ranges.clear()
        output = read_output(config_builder, stream_name, SyncMode.incremental, state=state, expecting_exception=True)
        assert requested_ranges == expected_ranges
        assert [message.record.data["ad_id"] for message in output.records] == ([] if empty_window else ["2023-01-03"])
        assert output.errors
        assert AirbyteStreamStateSerializer.dump(output.most_recent_state)["stream_state"] == {
            ACCOUNT_ID: {"date_start": "2023-01-05", "slices": []},
            "time_increment": 1,
        }
        state = [message.state for message in output.state_messages[-1:]]

    interrupt = False
    requested_ranges.clear()
    output = read_output(config_builder, stream_name, SyncMode.incremental, state=state)
    assert requested_ranges == expected_ranges
    assert [message.record.data["ad_id"] for message in output.records] == (
        [] if empty_window else [f"2023-01-{day:02}" for day in range(3, 7)]
    )
    assert AirbyteStreamStateSerializer.dump(output.most_recent_state)["stream_state"] == {
        ACCOUNT_ID: {"date_start": "2023-01-06", "slices": []},
        "time_increment": 1,
    }
