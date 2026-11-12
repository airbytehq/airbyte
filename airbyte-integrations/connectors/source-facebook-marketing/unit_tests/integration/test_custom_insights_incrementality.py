#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, Dict, List

import freezegun
import pytest
from source_facebook_marketing.streams.async_job import Status

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE, ConfigBuilder
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import encode_request_body, read_output


_CUSTOM_INSIGHT_NAME = "my_custom_insight"
# Custom insight streams are named `Custom<name>` and then snake-cased by the stream `name` property.
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["account_id", "ad_id", "date_start", "impressions", "actions"]
_BASE_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
def _config(top_level_incrementality: bool, custom_insight_incrementality: bool) -> ConfigBuilder:
    builder = ConfigBuilder()
    config = builder.build()
    config["include_incrementality"] = top_level_incrementality
    config["custom_insights"] = [
        {
            "name": _CUSTOM_INSIGHT_NAME,
            "fields": _FIELDS,
            "breakdowns": [],
            "action_breakdowns": [],
            "level": "ad",
            "include_incrementality": custom_insight_incrementality,
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


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _job_status_response() -> HttpResponse:
    body = [
        {
            "body": json.dumps(
                {"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": Status.COMPLETED, "async_percent_completion": 100}
            )
        }
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_response() -> HttpResponse:
    record = {
        "account_id": ACCOUNT_ID,
        "ad_id": "120200000000000001",
        "date_start": START_DATE[:10],
        "date_stop": START_DATE[:10],
        "impressions": "100",
        "actions": [{"action_type": "purchase", "value": "3", "1d_click": "2", "incrementality": "1"}],
    }
    return build_response(body={"data": [record]}, status_code=HTTPStatus.OK)


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_incrementality,custom_insight_incrementality,expected_windows",
    [
        pytest.param(False, False, _BASE_WINDOWS, id="disabled_everywhere"),
        pytest.param(True, False, _BASE_WINDOWS + ["incrementality"], id="top_level_enabled_falls_back_to_custom_insight"),
        pytest.param(False, True, _BASE_WINDOWS + ["incrementality"], id="custom_insight_enabled"),
    ],
)
def test_custom_insight_job_requests_incrementality_window(
    top_level_incrementality: bool, custom_insight_incrementality: bool, expected_windows: List[str]
) -> None:
    """
    The top-level `include_incrementality` toggle must propagate to custom insight streams
    (falling back the same way `insights_lookback_window` / `insights_job_timeout` do), so the
    async insights job is started with the `incrementality` action attribution window.
    """
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(), _throttle_response())
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

        output = read_output(
            config_builder=_config(top_level_incrementality, custom_insight_incrementality),
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
        )

    assert [record.record.data["ad_id"] for record in output.records] == ["120200000000000001"]
    assert output.records[0].record.stream == _STREAM_NAME
