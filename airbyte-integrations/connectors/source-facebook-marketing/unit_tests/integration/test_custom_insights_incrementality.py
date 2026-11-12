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

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_STREAM_NAME = "custom_incrementality_report"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["account_id", "ad_id", "actions"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_RECORD = {
    "account_id": ACCOUNT_ID,
    "ad_id": "23854695759200548",
    "actions": [{"action_type": "link_click", "value": "10", "1d_click": "10", "incrementality": "4"}],
    "date_start": START_DATE[:10],
    "date_stop": START_DATE[:10],
}


def _job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": _FIELDS,
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _job_status_response() -> HttpResponse:
    body = [
        {"body": json.dumps({"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100})}
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _config(top_level: Optional[bool], custom_insight: Optional[bool]) -> Any:
    insight: Dict[str, Any] = {"name": "IncrementalityReport", "fields": _FIELDS, "breakdowns": [], "action_breakdowns": []}
    if custom_insight is not None:
        insight["include_incrementality"] = custom_insight
    config_builder = config()
    config_builder._config["custom_insights"] = [insight]
    if top_level is not None:
        config_builder._config["include_incrementality"] = top_level
    return config_builder


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level,custom_insight,expected_windows",
    [
        pytest.param(True, None, _DEFAULT_WINDOWS + ["incrementality"], id="unset_custom_insight_inherits_enabled_top_level"),
        pytest.param(True, False, _DEFAULT_WINDOWS, id="explicit_false_on_custom_insight_overrides_enabled_top_level"),
        pytest.param(False, True, _DEFAULT_WINDOWS + ["incrementality"], id="explicit_true_on_custom_insight_overrides_disabled_top_level"),
        pytest.param(None, None, _DEFAULT_WINDOWS, id="both_unset_stays_disabled"),
    ],
)
def test_custom_insight_job_requests_incrementality_window_from_top_level_config_unless_overridden(
    top_level: Optional[bool], custom_insight: Optional[bool], expected_windows: List[str]
) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(),
            _throttle_response(),
        )
        # The async job is only matched when it is started with exactly `expected_windows`.
        http_mocker.post(
            _job_start_request(expected_windows).build(),
            build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK),
        )
        http_mocker.post(
            RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN)
            .with_body(encode_request_body({"batch": [{"method": "GET", "relative_url": f"{_REPORT_RUN_ID}/"}]}))
            .build(),
            _job_status_response(),
        )
        http_mocker.get(
            RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
            build_response(body={"data": [_RECORD]}, status_code=HTTPStatus.OK),
        )

        output = read_output(config_builder=_config(top_level, custom_insight), stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    assert [record.record.data["ad_id"] for record in output.records] == [_RECORD["ad_id"]]
