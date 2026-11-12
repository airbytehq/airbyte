#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from urllib.parse import parse_qs

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ACCESS_TOKEN, ACCOUNT_ID
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
from .utils import config, read_output


@pytest.mark.parametrize("include_incrementality", [True, False])
@freezegun.freeze_time("2023-01-10T00:00:00Z")
def test_custom_insights_inherit_top_level_incrementality(include_incrementality: bool) -> None:
    config_builder = config()
    config_builder.build().update(
        {
            "include_incrementality": include_incrementality,
            "custom_insights": [{"name": "Products", "fields": ["ad_id", "date_start"], "breakdowns": ["product_id"]}],
        }
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        job_request = RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build()
        http_mocker._mocker.post(job_request._parsed_url.geturl(), text=_job_start_response(_REPORT_RUN_ID).body)
        http_mocker.post(_job_status_request(_REPORT_RUN_ID).build(), _job_status_response(_JOB_ID))
        http_mocker.get(
            _get_insights_request(_JOB_ID).build(),
            _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
        )

        output = read_output(config_builder, stream_name="custom_products", sync_mode=SyncMode.full_refresh)

        job_requests = [
            request
            for request in http_mocker._mocker.request_history
            if request.method == "POST" and request.path.endswith(f"/act_{ACCOUNT_ID}/insights")
        ]
        assert len(job_requests) == 1
        assert len(output.records) == 1
        assert output.records[0].record.stream == "custom_products"
        attribution_windows = json.loads(parse_qs(job_requests[0].text)["action_attribution_windows"][0])
        assert ("incrementality" in attribution_windows) is include_incrementality
