#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from typing import Any, Dict, List

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponse,
    create_record_builder,
    create_response_builder,
    find_template,
)

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE, ConfigBuilder
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "incrementality_test"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_TEMPLATE_NAME = "ads_insights_action_product_id"
_CUSTOM_FIELDS = ["account_id", "ad_id", "date_start", "impressions"]
_BASE_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _config_with_custom_insight(top_level_incrementality: bool, insight_incrementality: bool) -> ConfigBuilder:
    builder = config()
    raw = builder.build()
    raw["include_incrementality"] = top_level_incrementality
    raw["custom_insights"] = [
        {
            "name": _INSIGHT_NAME,
            "fields": _CUSTOM_FIELDS,
            "breakdowns": [],
            "action_breakdowns": [],
            "level": "ad",
            "time_increment": 1,
            "include_incrementality": insight_incrementality,
        }
    ]
    return builder


def _job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body: Dict[str, Any] = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": _CUSTOM_FIELDS,
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


def _insights_records_response() -> HttpResponse:
    record = create_record_builder(
        response_template=find_template(_TEMPLATE_NAME, __file__),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("ad_id"),
    ).with_id("ad_1")
    return (
        create_response_builder(response_template=find_template(_TEMPLATE_NAME, __file__), records_path=FieldPath("data"))
        .with_record(record)
        .build()
    )


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_incrementality,insight_incrementality,expected_windows",
    [
        pytest.param(True, False, _BASE_WINDOWS + ["incrementality"], id="top_level_flag_propagates_to_custom_insight"),
        pytest.param(False, True, _BASE_WINDOWS + ["incrementality"], id="per_insight_flag_still_honoured"),
        pytest.param(False, False, _BASE_WINDOWS, id="both_disabled_no_incrementality_window"),
    ],
)
def test_custom_insight_job_request_action_attribution_windows(
    top_level_incrementality: bool, insight_incrementality: bool, expected_windows: List[str]
) -> None:
    """The async insights job for a custom insight must request the `incrementality` attribution window whenever
    either the top-level `include_incrementality` flag or the custom insight's own flag is enabled."""
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(), _throttle_response()
        )
        http_mocker.post(
            _job_start_request(expected_windows).build(), build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK)
        )
        http_mocker.post(_job_status_request().build(), _job_status_response())
        http_mocker.get(
            RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
            _insights_records_response(),
        )

        output = read_output(
            config_builder=_config_with_custom_insight(top_level_incrementality, insight_incrementality),
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
        )

    assert [record.record.data["ad_id"] for record in output.records] == ["ad_1"]
    assert not output.errors
