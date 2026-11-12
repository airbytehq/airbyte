#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ACCESS_TOKEN, ACCOUNT_ID, DATE_FORMAT, NOW, ConfigBuilder
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


_CUSTOM_INSIGHT_NAME = "incrementality_report"
_STREAM_NAME = f"custom{_CUSTOM_INSIGHT_NAME}"
_FIELDS = ["account_id", "ad_id", "actions", "spend"]
_DEFAULT_WINDOWS = ["1d_click", "7d_click", "28d_click", "1d_view"]


def _config(top_level: Optional[bool], custom_insight: Optional[bool], start_date: datetime, end_date: datetime) -> ConfigBuilder:
    insight: Dict[str, Any] = {"name": _CUSTOM_INSIGHT_NAME, "fields": _FIELDS, "level": "ad"}
    if custom_insight is not None:
        insight["include_incrementality"] = custom_insight

    builder = config().with_start_date(start_date).with_end_date(end_date)
    builder._config["custom_insights"] = [insight]
    if top_level is not None:
        builder._config["include_incrementality"] = top_level
    return builder


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


def _insights_response(ad_id: str, day: datetime):
    record = {
        "account_id": ACCOUNT_ID,
        "ad_id": ad_id,
        "actions": [{"action_type": "purchase", "value": "3", "1d_click": "2"}],
        "spend": "1.5",
        "date_start": day.strftime(DATE_FORMAT),
        "date_stop": day.strftime(DATE_FORMAT),
    }
    return build_response(body={"data": [record], "paging": {}}, status_code=HTTPStatus.OK)


@freezegun.freeze_time("2023-01-10T00:00:00Z")
@pytest.mark.parametrize(
    "top_level,custom_insight,expected_windows",
    [
        pytest.param(True, None, _DEFAULT_WINDOWS + ["incrementality"], id="top_level_on_propagates_to_custom_insight"),
        pytest.param(True, False, _DEFAULT_WINDOWS + ["incrementality"], id="top_level_on_wins_over_custom_insight_off"),
        pytest.param(False, True, _DEFAULT_WINDOWS + ["incrementality"], id="custom_insight_on_alone_still_enables"),
        pytest.param(None, None, _DEFAULT_WINDOWS, id="both_unset_keeps_default_windows"),
    ],
)
def test_custom_insight_job_requests_use_top_level_include_incrementality(
    top_level: Optional[bool], custom_insight: Optional[bool], expected_windows: List[str]
) -> None:
    """
    The async insights job for a custom insight stream must request the `incrementality` attribution window
    when either the top-level or the per-insight `include_incrementality` toggle is on. Unmatched requests fail
    the read, so the exact `action_attribution_windows` in the job-start body is the assertion.
    """
    first_day = NOW - timedelta(days=1)
    second_day = NOW
    report_run_ids = ["1571860060019500", "4571860060019599"]
    job_ids = ["1049937379601600", "1049937379601699"]

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        http_mocker.post(_job_start_request(first_day, expected_windows).build(), _job_start_response(report_run_ids[0]))
        http_mocker.post(_job_start_request(second_day, expected_windows).build(), _job_start_response(report_run_ids[1]))
        http_mocker.post(_job_status_request(report_run_ids).build(), _job_status_response(job_ids))
        http_mocker.get(_get_insights_request(job_ids[0]).build(), _insights_response("ad_1", first_day))
        http_mocker.get(_get_insights_request(job_ids[1]).build(), _insights_response("ad_2", second_day))

        output = read_output(
            config_builder=_config(top_level, custom_insight, first_day, second_day),
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
        )

    assert output.errors == []
    assert [(record.record.data["ad_id"], record.record.data["date_start"]) for record in output.records] == [
        ("ad_1", first_day.strftime(DATE_FORMAT)),
        ("ad_2", second_day.strftime(DATE_FORMAT)),
    ]
