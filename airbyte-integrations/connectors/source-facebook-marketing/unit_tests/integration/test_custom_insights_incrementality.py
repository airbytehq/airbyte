#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from typing import List
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_CUSTOM_INSIGHT_NAME = "my_custom_insight"
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"  # stream names are snake-cased from "Custom<name>"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_INCREMENTALITY_WINDOW = "incrementality"


def _job_start_request(action_attribution_windows: List[str]):
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["impressions"],
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": START_DATE[:10], "until": END_DATE[:10]},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _job_status_request():
    body = {"batch": [{"method": "GET", "relative_url": f"{_REPORT_RUN_ID}/"}]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _job_status_response() -> HttpResponse:
    body = [
        {"body": json.dumps({"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": "Job Completed", "async_percent_completion": 100})}
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_download_response() -> HttpResponse:
    body = {
        "data": [
            {"account_id": ACCOUNT_ID, "ad_id": "123", "date_start": START_DATE[:10], "impressions": "10"},
        ]
    }
    return build_response(body=body, status_code=HTTPStatus.OK)


@freezegun.freeze_time("2023-01-10T00:00:00Z")
class TestCustomInsightsIncrementality(TestCase):
    """Custom insight streams must honour the top-level `include_incrementality` toggle unless set per-insight."""

    def _run(self, http_mocker: HttpMocker, top_level: bool, per_insight: bool, expected_windows: List[str]) -> None:
        custom_insight = {
            "name": _CUSTOM_INSIGHT_NAME,
            "fields": ["impressions"],
            "breakdowns": [],
            "action_breakdowns": [],
            "level": "ad",
            "include_incrementality": per_insight,
        }
        config_builder = config()
        config_builder._config["include_incrementality"] = top_level
        config_builder._config["custom_insights"] = [custom_insight]

        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(), _throttle_response()
        )
        http_mocker.post(
            _job_start_request(expected_windows).build(),
            build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK),
        )
        http_mocker.post(_job_status_request().build(), _job_status_response())
        http_mocker.get(
            RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
            _insights_download_response(),
        )

        output = read_output(
            config_builder=config_builder,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            json_schema={"properties": {"account_id": {}, "ad_id": {}, "date_start": {}, "impressions": {}}},
        )

        assert [record.record.data["ad_id"] for record in output.records] == ["123"]
        assert not output.errors

    @HttpMocker()
    def test_top_level_include_incrementality_propagates_to_custom_insight(self, http_mocker: HttpMocker) -> None:
        self._run(http_mocker, top_level=True, per_insight=False, expected_windows=_DEFAULT_WINDOWS + [_INCREMENTALITY_WINDOW])

    @HttpMocker()
    def test_per_insight_include_incrementality_is_honoured(self, http_mocker: HttpMocker) -> None:
        self._run(http_mocker, top_level=False, per_insight=True, expected_windows=_DEFAULT_WINDOWS + [_INCREMENTALITY_WINDOW])

    @HttpMocker()
    def test_incrementality_disabled_everywhere_requests_default_windows(self, http_mocker: HttpMocker) -> None:
        self._run(http_mocker, top_level=False, per_insight=False, expected_windows=_DEFAULT_WINDOWS)
