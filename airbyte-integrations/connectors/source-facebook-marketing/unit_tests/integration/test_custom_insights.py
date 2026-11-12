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
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "incrementality_report"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_AD_ID = "23846784938030398"
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _custom_insight(include_incrementality: Optional[bool]) -> Dict[str, Any]:
    insight: Dict[str, Any] = {"name": _INSIGHT_NAME, "level": "ad", "fields": ["actions"]}
    if include_incrementality is not None:
        insight["include_incrementality"] = include_incrementality
    return insight


def _job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["actions"],
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _insight_record(action_attribution_windows: List[str]) -> Dict[str, Any]:
    # Facebook only returns the attribution windows that were requested when the report job was started
    action = {"action_type": "purchase", "value": "5"}
    action.update({window: "1" for window in action_attribution_windows})
    return {
        "account_id": ACCOUNT_ID,
        "ad_id": _AD_ID,
        "date_start": START_DATE[:10],
        "date_stop": START_DATE[:10],
        "actions": [action],
    }


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "source_include_incrementality, insight_include_incrementality, expected_windows",
    [
        pytest.param(True, None, [*_DEFAULT_WINDOWS, "incrementality"], id="source_level_setting_applies_to_custom_insight"),
        pytest.param(True, False, [*_DEFAULT_WINDOWS, "incrementality"], id="source_level_setting_applies_when_insight_flag_is_false"),
        pytest.param(False, True, [*_DEFAULT_WINDOWS, "incrementality"], id="insight_level_setting_alone_enables_incrementality"),
        pytest.param(False, None, _DEFAULT_WINDOWS, id="incrementality_is_not_requested_when_disabled_everywhere"),
    ],
)
def test_custom_insight_requests_incrementality_window_when_enabled_at_source_or_insight_level(
    source_include_incrementality: bool, insight_include_incrementality: Optional[bool], expected_windows: List[str]
) -> None:
    start_date = ab_datetime_parse(START_DATE)
    end_date = ab_datetime_parse(END_DATE)
    config_builder = (
        config()
        .with_start_date(start_date)
        .with_end_date(end_date)
        .with_include_incrementality(source_include_incrementality)
        .with_custom_insight(_custom_insight(insight_include_incrementality))
    )
    job_start_request = _job_start_request(expected_windows).build()
    job_status_body = {"batch": [{"method": "GET", "relative_url": f"{_REPORT_RUN_ID}/"}]}

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
        # The report job only starts when the request body carries exactly the expected attribution windows
        http_mocker.post(job_start_request, build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK))
        http_mocker.post(
            RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(job_status_body)).build(),
            build_response(
                body=[
                    {
                        "body": json.dumps(
                            {"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100}
                        )
                    }
                ],
                status_code=HTTPStatus.OK,
            ),
        )
        http_mocker.get(
            RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
            build_response(body={"data": [_insight_record(expected_windows)]}, status_code=HTTPStatus.OK),
        )

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

        http_mocker.assert_number_of_calls(job_start_request, 1)

    assert [(record.record.data["ad_id"], record.record.data["actions"]) for record in output.records] == [
        (_AD_ID, [{"action_type": "purchase", "value": 5.0, **{window: 1.0 for window in expected_windows}}])
    ]
