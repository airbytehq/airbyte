#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import json
from datetime import timedelta
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import freezegun
import pytest
from source_facebook_marketing.streams.async_job import Status

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import HttpResponse
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse

from .config import ACCESS_TOKEN, ACCOUNT_ID, DATE_FORMAT, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "my_report"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_FIELDS = ["account_id", "ad_id", "actions", "date_start"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_DAYS = ["2023-01-01", "2023-01-02"]
_REPORT_RUN_IDS = ["1571860060019548", "1571860060019549"]


def _job_start_request(day: str, action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": ["action_type"],
        "breakdowns": [],
        "fields": _FIELDS,
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
        {"body": json.dumps({"id": run_id, "account_id": ACCOUNT_ID, "async_status": Status.COMPLETED, "async_percent_completion": 100})}
        for run_id in report_run_ids
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _insights_response(day: str) -> HttpResponse:
    record = {"account_id": ACCOUNT_ID, "ad_id": f"ad_{day}", "date_start": day, "date_stop": day}
    return build_response(body={"data": [record]}, status_code=HTTPStatus.OK)


def _custom_insight(include_incrementality: Optional[bool]) -> Dict[str, Any]:
    insight: Dict[str, Any] = {"name": _INSIGHT_NAME, "fields": _FIELDS, "breakdowns": [], "action_breakdowns": ["action_type"]}
    if include_incrementality is not None:
        insight["include_incrementality"] = include_incrementality
    return insight


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "source_include_incrementality, insight_include_incrementality, expected_windows",
    [
        pytest.param(
            True, None, [*_DEFAULT_WINDOWS, "incrementality"], id="source_toggle_applies_to_custom_insight_without_its_own_setting"
        ),
        pytest.param(
            True, False, [*_DEFAULT_WINDOWS, "incrementality"], id="source_toggle_applies_to_custom_insight_left_at_default_false"
        ),
        pytest.param(False, True, [*_DEFAULT_WINDOWS, "incrementality"], id="custom_insight_toggle_alone_still_enables_it"),
        pytest.param(False, None, _DEFAULT_WINDOWS, id="incrementality_stays_off_when_neither_toggle_is_set"),
    ],
)
def test_custom_insight_job_requests_incrementality_window_when_enabled_on_source_or_insight(
    source_include_incrementality: bool, insight_include_incrementality: Optional[bool], expected_windows: List[str]
) -> None:
    start_date = ab_datetime_parse(START_DATE)
    end_date = start_date + timedelta(days=1, hours=23)

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(),
            _throttle_response(),
        )
        # One async job per day: both must carry the same attribution windows, matched on the exact request body.
        for day, report_run_id in zip(_DAYS, _REPORT_RUN_IDS):
            http_mocker.post(
                _job_start_request(day, expected_windows).build(),
                build_response(body={"report_run_id": report_run_id}, status_code=HTTPStatus.OK),
            )
            http_mocker.get(
                RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=report_run_id).with_limit(100).build(),
                _insights_response(day),
            )
        http_mocker.post(_job_status_request(_REPORT_RUN_IDS).build(), _job_status_response(_REPORT_RUN_IDS))

        output = read_output(
            config_builder=config()
            .with_start_date(start_date)
            .with_end_date(end_date)
            .with_include_incrementality(source_include_incrementality)
            .with_custom_insights([_custom_insight(insight_include_incrementality)]),
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
        )

    # The job start mocks only match the exact body, so both days being read proves each job asked for expected_windows.
    assert [record.record.data["ad_id"] for record in output.records] == [f"ad_{day}" for day in _DAYS]
