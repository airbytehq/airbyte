#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, Dict, List
from unittest import TestCase

import freezegun
from source_facebook_marketing.streams.async_job import Status

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "MyInsight"
_STREAM_NAME = "custom_my_insight"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_INSIGHT_FIELDS = ["ad_id", "impressions"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _custom_insight(include_incrementality: bool) -> Dict[str, Any]:
    return {
        "name": _INSIGHT_NAME,
        "fields": _INSIGHT_FIELDS,
        "breakdowns": [],
        "action_breakdowns": [],
        "level": "ad",
        "include_incrementality": include_incrementality,
    }


def _job_start_request(action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": _INSIGHT_FIELDS,
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _job_status_request() -> RequestBuilder:
    body = {"batch": [{"method": "GET", "relative_url": f"{_REPORT_RUN_ID}/"}]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _job_status_response() -> HttpResponse:
    body = [
        {
            "body": json.dumps(
                {"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": Status.COMPLETED, "async_percent_completion": 100}
            ),
        }
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


@freezegun.freeze_time("2023-01-10T00:00:00Z")
class TestCustomInsightsIncrementality(TestCase):
    def _assert_job_requests_windows(
        self, top_level_include_incrementality: bool, insight_include_incrementality: bool, expected_windows: List[str]
    ) -> None:
        with HttpMocker() as http_mocker:
            http_mocker.get(get_account_request().build(), get_account_response())
            http_mocker.get(
                RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(),
                _throttle_response(),
            )
            http_mocker.post(
                _job_start_request(expected_windows).build(),
                build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK),
            )
            http_mocker.post(_job_status_request().build(), _job_status_response())
            http_mocker.get(
                RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
                build_response(
                    body={
                        "data": [
                            {
                                "account_id": ACCOUNT_ID,
                                "ad_id": "1",
                                "impressions": "10",
                                "date_start": "2023-01-01",
                                "date_stop": "2023-01-01",
                            }
                        ]
                    },
                    status_code=HTTPStatus.OK,
                ),
            )

            output = read_output(
                config_builder=config()
                .with_include_incrementality(top_level_include_incrementality)
                .with_custom_insights([_custom_insight(insight_include_incrementality)]),
                stream_name=_STREAM_NAME,
                sync_mode=SyncMode.full_refresh,
            )

        assert [record.record.data["ad_id"] for record in output.records] == ["1"]

    def test_top_level_include_incrementality_applies_to_custom_insight(self) -> None:
        self._assert_job_requests_windows(True, False, _DEFAULT_WINDOWS + ["incrementality"])

    def test_custom_insight_include_incrementality_applies_without_top_level(self) -> None:
        self._assert_job_requests_windows(False, True, _DEFAULT_WINDOWS + ["incrementality"])

    def test_incrementality_omitted_when_disabled_everywhere(self) -> None:
        self._assert_job_requests_windows(False, False, _DEFAULT_WINDOWS)
