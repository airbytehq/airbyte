#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import List
from unittest import TestCase

import freezegun
from source_facebook_marketing.streams.async_job import Status

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponse,
    create_record_builder,
    create_response_builder,
    find_template,
)

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .pagination import NEXT_PAGE_TOKEN, FacebookMarketingPaginationStrategy
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "MyInsight"
_STREAM_NAME = "custom_my_insight"
_TEMPLATE_NAME = "ads_insights_action_product_id"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["ad_id", "clicks", "actions"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


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


def _job_status_request() -> RequestBuilder:
    body = {"batch": [{"method": "GET", "relative_url": f"{_REPORT_RUN_ID}/"}]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _get_insights_request() -> RequestBuilder:
    return RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100)


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"})
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _job_status_response() -> HttpResponse:
    body = [
        {"body": json.dumps({"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": Status.COMPLETED, "async_percent_completion": 100})}
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_response() -> HttpResponse:
    response_builder = create_response_builder(
        response_template=find_template(_TEMPLATE_NAME, __file__),
        records_path=FieldPath("data"),
        pagination_strategy=FacebookMarketingPaginationStrategy(request=_get_insights_request().build(), next_page_token=NEXT_PAGE_TOKEN),
    )
    record = create_record_builder(
        response_template=find_template(_TEMPLATE_NAME, __file__),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("ad_id"),
    ).with_id("120201234567890")
    return response_builder.with_record(record).build()


@freezegun.freeze_time("2023-01-10T00:00:00Z")
class TestCustomInsightsAttributionWindows(TestCase):
    def _read_with(
        self, http_mocker: HttpMocker, top_level_incrementality: bool, insight_incrementality: bool, expected_windows: List[str]
    ):
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(), _throttle_response()
        )
        http_mocker.post(
            _job_start_request(expected_windows).build(),
            build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK),
        )
        http_mocker.post(_job_status_request().build(), _job_status_response())
        http_mocker.get(_get_insights_request().build(), _insights_response())

        config_builder = config()
        config_builder._config["include_incrementality"] = top_level_incrementality
        config_builder._config["custom_insights"] = [
            {
                "name": _INSIGHT_NAME,
                "level": "ad",
                "fields": _FIELDS,
                "breakdowns": [],
                "action_breakdowns": [],
                "time_increment": 1,
                "include_incrementality": insight_incrementality,
            }
        ]
        return read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    @HttpMocker()
    def test_top_level_include_incrementality_propagates_to_custom_insight(self, http_mocker: HttpMocker) -> None:
        output = self._read_with(
            http_mocker, top_level_incrementality=True, insight_incrementality=False, expected_windows=_DEFAULT_WINDOWS + ["incrementality"]
        )

        assert [record.record.data["ad_id"] for record in output.records] == ["120201234567890"]

    @HttpMocker()
    def test_custom_insight_include_incrementality_without_top_level(self, http_mocker: HttpMocker) -> None:
        output = self._read_with(
            http_mocker, top_level_incrementality=False, insight_incrementality=True, expected_windows=_DEFAULT_WINDOWS + ["incrementality"]
        )

        assert [record.record.data["ad_id"] for record in output.records] == ["120201234567890"]

    @HttpMocker()
    def test_no_incrementality_when_disabled_everywhere(self, http_mocker: HttpMocker) -> None:
        output = self._read_with(
            http_mocker, top_level_incrementality=False, insight_incrementality=False, expected_windows=_DEFAULT_WINDOWS
        )

        assert [record.record.data["ad_id"] for record in output.records] == ["120201234567890"]
