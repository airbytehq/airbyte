#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from typing import List

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath, create_record_builder, create_response_builder, find_template

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import get_account_response
from .test_ads_insights_action_product_id import (
    _get_insights_request,
    _job_start_response,
    _job_status_request,
    _job_status_response,
    _update_api_throttle_limit_request,
    _update_api_throttle_limit_response,
)
from .utils import config, encode_request_body, read_output


_CUSTOM_INSIGHT_NAME = "my_custom_insight"
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"
_FIELDS = ["account_id", "ad_id", "actions", "date_start", "date_stop"]
_RECORD_TEMPLATE = "ads_insights_action_product_id"
_BASE_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_WINDOWS_WITH_INCREMENTALITY = [*_BASE_WINDOWS, "incrementality"]


def _job_start_request(report_run_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": _FIELDS,
        "time_increment": 1,
        "action_attribution_windows": report_run_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


@pytest.mark.parametrize(
    "source_level_flag, custom_insight_flag, expected_windows",
    [
        pytest.param(True, None, _WINDOWS_WITH_INCREMENTALITY, id="source_level_on_custom_insight_unset_inherits"),
        pytest.param(True, False, _WINDOWS_WITH_INCREMENTALITY, id="source_level_on_custom_insight_default_false_inherits"),
        pytest.param(False, True, _WINDOWS_WITH_INCREMENTALITY, id="custom_insight_on_without_source_level"),
        pytest.param(False, False, _BASE_WINDOWS, id="both_off_sends_no_incrementality_window"),
    ],
)
@freezegun.freeze_time("2023-01-10T00:00:00Z")
def test_custom_insight_report_request_honors_source_level_include_incrementality(
    source_level_flag: bool, custom_insight_flag, expected_windows: List[str]
) -> None:
    """
    The report job a custom insight stream starts must ask Facebook for the `incrementality` attribution window
    when either the source-level or the custom insight's own "Include Incrementality" option is enabled.
    The mocked job-start request matches on the exact body, so a wrong window list fails the read.
    """
    custom_insight = {"name": _CUSTOM_INSIGHT_NAME, "fields": _FIELDS}
    if custom_insight_flag is not None:
        custom_insight["include_incrementality"] = custom_insight_flag
    config_builder = config()
    config_builder._config["include_incrementality"] = source_level_flag
    config_builder._config["custom_insights"] = [custom_insight]

    record = create_record_builder(
        response_template=find_template(_RECORD_TEMPLATE, __file__),
        records_path=FieldPath("data"),
    )
    insights_response = create_response_builder(
        response_template=find_template(_RECORD_TEMPLATE, __file__),
        records_path=FieldPath("data"),
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        http_mocker.post(_job_start_request(expected_windows).build(), _job_start_response("1571860060019548"))
        http_mocker.post(_job_status_request("1571860060019548").build(), _job_status_response("1049937379601625"))
        http_mocker.get(_get_insights_request("1049937379601625").build(), insights_response.with_record(record).build())

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    assert output.errors == []
    assert len(output.records) == 1
