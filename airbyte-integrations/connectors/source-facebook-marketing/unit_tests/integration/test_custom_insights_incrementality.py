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


_INSIGHT_NAME = "my_custom_insight"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_FIELDS = ["ad_id", "impressions", "actions"]
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


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


def _job_status_response() -> HttpResponse:
    body = [
        {"body": json.dumps({"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100})}
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_response() -> HttpResponse:
    record = {
        "ad_id": "120200000000000001",
        "impressions": "100",
        "actions": [{"action_type": "purchase", "value": "3", "incrementality": "1"}],
        "account_id": ACCOUNT_ID,
        "date_start": START_DATE[:10],
        "date_stop": START_DATE[:10],
    }
    return build_response(body={"data": [record]}, status_code=HTTPStatus.OK)


def _custom_insight(include_incrementality: Optional[bool]) -> Dict[str, Any]:
    insight: Dict[str, Any] = {"name": _INSIGHT_NAME, "fields": _FIELDS, "breakdowns": [], "action_breakdowns": []}
    if include_incrementality is not None:
        insight["include_incrementality"] = include_incrementality
    return insight


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_include_incrementality,insight_include_incrementality,expected_windows",
    [
        pytest.param(True, None, _DEFAULT_WINDOWS + ["incrementality"], id="top_level_enabled_propagates_to_custom_insight"),
        pytest.param(False, True, _DEFAULT_WINDOWS + ["incrementality"], id="custom_insight_enabled_without_top_level"),
        pytest.param(False, None, _DEFAULT_WINDOWS, id="both_disabled_requests_default_windows"),
    ],
)
def test_custom_insight_job_requests_incrementality_window(
    top_level_include_incrementality: bool,
    insight_include_incrementality: Optional[bool],
    expected_windows: List[str],
) -> None:
    config_builder = config()
    config_builder._config["include_incrementality"] = top_level_include_incrementality
    config_builder._config["custom_insights"] = [_custom_insight(insight_include_incrementality)]

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
            _insights_response(),
        )

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    assert [record.record.data["ad_id"] for record in output.records] == ["120200000000000001"]
