#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
from urllib.parse import parse_qs

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from freezegun import freeze_time
from source_facebook_marketing import SourceFacebookMarketing

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, Type


@freeze_time("2026-11-03")
@pytest.mark.parametrize(
    "source_enabled,insight_enabled,expected_incrementality",
    [
        pytest.param(True, None, True, id="inherit_source"),
        pytest.param(True, False, True, id="source_enabled_insight_false"),
        pytest.param(False, True, True, id="insight_enabled"),
        pytest.param(True, True, True, id="both_enabled"),
        pytest.param(False, False, False, id="both_disabled"),
        pytest.param(False, None, False, id="defaults_disabled"),
    ],
)
def test_custom_insights_incrementality_requests(requests_mock, config, source_enabled, insight_enabled, expected_incrementality):
    insight = {
        "name": "Incrementality",
        "fields": ["ad_id", "account_id", "spend"],
        "breakdowns": [],
        "action_breakdowns": [],
        "time_increment": 1,
    }
    if insight_enabled is not None:
        insight["include_incrementality"] = insight_enabled
    config.update(
        start_date="2026-11-01T00:00:00Z",
        end_date="2026-11-02T00:00:00Z",
        include_incrementality=source_enabled,
        custom_insights=[insight],
    )
    graph_url = f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}"
    requests_mock.get(
        f"{graph_url}/act_123/insights",
        json={"data": []},
        headers={"x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0})},
    )
    requests_mock.post(
        f"{graph_url}/act_123/insights",
        [{"json": {"report_run_id": "report_1"}}, {"json": {"report_run_id": "report_2"}}],
    )
    requests_mock.post(
        f"{graph_url}/",
        json=[
            {
                "code": 200,
                "body": json.dumps({"id": f"report_{index}", "async_status": "Job Completed", "async_percent_completion": 100}),
            }
            for index in (1, 2)
        ],
    )
    for index, day in enumerate(("2026-11-01", "2026-11-02"), start=1):
        requests_mock.get(
            f"{graph_url}/report_{index}/insights",
            json={"data": [{"ad_id": str(index), "account_id": "123", "spend": "1.00", "date_start": day, "date_stop": day}]},
        )
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="custom_incrementality",
                    json_schema={"type": "object"},
                    supported_sync_modes=[SyncMode.incremental],
                    default_cursor_field=["date_start"],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
                cursor_field=["date_start"],
            )
        ]
    )

    messages = list(SourceFacebookMarketing().read(logging.getLogger("test"), config, catalog))

    records = [message.record.data for message in messages if message.type == Type.RECORD]
    assert [record["ad_id"] for record in records] == ["1", "2"]
    reports = [
        request for request in requests_mock.request_history if request.method == "POST" and request.path.endswith("/act_123/insights")
    ]
    assert len(reports) == 2
    expected_windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if expected_incrementality:
        expected_windows.append("incrementality")
    for request, day in zip(reports, ("2026-11-01", "2026-11-02")):
        body = parse_qs(request.text)
        assert request.path == f"/{FacebookAdsApi.API_VERSION}/act_123/insights"
        assert json.loads(body["action_attribution_windows"][0]) == expected_windows
        assert json.loads(body["time_range"][0]) == {"since": day, "until": day}
        assert json.loads(body["fields"][0]) == ["ad_id", "account_id", "spend"]
        assert body["level"] == ["ad"]
        assert body["time_increment"] == ["1"]
