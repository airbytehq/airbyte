#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.request import HttpRequest

from .config import ACCESS_TOKEN, ACCOUNT_ID, DATE_FORMAT, NOW
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "incrementality_report"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_BASE_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_REPORT_RUN_IDS = ["1571860060019500", "4571860060019599"]
_JOB_IDS = ["1049937379601600", "1049937379601699"]


def _job_start_request(day: datetime, action_attribution_windows: List[str]) -> HttpRequest:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["actions"],
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": day.strftime(DATE_FORMAT), "until": day.strftime(DATE_FORMAT)},
    }
    return (
        RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body)).build()
    )


def _insights_response(day: datetime, ad_id: str):
    record = {
        "account_id": ACCOUNT_ID,
        "ad_id": ad_id,
        "date_start": day.strftime(DATE_FORMAT),
        "date_stop": day.strftime(DATE_FORMAT),
        "actions": [{"action_type": "purchase", "value": "3", "incrementality": "1"}],
    }
    return build_response(body={"data": [record]}, status_code=HTTPStatus.OK)


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_flag, custom_insight_flag, expected_windows",
    [
        pytest.param(True, False, _BASE_WINDOWS + ["incrementality"], id="top_level_flag_propagates_to_custom_insight"),
        pytest.param(False, True, _BASE_WINDOWS + ["incrementality"], id="custom_insight_flag_alone_enables_window"),
        pytest.param(True, True, _BASE_WINDOWS + ["incrementality"], id="both_flags_request_window_once"),
        pytest.param(False, False, _BASE_WINDOWS, id="no_flag_keeps_default_windows"),
    ],
)
def test_custom_insight_job_requests_incrementality_window(top_level_flag, custom_insight_flag, expected_windows):
    days = [NOW - timedelta(days=1), NOW]
    config_builder = config().with_start_date(days[0]).with_end_date(days[1])
    config_builder._config["include_incrementality"] = top_level_flag
    config_builder._config["custom_insights"] = [
        {
            "name": _INSIGHT_NAME,
            "fields": ["actions"],
            "breakdowns": [],
            "action_breakdowns": [],
            "level": "ad",
            "include_incrementality": custom_insight_flag,
        }
    ]

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(),
            build_response(
                body={},
                status_code=HTTPStatus.OK,
                headers={
                    "x-fb-ads-insights-throttle": json.dumps(
                        {"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}
                    )
                },
            ),
        )
        # The job start bodies are matched exactly, so a read that sends different attribution windows finds no mock and fails.
        for day, report_run_id in zip(days, _REPORT_RUN_IDS):
            http_mocker.post(
                _job_start_request(day, expected_windows),
                build_response(body={"report_run_id": report_run_id}, status_code=HTTPStatus.OK),
            )
        http_mocker.post(
            RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN)
            .with_body(encode_request_body({"batch": [{"method": "GET", "relative_url": f"{run_id}/"} for run_id in _REPORT_RUN_IDS]}))
            .build(),
            build_response(
                body=[
                    {
                        "body": json.dumps(
                            {"id": job_id, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100}
                        )
                    }
                    for job_id in _JOB_IDS
                ],
                status_code=HTTPStatus.OK,
            ),
        )
        for day, job_id, ad_id in zip(days, _JOB_IDS, ["ad_1", "ad_2"]):
            http_mocker.get(
                RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=job_id).with_limit(100).build(),
                _insights_response(day, ad_id),
            )

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    assert [(record.record.data["ad_id"], record.record.data["date_start"]) for record in output.records] == [
        ("ad_1", "2023-01-09"),
        ("ad_2", "2023-01-10"),
    ]
    assert [record.record.data["actions"] for record in output.records] == [
        [{"action_type": "purchase", "value": 3.0, "incrementality": 1.0}]
    ] * 2
