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

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "incrementality_test"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["ad_id", "date_start", "actions"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _custom_insight(include_incrementality: Optional[bool] = None) -> Dict[str, Any]:
    insight = {"name": _INSIGHT_NAME, "fields": _FIELDS, "breakdowns": [], "action_breakdowns": []}
    if include_incrementality is not None:
        insight["include_incrementality"] = include_incrementality
    return insight


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


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _job_status_response() -> HttpResponse:
    body = [
        {"body": json.dumps({"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": Status.COMPLETED, "async_percent_completion": 100})}
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_records_response() -> HttpResponse:
    body = {
        "data": [
            {
                "ad_id": "23854695759200548",
                "account_id": ACCOUNT_ID,
                "date_start": START_DATE[:10],
                "date_stop": START_DATE[:10],
                "actions": [{"action_type": "purchase", "value": "3", "1d_click": "2", "incrementality": "1"}],
            }
        ]
    }
    return build_response(body=body, status_code=HTTPStatus.OK)


@freezegun.freeze_time("2023-01-10T00:00:00Z")
class TestCustomInsightsIncludeIncrementality(TestCase):
    def _mock_job(self, http_mocker: HttpMocker, expected_windows: List[str]) -> None:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(), _throttle_response()
        )
        # The job is only matched (and the read only succeeds) if the request carries exactly `expected_windows`.
        http_mocker.post(
            _job_start_request(expected_windows).build(),
            build_response(body={"report_run_id": _REPORT_RUN_ID}, status_code=HTTPStatus.OK),
        )
        http_mocker.post(
            RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN)
            .with_body(encode_request_body({"batch": [{"method": "GET", "relative_url": f"{_REPORT_RUN_ID}/"}]}))
            .build(),
            _job_status_response(),
        )
        http_mocker.get(
            RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=_JOB_ID).with_limit(100).build(),
            _insights_records_response(),
        )

    def _read(self, top_level: Optional[bool], per_insight: Optional[bool]):
        config_builder = config()
        raw = config_builder.build()
        raw["custom_insights"] = [_custom_insight(per_insight)]
        if top_level is not None:
            raw["include_incrementality"] = top_level
        json_schema = {"properties": {field: {} for field in _FIELDS}}
        return read_output(
            config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh, json_schema=json_schema
        )

    def _assert_read(self, top_level: Optional[bool], per_insight: Optional[bool], expected_windows: List[str]) -> None:
        with HttpMocker() as http_mocker:
            self._mock_job(http_mocker, expected_windows)
            output = self._read(top_level, per_insight)

        assert not output.errors, output.errors
        assert [record.record.data["ad_id"] for record in output.records] == ["23854695759200548"]

    def test_top_level_include_incrementality_propagates_to_custom_insight(self) -> None:
        # Customer scenario: toggle enabled at the source level, per-insight value left at its default (false).
        self._assert_read(top_level=True, per_insight=False, expected_windows=_DEFAULT_WINDOWS + ["incrementality"])

    def test_top_level_include_incrementality_propagates_when_insight_omits_flag(self) -> None:
        self._assert_read(top_level=True, per_insight=None, expected_windows=_DEFAULT_WINDOWS + ["incrementality"])

    def test_per_insight_include_incrementality_still_honored(self) -> None:
        self._assert_read(top_level=False, per_insight=True, expected_windows=_DEFAULT_WINDOWS + ["incrementality"])

    def test_incrementality_not_requested_when_disabled_everywhere(self) -> None:
        self._assert_read(top_level=False, per_insight=False, expected_windows=_DEFAULT_WINDOWS)
