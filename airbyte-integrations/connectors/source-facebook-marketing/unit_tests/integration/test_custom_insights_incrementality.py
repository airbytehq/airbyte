#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, Dict, List

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE, ConfigBuilder
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import encode_request_body, read_output


_CUSTOM_INSIGHT_NAME = "my_custom_insight"
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["account_id", "ad_id", "date_start", "impressions"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_WINDOWS_WITH_INCREMENTALITY = _DEFAULT_WINDOWS + ["incrementality"]


def _config(top_level_include_incrementality: bool, insight_include_incrementality: bool) -> ConfigBuilder:
    builder = ConfigBuilder()
    builder._config["include_incrementality"] = top_level_include_incrementality
    builder._config["custom_insights"] = [
        {
            "name": _CUSTOM_INSIGHT_NAME,
            "fields": _FIELDS,
            "breakdowns": [],
            "action_breakdowns": [],
            "level": "ad",
            "time_increment": 1,
            "include_incrementality": insight_include_incrementality,
        }
    ]
    return builder


def _job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body: Dict[str, Any] = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": _FIELDS,
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _job_status_request() -> RequestBuilder:
    body = {"batch": [{"method": "GET", "relative_url": f"{_REPORT_RUN_ID}/"}]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _job_status_response() -> HttpResponse:
    body = [
        {
            "body": json.dumps({"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100}),
        }
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_include_incrementality, insight_include_incrementality, expected_windows",
    [
        pytest.param(True, False, _WINDOWS_WITH_INCREMENTALITY, id="top_level_enabled_propagates_to_custom_insight"),
        pytest.param(False, True, _WINDOWS_WITH_INCREMENTALITY, id="per_insight_enabled"),
        pytest.param(False, False, _DEFAULT_WINDOWS, id="both_disabled"),
    ],
)
def test_custom_insight_job_requests_incrementality_window(
    top_level_include_incrementality: bool, insight_include_incrementality: bool, expected_windows: List[str]
) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(),
            _throttle_response(),
        )
        http_mocker.post(
            _job_start_request(expected_windows).build(),
            build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK),
        )
        http_mocker.post(_job_status_request().build(), _job_status_response())
        http_mocker.get(
            RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
            build_response(
                body={"data": [{"account_id": ACCOUNT_ID, "ad_id": "123", "date_start": "2023-01-01", "impressions": "10"}]},
                status_code=HTTPStatus.OK,
            ),
        )

        output = read_output(
            config_builder=_config(top_level_include_incrementality, insight_include_incrementality),
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
        )

    assert [record.record.data["ad_id"] for record in output.records] == ["123"]
