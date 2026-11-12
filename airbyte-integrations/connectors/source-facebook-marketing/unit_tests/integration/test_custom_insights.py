#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID, DATE_FORMAT, NOW
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "incrementality_report"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_FIELDS = ["ad_id", "actions", "spend"]
_BASE_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_WINDOWS_WITH_INCREMENTALITY = [*_BASE_WINDOWS, "incrementality"]


def _job_start_request(day: datetime, action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": _FIELDS,
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": day.strftime(DATE_FORMAT), "until": day.strftime(DATE_FORMAT)},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _job_status_request(report_run_ids: List[str]) -> RequestBuilder:
    body = {"batch": [{"method": "GET", "relative_url": f"{report_run_id}/"} for report_run_id in report_run_ids]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _job_status_response(job_ids: List[str]) -> HttpResponse:
    body = [
        {"body": json.dumps({"id": job_id, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100})}
        for job_id in job_ids
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _insights_response(ad_id: str, day: datetime, incrementality: Optional[str]) -> HttpResponse:
    action: Dict[str, Any] = {"action_type": "purchase", "value": "10", "1d_click": "10"}
    if incrementality is not None:
        action["incrementality"] = incrementality
    record = {
        "account_id": ACCOUNT_ID,
        "ad_id": ad_id,
        "actions": [action],
        "spend": "1.5",
        "date_start": day.strftime(DATE_FORMAT),
        "date_stop": day.strftime(DATE_FORMAT),
    }
    return build_response(body={"data": [record]}, status_code=HTTPStatus.OK)


@pytest.mark.parametrize(
    "top_level_flag,custom_insight_flag,expected_windows",
    [
        pytest.param(True, None, _WINDOWS_WITH_INCREMENTALITY, id="top_level_enabled_custom_insight_unset_inherits"),
        pytest.param(True, False, _WINDOWS_WITH_INCREMENTALITY, id="top_level_enabled_custom_insight_default_false_inherits"),
        pytest.param(False, True, _WINDOWS_WITH_INCREMENTALITY, id="custom_insight_enabled_only"),
        pytest.param(False, False, _BASE_WINDOWS, id="both_disabled"),
    ],
)
@freezegun.freeze_time(NOW.isoformat())
def test_custom_insight_requests_incrementality_window_when_enabled_at_either_level(
    top_level_flag: bool, custom_insight_flag: Optional[bool], expected_windows: List[str]
) -> None:
    """The top-level `include_incrementality` option must reach custom insight streams (airbyte-internal-issues#19563)."""
    day_1, day_2 = NOW - timedelta(days=1), NOW
    report_run_id_1, report_run_id_2 = "1571860060019500", "4571860060019599"
    job_id_1, job_id_2 = "1049937379601600", "1049937379601699"
    includes_incrementality = "incrementality" in expected_windows

    custom_insight: Dict[str, Any] = {"name": _INSIGHT_NAME, "fields": _FIELDS, "level": "ad"}
    if custom_insight_flag is not None:
        custom_insight["include_incrementality"] = custom_insight_flag
    config_builder = (
        config()
        .with_start_date(day_1)
        .with_end_date(day_2)
        .with_include_incrementality(top_level_flag)
        .with_custom_insights([custom_insight])
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(), _throttle_response()
        )
        # The job-start mocks match on the exact request body, so a read only succeeds when every daily
        # report is requested with exactly `expected_windows`.
        job_start_1 = _job_start_request(day_1, expected_windows).build()
        job_start_2 = _job_start_request(day_2, expected_windows).build()
        http_mocker.post(job_start_1, build_response(body={"report_run_id": report_run_id_1}, status_code=HTTPStatus.OK))
        http_mocker.post(job_start_2, build_response(body={"report_run_id": report_run_id_2}, status_code=HTTPStatus.OK))
        http_mocker.post(_job_status_request([report_run_id_1, report_run_id_2]).build(), _job_status_response([job_id_1, job_id_2]))
        http_mocker.get(
            RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=job_id_1).with_limit(100).build(),
            _insights_response("ad_1", day_1, "4" if includes_incrementality else None),
        )
        http_mocker.get(
            RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=job_id_2).with_limit(100).build(),
            _insights_response("ad_2", day_2, "4" if includes_incrementality else None),
        )

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

        http_mocker.assert_number_of_calls(job_start_1, 1)
        http_mocker.assert_number_of_calls(job_start_2, 1)

    assert output.errors == []
    assert [(record.record.data["ad_id"], record.record.data["date_start"]) for record in output.records] == [
        ("ad_1", day_1.strftime(DATE_FORMAT)),
        ("ad_2", day_2.strftime(DATE_FORMAT)),
    ]
    assert [record.record.data["actions"][0].get("incrementality") for record in output.records] == [
        4.0 if includes_incrementality else None
    ] * 2
