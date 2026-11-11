#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ACCESS_TOKEN, ACCOUNT_ID
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


@pytest.mark.parametrize(
    "top_level,custom,expected_windows",
    [
        (True, None, ["1d_click", "7d_click", "28d_click", "1d_view", "incrementality"]),
        (False, True, ["1d_click", "7d_click", "28d_click", "1d_view", "incrementality"]),
        (False, False, ["1d_click", "7d_click", "28d_click", "1d_view"]),
    ],
    ids=["top-level-inherited", "custom-enabled", "both-disabled"],
)
@freezegun.freeze_time("2023-01-10T00:00:00Z")
def test_custom_insights_incrementality(top_level, custom, expected_windows):
    config_builder = config()
    insight = {"name": "my_insight", "fields": ["ad_id", "impressions"], "level": "ad"}
    if custom is not None:
        insight["include_incrementality"] = custom
    config_builder.build().update(include_incrementality=top_level, custom_insights=[insight])
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["ad_id", "impressions"],
        "time_increment": 1,
        "action_attribution_windows": expected_windows,
        "time_range": {"since": "2023-01-01", "until": "2023-01-01"},
    }
    record = {"ad_id": "123", "impressions": "42", "date_start": "2023-01-01", "date_stop": "2023-01-01"}
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        job_start_request = (
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID)
            .with_body(encode_request_body(body))
            .build()
        )
        http_mocker.post(job_start_request, _job_start_response("report-id"))
        http_mocker.post(_job_status_request("report-id").build(), _job_status_response("job-id"))
        http_mocker.get(_get_insights_request("job-id").build(), build_response(body={"data": [record]}, status_code=HTTPStatus.OK))

        output = read_output(config_builder, "custommy_insight", SyncMode.full_refresh)
        http_mocker.assert_number_of_calls(job_start_request, 1)
        assert [message.record.data for message in output.records] == [{**record, "impressions": 42, "account_id": ACCOUNT_ID}]
