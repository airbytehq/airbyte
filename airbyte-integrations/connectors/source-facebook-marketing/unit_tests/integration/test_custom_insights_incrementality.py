#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


from http import HTTPStatus
from typing import Any, Dict, List, Optional

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

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


_CUSTOM_INSIGHT_NAME = "incrementality_report"
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_BASE_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_RECORD = {
    "account_id": ACCOUNT_ID,
    "ad_id": "23846765228310398",
    "date_start": START_DATE[:10],
    "date_stop": START_DATE[:10],
}


def _job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["account_id", "ad_id", "actions"],
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _config(source_level: Optional[bool], insight_level: Optional[bool]):
    custom_insight: Dict[str, Any] = {
        "name": _CUSTOM_INSIGHT_NAME,
        "level": "ad",
        "fields": ["account_id", "ad_id", "actions"],
        "breakdowns": [],
        "action_breakdowns": [],
    }
    if insight_level is not None:
        custom_insight["include_incrementality"] = insight_level
    builder = config()
    builder._config["custom_insights"] = [custom_insight]
    if source_level is not None:
        builder._config["include_incrementality"] = source_level
    return builder


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "source_level,insight_level,expected_windows",
    [
        pytest.param(True, None, _BASE_WINDOWS + ["incrementality"], id="source_level_only_propagates_to_custom_insight"),
        pytest.param(True, False, _BASE_WINDOWS + ["incrementality"], id="source_level_wins_over_insight_default_false"),
        pytest.param(False, True, _BASE_WINDOWS + ["incrementality"], id="insight_level_only_still_enables"),
        pytest.param(None, None, _BASE_WINDOWS, id="neither_set_keeps_default_windows"),
        pytest.param(False, False, _BASE_WINDOWS, id="both_disabled_keeps_default_windows"),
    ],
)
def test_custom_insight_job_requests_incrementality_window_when_enabled_at_either_level(
    source_level: Optional[bool], insight_level: Optional[bool], expected_windows: List[str]
) -> None:
    """
    The async insights job for a custom insight stream must request the `incrementality` attribution
    window when `include_incrementality` is enabled on the source config or on the custom insight entry.
    HttpMocker only matches the job-start POST with the exact expected body, so a wrong window list fails the read.
    """
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        http_mocker.post(_job_start_request(expected_windows).build(), _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            build_response(body={"data": [_RECORD]}, status_code=HTTPStatus.OK),
        )

        output = read_output(config_builder=_config(source_level, insight_level), stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    assert output.errors == []
    assert [record.record.data["ad_id"] for record in output.records] == [_RECORD["ad_id"]]
