#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Dict, List

import freezegun
import pytest
from source_facebook_marketing.streams.async_job import Status

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID, DATE_FORMAT, NOW
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "incrementality_report"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_FIELDS = ["account_id", "actions", "ad_id", "date_start"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _job_start_request(day: datetime, action_attribution_windows: List[str]) -> RequestBuilder:
    body = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": _FIELDS,
        "time_increment": 1,
        "action_attribution_windows": action_attribution_windows,
        "time_range": {"since": day.strftime(DATE_FORMAT), "until": day.strftime(DATE_FORMAT)},
    }
    return RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).with_body(encode_request_body(body))


def _job_status_request(report_run_ids: List[str]) -> RequestBuilder:
    body = {"batch": [{"method": "GET", "relative_url": f"{report_run_id}/"} for report_run_id in report_run_ids]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _job_status_response(job_ids: List[str]) -> HttpResponse:
    body = [
        {"body": json.dumps({"id": job_id, "account_id": ACCOUNT_ID, "async_status": Status.COMPLETED, "async_percent_completion": 100})}
        for job_id in job_ids
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"})
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _insights_response(ad_id: str, day: datetime) -> HttpResponse:
    record = {
        "account_id": ACCOUNT_ID,
        "ad_id": ad_id,
        "date_start": day.strftime(DATE_FORMAT),
        "date_stop": day.strftime(DATE_FORMAT),
    }
    return build_response(body={"data": [record]}, status_code=HTTPStatus.OK)


@freezegun.freeze_time(NOW.isoformat())
@pytest.mark.parametrize(
    "top_level_config, custom_insight_config, expected_windows",
    [
        pytest.param({"include_incrementality": True}, {}, [*_DEFAULT_WINDOWS, "incrementality"], id="top_level_toggle_only"),
        pytest.param(
            {"include_incrementality": True},
            {"include_incrementality": False},
            [*_DEFAULT_WINDOWS, "incrementality"],
            id="top_level_toggle_with_custom_insight_default_false",
        ),
        pytest.param({}, {"include_incrementality": True}, [*_DEFAULT_WINDOWS, "incrementality"], id="custom_insight_toggle_only"),
        pytest.param({}, {}, _DEFAULT_WINDOWS, id="no_toggle"),
    ],
)
def test_custom_insight_job_requests_include_incrementality_window_from_either_toggle(
    top_level_config: Dict[str, Any], custom_insight_config: Dict[str, Any], expected_windows: List[str]
) -> None:
    """
    A custom insight stream must request the `incrementality` attribution window when either the
    source-level `include_incrementality` toggle or the custom insight's own toggle is enabled.
    """
    days = [NOW - timedelta(days=1), NOW]
    report_run_ids = ["1571860060019500", "4571860060019599"]
    job_ids = ["1049937379601600", "1049937379601699"]
    ad_ids = ["ad_1", "ad_2"]

    config_builder = config().with_start_date(days[0]).with_end_date(days[1])
    config_builder.build().update(
        {
            **top_level_config,
            "custom_insights": [{"name": _INSIGHT_NAME, "fields": _FIELDS, "level": "ad", **custom_insight_config}],
        }
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(),
            _throttle_response(),
        )
        job_start_requests = [_job_start_request(day, expected_windows).build() for day in days]
        for job_start_request, report_run_id in zip(job_start_requests, report_run_ids):
            http_mocker.post(job_start_request, build_response(body={"report_run_id": report_run_id}, status_code=HTTPStatus.OK))
        http_mocker.post(_job_status_request(report_run_ids).build(), _job_status_response(job_ids))
        for job_id, ad_id, day in zip(job_ids, ad_ids, days):
            http_mocker.get(
                RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=job_id).with_limit(100).build(),
                _insights_response(ad_id, day),
            )

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

        assert [record.record.data["ad_id"] for record in output.records] == ad_ids
        for job_start_request in job_start_requests:
            http_mocker.assert_number_of_calls(job_start_request, 1)
