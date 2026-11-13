#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_STREAM_NAME = "custommy_report"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_RECORD = {
    "account_id": ACCOUNT_ID,
    "ad_id": "ad_1",
    "date_start": START_DATE[:10],
    "date_stop": START_DATE[:10],
    "impressions": "10",
}


def _job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": ["action_type"],
        "breakdowns": [],
        "fields": ["impressions", "actions"],
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _job_status_request() -> RequestBuilder:
    body = {"batch": [{"method": "GET", "relative_url": f"{_REPORT_RUN_ID}/"}]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _job_status_response() -> HttpResponse:
    job = {"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100}
    return build_response(body=[{"body": json.dumps(job)}], status_code=HTTPStatus.OK)


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_flag, custom_insight_flag, expected_windows",
    [
        pytest.param(True, None, _DEFAULT_WINDOWS + ["incrementality"], id="top_level_flag_propagates_to_custom_insight"),
        pytest.param(False, True, _DEFAULT_WINDOWS + ["incrementality"], id="custom_insight_flag_alone_enables_it"),
        pytest.param(False, None, _DEFAULT_WINDOWS, id="neither_flag_keeps_default_windows"),
    ],
)
def test_custom_insight_job_requests_incrementality_window(
    top_level_flag: bool, custom_insight_flag: Optional[bool], expected_windows: List[str]
) -> None:
    custom_insight: Dict[str, Any] = {
        "name": "my_report",
        "level": "ad",
        "fields": ["impressions", "actions"],
        "breakdowns": [],
        "action_breakdowns": ["action_type"],
    }
    if custom_insight_flag is not None:
        custom_insight["include_incrementality"] = custom_insight_flag
    config_builder = config()
    config_builder.build().update({"include_incrementality": top_level_flag, "custom_insights": [custom_insight]})

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(),
            _throttle_response(),
        )
        # The job-start mock matches on the exact body, so the read only yields the record when
        # the connector asks Facebook for exactly `expected_windows`.
        http_mocker.post(
            _job_start_request(expected_windows).build(),
            build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK),
        )
        http_mocker.post(_job_status_request().build(), _job_status_response())
        http_mocker.get(
            RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
            build_response(body={"data": [_RECORD]}, status_code=HTTPStatus.OK),
        )

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    assert [record.record.data["ad_id"] for record in output.records] == ["ad_1"]
    assert output.errors == []
