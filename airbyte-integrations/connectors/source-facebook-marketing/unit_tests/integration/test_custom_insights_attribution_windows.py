#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from typing import List

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ACCESS_TOKEN, ACCOUNT_ID, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .test_ads_insights_action_product_id import (
    _get_insights_request,
    _job_start_response,
    _job_status_request,
    _job_status_response,
    _update_api_throttle_limit_request,
    _update_api_throttle_limit_response,
)
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "test_insight"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _custom_insight_job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["impressions"],
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": START_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_include_incrementality, insight_include_incrementality, expected_windows",
    [
        pytest.param(True, False, _DEFAULT_WINDOWS + ["incrementality"], id="top_level_flag_propagates_to_custom_insight"),
        pytest.param(False, True, _DEFAULT_WINDOWS + ["incrementality"], id="per_insight_flag"),
        pytest.param(False, False, _DEFAULT_WINDOWS, id="flag_disabled"),
    ],
)
def test_custom_insight_job_requests_incrementality_window(
    top_level_include_incrementality: bool, insight_include_incrementality: bool, expected_windows: List[str]
) -> None:
    config_builder = config()
    config_builder._config["include_incrementality"] = top_level_include_incrementality
    config_builder._config["custom_insights"] = [
        {
            "name": _INSIGHT_NAME,
            "fields": ["impressions"],
            "breakdowns": [],
            "action_breakdowns": [],
            "level": "ad",
            "time_increment": 1,
            "include_incrementality": insight_include_incrementality,
        }
    ]

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        http_mocker.post(_custom_insight_job_start_request(expected_windows).build(), _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            build_response(
                body={
                    "data": [
                        {"account_id": ACCOUNT_ID, "ad_id": "1", "date_start": "2023-01-01", "date_stop": "2023-01-01", "impressions": "10"}
                    ]
                },
                status_code=HTTPStatus.OK,
            ),
        )

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    assert [(record.record.data["ad_id"], record.record.data["impressions"]) for record in output.records] == [("1", 10)]
