# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta
from typing import List

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ACCESS_TOKEN, ACCOUNT_ID, DATE_FORMAT, NOW
from .request_builder import RequestBuilder, get_account_request
from .response_builder import get_account_response
from .test_ads_insights_action_product_id import (
    _ads_insights_action_product_id_record,
    _get_insights_request,
    _insights_response,
    _job_start_response,
    _job_status_request,
    _job_status_response,
    _update_api_throttle_limit_request,
    _update_api_throttle_limit_response,
)
from .utils import config, encode_request_body, read_output


_INSIGHT_NAME = "incrementality_report"
_STREAM_NAME = f"custom{_INSIGHT_NAME}"
_FIELDS = ["account_id", "ad_id", "spend", "actions"]
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


@pytest.mark.parametrize(
    "source_level,insight_level,expected_windows",
    [
        pytest.param(True, False, [*_DEFAULT_WINDOWS, "incrementality"], id="source_level_toggle_applies_to_custom_insight"),
        pytest.param(False, True, [*_DEFAULT_WINDOWS, "incrementality"], id="custom_insight_toggle_alone"),
        pytest.param(False, False, _DEFAULT_WINDOWS, id="both_off_requests_default_windows"),
    ],
)
@freezegun.freeze_time("2023-01-10T00:00:00Z")
def test_custom_insight_job_requests_incrementality_window(source_level: bool, insight_level: bool, expected_windows: List[str]) -> None:
    days = [NOW - timedelta(days=1), NOW]
    report_run_ids = ["1571860060019500", "4571860060019599"]
    job_ids = ["1049937379601600", "1049937379601699"]

    config_builder = config().with_start_date(days[0]).with_end_date(days[1])
    config_builder._config["include_incrementality"] = source_level
    config_builder._config["custom_insights"] = [{"name": _INSIGHT_NAME, "fields": _FIELDS, "include_incrementality": insight_level}]

    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        # The job start mocks only match a request carrying exactly `expected_windows`, one per daily slice.
        for day, report_run_id in zip(days, report_run_ids):
            http_mocker.post(_job_start_request(day, expected_windows).build(), _job_start_response(report_run_id))
        http_mocker.post(_job_status_request(report_run_ids).build(), _job_status_response(job_ids))
        for job_id in job_ids:
            http_mocker.get(
                _get_insights_request(job_id).build(),
                _insights_response().with_record(_ads_insights_action_product_id_record()).build(),
            )

        output = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh)

    assert output.errors == []
    assert len(output.records) == 2
