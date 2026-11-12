#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import freezegun
import pytest
from source_facebook_marketing.streams.async_job import Status

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath, create_record_builder, create_response_builder, find_template

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_CUSTOM_INSIGHT_NAME = "my_insight"
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"
_TEMPLATE_NAME = "ads_insights_action_product_id"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["account_id", "ad_id", "date_start", "impressions"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _custom_insight(include_incrementality: Optional[bool] = None) -> Dict[str, Any]:
    insight = {
        "name": _CUSTOM_INSIGHT_NAME,
        "fields": _FIELDS,
        "breakdowns": [],
        "action_breakdowns": [],
        "level": "ad",
    }
    if include_incrementality is not None:
        insight["include_incrementality"] = include_incrementality
    return insight


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
        {"body": json.dumps({"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": Status.COMPLETED, "async_percent_completion": 100})}
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_response() -> HttpResponse:
    record = create_record_builder(
        response_template=find_template(_TEMPLATE_NAME, __file__),
        records_path=FieldPath("data"),
        record_cursor_path=FieldPath("date_start"),
    )
    return (
        create_response_builder(response_template=find_template(_TEMPLATE_NAME, __file__), records_path=FieldPath("data"))
        .with_record(record)
        .build()
    )


def _mock_job(http_mocker: HttpMocker, expected_windows: List[str]) -> None:
    http_mocker.get(get_account_request().build(), get_account_response())
    http_mocker.get(RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(), _throttle_response())
    http_mocker.post(
        _job_start_request(expected_windows).build(),
        build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK),
    )
    batch_body = {"batch": [{"method": "GET", "relative_url": f"{_REPORT_RUN_ID}/"}]}
    http_mocker.post(
        RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(batch_body)).build(),
        _job_status_response(),
    )
    http_mocker.get(
        RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
        _insights_response(),
    )


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_include_incrementality,custom_insight_include_incrementality,expected_windows",
    [
        pytest.param(True, None, _DEFAULT_WINDOWS + ["incrementality"], id="top_level_enabled_propagates_to_custom_insight"),
        pytest.param(False, True, _DEFAULT_WINDOWS + ["incrementality"], id="custom_insight_enabled"),
        pytest.param(None, None, _DEFAULT_WINDOWS, id="disabled_everywhere"),
    ],
)
def test_custom_insight_job_requests_incrementality_window(
    top_level_include_incrementality: Optional[bool],
    custom_insight_include_incrementality: Optional[bool],
    expected_windows: List[str],
) -> None:
    """The async job for a custom insight must request the `incrementality` attribution window when it is enabled
    either on the custom insight itself or via the top-level `include_incrementality` toggle."""
    with HttpMocker() as http_mocker:
        # The job-start POST is only mocked for a body carrying exactly `expected_windows`;
        # any other action_attribution_windows value makes the read fail with "No mock address".
        _mock_job(http_mocker, expected_windows)
        config_ = config().with_custom_insights([_custom_insight(custom_insight_include_incrementality)])
        if top_level_include_incrementality is not None:
            config_ = config_.with_include_incrementality(top_level_include_incrementality)

        json_schema = {"properties": {field: {"type": ["null", "string"]} for field in _FIELDS}}
        output: EntrypointOutput = read_output(
            config_builder=config_, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh, json_schema=json_schema
        )

    assert not output.errors, output.errors
    assert [record.record.stream for record in output.records] == [_STREAM_NAME]
