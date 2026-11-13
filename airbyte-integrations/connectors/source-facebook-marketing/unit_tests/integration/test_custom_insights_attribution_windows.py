#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from typing import Any, Dict, List

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import find_template

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
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


_INSIGHT_NAME = "my_insight"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _custom_insight_job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["actions", "spend"],
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level_config, insight_config, expected_windows",
    [
        pytest.param({}, {}, _DEFAULT_WINDOWS, id="disabled_everywhere_sends_default_windows"),
        pytest.param(
            {"include_incrementality": True},
            {},
            [*_DEFAULT_WINDOWS, "incrementality"],
            id="top_level_toggle_applies_to_custom_insight",
        ),
        pytest.param(
            {},
            {"include_incrementality": True},
            [*_DEFAULT_WINDOWS, "incrementality"],
            id="custom_insight_toggle_alone_still_applies",
        ),
    ],
)
def test_custom_insight_job_requests_configured_attribution_windows(
    top_level_config: Dict[str, Any], insight_config: Dict[str, Any], expected_windows: List[str]
) -> None:
    config_builder = config()
    config_builder._config.update(top_level_config)
    config_builder._config["custom_insights"] = [{"name": _INSIGHT_NAME, "fields": ["actions", "spend"], **insight_config}]
    record = {"account_id": ACCOUNT_ID, "ad_id": "ad_1", "date_start": START_DATE[:10], "date_stop": START_DATE[:10], "spend": 1.5}

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        # The job is only started when the request body matches exactly, including `action_attribution_windows`.
        http_mocker.post(_custom_insight_job_start_request(expected_windows).build(), _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(_get_insights_request(_JOB_ID).build(), build_response(body={"data": [record]}, status_code=HTTPStatus.OK))

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    assert [(r.record.stream, r.record.data["ad_id"], r.record.data["date_start"]) for r in output.records] == [
        (_STREAM_NAME, "ad_1", START_DATE[:10])
    ]
