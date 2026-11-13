#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE, ConfigBuilder
from .request_builder import RequestBuilder, get_account_request
from .response_builder import get_account_response
from .test_ads_insights_action_product_id import (
    _JOB_ID,
    _REPORT_RUN_ID,
    _ads_insights_action_product_id_record,
    _get_insights_request,
    _insights_response,
    _job_start_response,
    _job_status_request,
    _job_status_response,
    _update_api_throttle_limit_request,
    _update_api_throttle_limit_response,
)
from .utils import encode_request_body, read_output


@pytest.mark.parametrize(
    "top_level,custom,expected_incrementality",
    [(True, None, True), (True, False, True), (False, True, True), (False, False, False)],
)
@freezegun.freeze_time("2023-01-10T00:00:00Z")
def test_custom_insights_incrementality(top_level, custom, expected_incrementality):
    config_builder = ConfigBuilder()
    custom_insight = {"name": "Incrementality", "fields": ["ad_id", "date_start", "date_stop"], "breakdowns": ["product_id"]}
    if custom is not None:
        custom_insight["include_incrementality"] = custom
    config_builder.build().update(include_incrementality=top_level, custom_insights=[custom_insight])
    windows = ["1d_click", "7d_click", "28d_click", "1d_view"]
    if expected_incrementality:
        windows.append("incrementality")
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": ["product_id"],
        "fields": custom_insight["fields"],
        "time_increment": 1,
        "action_attribution_windows": windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    job_request = (
        RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID)
        .with_body(encode_request_body(body))
        .build()
    )
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        http_mocker.post(job_request, _job_start_response(_REPORT_RUN_ID))
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )
        output = read_output(config_builder, "custom_incrementality", SyncMode.full_refresh)
        http_mocker.assert_number_of_calls(job_request, 1)
        assert len(output.records) == 1
