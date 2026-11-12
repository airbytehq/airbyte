#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath, create_record_builder, create_response_builder, find_template

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_STREAM_NAME = "custom_my_insight"
_TEMPLATE_NAME = "ads_insights_action_product_id"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["ad_id", "date_start", "impressions"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _job_start_request(action_attribution_windows):
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


def _job_status_response():
    body = [
        {"body": json.dumps({"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100})}
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_response():
    record = create_record_builder(
        response_template=find_template(_TEMPLATE_NAME, __file__),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("ad_id"),
    ).with_id("23854695759200548")
    return create_response_builder(response_template=find_template(_TEMPLATE_NAME, __file__), records_path=FieldPath("data")).with_record(
        record
    )


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_include_incrementality,insight_include_incrementality,expected_windows",
    [
        pytest.param(True, False, _DEFAULT_WINDOWS + ["incrementality"], id="top_level_flag_propagates_to_custom_insight"),
        pytest.param(False, True, _DEFAULT_WINDOWS + ["incrementality"], id="custom_insight_flag_only"),
        pytest.param(False, False, _DEFAULT_WINDOWS, id="disabled_everywhere"),
    ],
)
def test_custom_insight_job_requests_incrementality_window(
    top_level_include_incrementality: bool, insight_include_incrementality: bool, expected_windows: list
) -> None:
    with HttpMocker() as http_mocker:
        _mock_custom_insight_job(http_mocker, expected_windows)
        output = read_output(
            config_builder=_config(top_level_include_incrementality, insight_include_incrementality),
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
        )

    assert not output.errors
    assert [record.record.data["ad_id"] for record in output.records] == ["23854695759200548"]


def _mock_custom_insight_job(http_mocker: HttpMocker, expected_windows: list) -> None:
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
        _insights_response().build(),
    )


def _config(top_level_include_incrementality: bool, insight_include_incrementality: bool):
    config_builder = config()
    config_builder._config["include_incrementality"] = top_level_include_incrementality
    config_builder._config["custom_insights"] = [
        {
            "name": "MyInsight",
            "fields": _FIELDS,
            "breakdowns": [],
            "action_breakdowns": [],
            "include_incrementality": insight_include_incrementality,
        }
    ]
    return config_builder
