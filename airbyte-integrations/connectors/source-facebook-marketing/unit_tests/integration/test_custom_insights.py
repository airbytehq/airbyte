#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import freezegun
import pytest
from source_facebook_marketing.streams.async_job import Status

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import HttpResponse

from .config import ACCESS_TOKEN, ACCOUNT_ID, DATE_FORMAT, NOW, ConfigBuilder
from .request_builder import RequestBuilder, get_account_request
from .response_builder import build_response, get_account_response
from .utils import config, encode_request_body, read_output


_CUSTOM_INSIGHT_NAME = "my_report"
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"
_FIELDS = ["account_id", "ad_id", "spend", "actions"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]
_WINDOWS_WITH_INCREMENTALITY = [*_DEFAULT_WINDOWS, "incrementality"]
_FIRST_DAY = NOW - timedelta(days=1)
_SECOND_DAY = NOW
# One report job per daily slice: (report_run_id, job_id, ad_id of the record the job returns)
_JOBS_BY_DAY = {
    _FIRST_DAY: ("1571860060019500", "1049937379601600", "ad_first_day"),
    _SECOND_DAY: ("4571860060019599", "1049937379601699", "ad_second_day"),
}


def _config(top_level: Optional[bool], per_insight: Optional[bool]) -> ConfigBuilder:
    """Build a config with one custom insight, leaving `include_incrementality` unset wherever `None` is given."""
    custom_insight: Dict[str, Any] = {"name": _CUSTOM_INSIGHT_NAME, "level": "ad", "fields": _FIELDS}
    if per_insight is not None:
        custom_insight["include_incrementality"] = per_insight
    config_builder = config().with_start_date(_FIRST_DAY).with_end_date(_SECOND_DAY)
    built_config = config_builder.build()
    built_config["custom_insights"] = [custom_insight]
    if top_level is not None:
        built_config["include_incrementality"] = top_level
    return config_builder


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


def _throttle_response() -> HttpResponse:
    headers = {
        "x-fb-ads-insights-throttle": json.dumps({"app_id_util_pct": 0, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}),
    }
    return build_response(body={}, status_code=HTTPStatus.OK, headers=headers)


def _job_status_request(report_run_ids: List[str]) -> RequestBuilder:
    body = {"batch": [{"method": "GET", "relative_url": f"{report_run_id}/"} for report_run_id in report_run_ids]}
    return RequestBuilder.get_execute_batch_endpoint(access_token=ACCESS_TOKEN).with_body(encode_request_body(body))


def _job_status_response(job_ids: List[str]) -> HttpResponse:
    body = [
        {"body": json.dumps({"id": job_id, "account_id": ACCOUNT_ID, "async_status": Status.COMPLETED, "async_percent_completion": 100})}
        for job_id in job_ids
    ]
    return build_response(body=body, status_code=HTTPStatus.OK)


def _insights_response(day: datetime, ad_id: str) -> HttpResponse:
    record = {
        "account_id": ACCOUNT_ID,
        "ad_id": ad_id,
        "spend": "1.5",
        "actions": [{"action_type": "link_click", "value": "3", "1d_click": "3", "incrementality": "2"}],
        "date_start": day.strftime(DATE_FORMAT),
        "date_stop": day.strftime(DATE_FORMAT),
    }
    return build_response(body={"data": [record]}, status_code=HTTPStatus.OK)


@freezegun.freeze_time(NOW.isoformat())
@pytest.mark.parametrize(
    "top_level,per_insight,expected_windows",
    [
        pytest.param(True, None, _WINDOWS_WITH_INCREMENTALITY, id="top_level_enabled_and_custom_insight_unset_inherits_incrementality"),
        pytest.param(False, True, _WINDOWS_WITH_INCREMENTALITY, id="custom_insight_enabled_alone_requests_incrementality"),
        pytest.param(None, None, _DEFAULT_WINDOWS, id="both_unset_requests_default_windows_only"),
    ],
)
def test_custom_insight_job_requests_incrementality_window_from_either_config_level(
    top_level: Optional[bool], per_insight: Optional[bool], expected_windows: List[str]
) -> None:
    """
    The report job a custom insight stream starts for every daily slice must carry the `incrementality`
    attribution window when `include_incrementality` is enabled on the custom insight or at the top level
    of the config, and only the default windows otherwise.

    HttpMocker matches the job creation body exactly, so a job started with any other
    `action_attribution_windows` finds no mocked response and the read emits no records.
    """
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            RequestBuilder.get_insights_endpoint(access_token=ACCESS_TOKEN, account_id=ACCOUNT_ID).build(),
            _throttle_response(),
        )
        for day, (report_run_id, _, _) in _JOBS_BY_DAY.items():
            http_mocker.post(
                _job_start_request(day, expected_windows).build(),
                build_response(body={"report_run_id": report_run_id}, status_code=HTTPStatus.OK),
            )
        http_mocker.post(
            _job_status_request([report_run_id for report_run_id, _, _ in _JOBS_BY_DAY.values()]).build(),
            _job_status_response([job_id for _, job_id, _ in _JOBS_BY_DAY.values()]),
        )
        for day, (_, job_id, ad_id) in _JOBS_BY_DAY.items():
            http_mocker.get(
                RequestBuilder.get_insights_download_endpoint(access_token=ACCESS_TOKEN, job_id=job_id).with_limit(100).build(),
                _insights_response(day, ad_id),
            )

        output = read_output(
            config_builder=_config(top_level=top_level, per_insight=per_insight),
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
        )

    assert [(record.record.data["ad_id"], record.record.data["date_start"]) for record in output.records] == [
        (ad_id, day.strftime(DATE_FORMAT)) for day, (_, _, ad_id) in _JOBS_BY_DAY.items()
    ]
    assert output.errors == []
