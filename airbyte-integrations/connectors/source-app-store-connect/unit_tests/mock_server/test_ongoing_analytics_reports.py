# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.test.mock_http import HttpMocker

from .analytics_helpers import (
    APP_ID,
    INSTANCE_ID,
    REPORT_ID,
    download_processing_date,
    processing_date,
    read_analytics_stream,
)
from .utils import latest_stream_state


REPORTS = [
    ("app_sessions", "App Sessions Standard", "Sessions"),
    ("app_crashes", "App Crashes", "Crashes"),
    ("app_store_discovery_and_engagement", "App Store Discovery and Engagement Standard", "Counts"),
    ("app_store_purchases", "App Store Purchases Standard", "Purchases"),
    ("app_store_pre_orders", "App Store Pre-orders Standard", "Pre-Orders Placed"),
    ("app_store_retention_messaging", "App Store Retention Messaging", "Counts"),
    ("browser_choice_screen_selection", "Browser Choice Screen Selection", "Selection Rate"),
    ("browser_choice_screen_engagement", "Browser Choice Screen Engagement (iOS versions before 18.2)", "Counts"),
]


@pytest.mark.parametrize("stream_name,report_name,metric", REPORTS)
@pytest.mark.parametrize("scenario", ["full_refresh", "incremental", "empty", "missing"])
def test_ongoing_analytics_report(stream_name: str, report_name: str, metric: str, scenario: str) -> None:
    body = f"Date\tDevice\t{metric}\n"
    if scenario != "empty":
        body += f"{download_processing_date()}\tiPhone\t42\n"
    with HttpMocker() as http_mocker:
        output = read_analytics_stream(
            http_mocker,
            stream_name,
            report_name=report_name,
            tsv_body=body,
            incremental=scenario == "incremental",
            ignored_error=scenario == "missing",
        )
        if scenario in ("empty", "missing"):
            assert not output.records
        else:
            assert len(output.records) == 1
            record = output.records[0].record.data
            assert record["Date"] == download_processing_date()
            assert record["Device"] == "iPhone"
            assert record[metric] == "42"
            assert record["app_id"] == APP_ID
            assert record["report_id"] == REPORT_ID
            assert record["instance_id"] == INSTANCE_ID
            assert record["access_type"] == "ONGOING"
            assert record["processing_date"] == download_processing_date()
            if scenario == "incremental":
                assert latest_stream_state(output, "processing_date") == download_processing_date()
                state = vars(output.state_messages[-1].state.stream.stream_state)
                assert state["state"] == {"processing_date": download_processing_date()}
                assert state["use_global_cursor"] is False
                assert state["states"][0]["cursor"] == {"processing_date": download_processing_date()}
                segments_state = state["parent_state"]["analytics_standard_segments"]
                assert segments_state["state"] == {"processing_date": processing_date()}
                instances_state = segments_state["parent_state"]["analytics_standard_instances"]
                assert instances_state["state"] == {"processing_date": processing_date()}
