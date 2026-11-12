#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
import pytest
from source_facebook_marketing.streams.async_job import Status

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponse,
    create_record_builder,
    create_response_builder,
    find_template,
)

from .config import ACCESS_TOKEN, ACCOUNT_ID, END_DATE, START_DATE, ConfigBuilder
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_CUSTOM_INSIGHT_NAME = "my_custom_insight"
_STREAM_NAME = "custommy_custom_insight"  # f"Custom{name}" camel_to_snake-cased by the stream
_TEMPLATE_NAME = "ads_insights_action_product_id"
_REPORT_RUN_ID = "1571860060019548"
_JOB_ID = "1049937379601625"
_FIELDS = ["ad_id", "clicks", "impressions"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _custom_insight(include_incrementality: Optional[bool]) -> Dict[str, Any]:
    insight = {
        "name": _CUSTOM_INSIGHT_NAME,
        "level": "ad",
        "fields": _FIELDS,
        "breakdowns": [],
        "action_breakdowns": [],
        "time_increment": 1,
    }
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
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"})
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _job_status_response() -> HttpResponse:
    body = [
        {"body": json.dumps({"id": _JOB_ID, "account_id": ACCOUNT_ID, "async_status": Status.COMPLETED, "async_percent_completion": 100})}
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_response() -> HttpResponse:
    record = create_record_builder(
        response_template=find_template(_TEMPLATE_NAME, __file__),
        records_path=FieldPath("data"),
        record_cursor_path=FieldPath("date_start"),
    )
    return (
        create_response_builder(response_template=find_template(_TEMPLATE_NAME, __file__), records_path=FieldPath("data"))
        .with_record(record)
        .build()
    )


@freezegun.freeze_time("2023-01-10T00:00:00Z")
class TestCustomInsightsIncludeIncrementality(TestCase):
    def _read(self, config_: ConfigBuilder) -> EntrypointOutput:
        return read_output(config_builder=config_, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    def _run(self, top_level: Optional[bool], per_insight: Optional[bool], expected_windows: List[str]) -> None:
        config_ = config().with_custom_insights([_custom_insight(per_insight)])
        if top_level is not None:
            config_ = config_.with_include_incrementality(top_level)

        with HttpMocker() as http_mocker:
            http_mocker.get(get_account_request().build(), get_account_response())
            http_mocker.get(
                RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(), _throttle_response()
            )
            # The job start request only matches when the body carries exactly `expected_windows`.
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
                _insights_response(),
            )

            output = self._read(config_)

        assert [r.record.stream for r in output.records] == [_STREAM_NAME]
        assert not output.errors

    def test_top_level_include_incrementality_propagates_to_custom_insight(self) -> None:
        self._run(top_level=True, per_insight=None, expected_windows=_DEFAULT_WINDOWS + ["incrementality"])

    def test_per_insight_include_incrementality_still_applies_without_top_level(self) -> None:
        self._run(top_level=False, per_insight=True, expected_windows=_DEFAULT_WINDOWS + ["incrementality"])

    def test_include_incrementality_disabled_everywhere_requests_default_windows(self) -> None:
        self._run(top_level=None, per_insight=None, expected_windows=_DEFAULT_WINDOWS)
