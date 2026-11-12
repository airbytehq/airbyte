#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_STREAM_NAME = "customincrementality_report"
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
# The config spans two days, so the stream starts one report job per day.
_DAYS = ["2023-01-01", "2023-01-02"]
_REPORT_RUN_IDS = {"2023-01-01": "1571860060019548", "2023-01-02": "1571860060019549"}


def _job_start_request(day: str, action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": ["action_type"],
        "breakdowns": [],
        "fields": ["account_id", "ad_id", "actions", "date_start", "date_stop"],
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": day, "until": day},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _job_status_request(report_run_ids: List[str]) -> RequestBuilder:
    body = {"batch": [{"method": "GET", "relative_url": f"{report_run_id}/"} for report_run_id in report_run_ids]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _job_status_response(report_run_ids: List[str]) -> HttpResponse:
    body = [
        {"body": json.dumps({"id": run_id, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100})}
        for run_id in report_run_ids
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _insights_response(day: str) -> HttpResponse:
    record = {
        "account_id": ACCOUNT_ID,
        "ad_id": f"ad_{day}",
        "actions": [{"action_type": "purchase", "value": "3", "1d_click": "2", "incrementality": "1"}],
        "date_start": day,
        "date_stop": day,
    }
    return build_response(body={"data": [record]}, status_code=HTTPStatus.OK)


def _custom_insight(include_incrementality: Optional[bool]) -> Dict[str, Any]:
    insight = {
        "name": "incrementality_report",
        "level": "ad",
        "fields": ["account_id", "ad_id", "actions", "date_start", "date_stop"],
        "breakdowns": [],
        "action_breakdowns": ["action_type"],
    }
    if include_incrementality is not None:
        insight["include_incrementality"] = include_incrementality
    return insight


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "source_level,insight_level,expected_windows",
    [
        pytest.param(True, None, _DEFAULT_WINDOWS + ["incrementality"], id="source_toggle_applies_when_insight_toggle_is_unset"),
        pytest.param(True, False, _DEFAULT_WINDOWS + ["incrementality"], id="source_toggle_applies_when_insight_toggle_is_off"),
        pytest.param(False, True, _DEFAULT_WINDOWS + ["incrementality"], id="insight_toggle_alone_still_applies"),
        pytest.param(False, None, _DEFAULT_WINDOWS, id="no_toggle_requests_default_windows"),
    ],
)
def test_custom_insight_job_requests_incrementality_window(source_level, insight_level, expected_windows):
    """
    The `action_attribution_windows` a custom insight stream sends when starting its report jobs must honour the
    source-level `include_incrementality` toggle as well as the per-insight one.
    """
    config_builder = config()
    config_builder.build().update(
        {
            "end_date": "2023-01-02T23:59:59Z",
            "include_incrementality": source_level,
            "custom_insights": [_custom_insight(insight_level)],
        }
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(),
            _throttle_response(),
        )
        # HttpMocker matches the POST body exactly: a job started with any other attribution windows finds no match.
        job_start_requests = {day: _job_start_request(day, expected_windows).build() for day in _DAYS}
        for day in _DAYS:
            http_mocker.post(
                job_start_requests[day], build_response(body={"report_run_id": _REPORT_RUN_IDS[day]}, status_code=HTTPStatus.OK)
            )
            http_mocker.get(
                RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_REPORT_RUN_IDS[day])
                .with_limit(100)
                .build(),
                _insights_response(day),
            )
        run_ids = list(_REPORT_RUN_IDS.values())
        http_mocker.post(_job_status_request(run_ids).build(), _job_status_response(run_ids))

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

        assert [record.record.data["ad_id"] for record in output.records] == ["ad_2023-01-01", "ad_2023-01-02"]
        assert output.errors == []
        for day in _DAYS:
            http_mocker.assert_number_of_calls(job_start_requests[day], 1)
