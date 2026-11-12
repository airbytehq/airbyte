#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from source_facebook_marketing.streams.async_job import Status

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE, ConfigBuilder
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_CUSTOM_INSIGHT_NAME = "my_custom_insight"
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["ad_id", "date_start", "impressions"]
_BASE_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_INCREMENTALITY_WINDOWS = _BASE_WINDOWS + ["incrementality"]


def _config(top_level_incrementality: Optional[bool], custom_insight_incrementality: Optional[bool]) -> ConfigBuilder:
    builder = config()
    custom_insight: Dict[str, Any] = {
        "name": _CUSTOM_INSIGHT_NAME,
        "fields": _FIELDS,
        "breakdowns": [],
        "action_breakdowns": [],
        "level": "ad",
        "time_increment": 1,
    }
    if custom_insight_incrementality is not None:
        custom_insight["include_incrementality"] = custom_insight_incrementality
    builder._config["custom_insights"] = [custom_insight]
    if top_level_incrementality is not None:
        builder._config["include_incrementality"] = top_level_incrementality
    return builder


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


def _job_start_response() -> HttpResponse:
    return build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK)


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


def _insights_response() -> HttpResponse:
    body = {
        "data": [
            {
                "account_id": ACCOUNT_ID,
                "ad_id": "120203000000000001",
                "date_start": START_DATE[:10],
                "date_stop": START_DATE[:10],
                "impressions": "42",
            }
        ]
    }
    return build_response(body=body, status_code=HTTPStatus.OK)


@freezegun.freeze_time("2023-01-10T00:00:00Z")
class TestCustomInsightsIncrementality(TestCase):
    def _run(self, top_level: Optional[bool], per_insight: Optional[bool], expected_windows: List[str]) -> None:
        with HttpMocker() as http_mocker:
            http_mocker.get(get_account_request().build(), get_account_response())
            http_mocker.get(
                RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(), _throttle_response()
            )
            http_mocker.post(_job_start_request(expected_windows).build(), _job_start_response())
            http_mocker.post(_job_status_request().build(), _job_status_response())
            http_mocker.get(
                RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
                _insights_response(),
            )

            output = read_output(
                config_builder=_config(top_level, per_insight),
                stream_name=_STREAM_NAME,
                sync_mode=SyncMode.full_refresh,
            )

        assert not output.errors, output.errors
        assert [record.record.data["ad_id"] for record in output.records] == ["120203000000000001"]

    def test_top_level_include_incrementality_propagates_to_custom_insight(self) -> None:
        """Top-level include_incrementality=true must add the incrementality window to custom insight job requests
        when the custom insight entry does not set the flag itself."""
        self._run(top_level=True, per_insight=None, expected_windows=_INCREMENTALITY_WINDOWS)

    def test_custom_insight_include_incrementality_without_top_level(self) -> None:
        self._run(top_level=False, per_insight=True, expected_windows=_INCREMENTALITY_WINDOWS)

    def test_no_incrementality_when_neither_flag_set(self) -> None:
        self._run(top_level=None, per_insight=None, expected_windows=_BASE_WINDOWS)
