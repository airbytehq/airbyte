# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from http import HTTPStatus

import freezegun
import pytest

from airbyte_cdk.models import AirbyteStateMessageSerializer, AirbyteStreamStateSerializer, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ACCOUNT_ID, DATE_FORMAT, NOW
from .request_builder import get_account_request
from .response_builder import build_response, get_account_response
from .test_ads_insights_action_product_id import (
    _get_insights_request,
    _job_start_request,
    _job_start_response,
    _job_status_request,
    _job_status_response,
    _update_api_throttle_limit_request,
    _update_api_throttle_limit_response,
)
from .utils import config, read_output


@freezegun.freeze_time(NOW.isoformat())
@pytest.mark.parametrize("empty_results", [False, True])
def test_lookback_never_emits_cursor_older_than_input(empty_results: bool) -> None:
    @HttpMocker()
    def read_and_assert(http_mocker: HttpMocker) -> None:
        _assert_lookback_cursor(empty_results, http_mocker)

    read_and_assert()


def _assert_lookback_cursor(empty_results: bool, http_mocker: HttpMocker) -> None:
    cursor = NOW - timedelta(days=3)
    start = cursor - timedelta(days=28)
    end = NOW - timedelta(days=1)
    cursor_string = cursor.strftime(DATE_FORMAT)
    state = AirbyteStateMessageSerializer.load(
        {
            "type": "STREAM",
            "stream": {
                "stream_descriptor": {"name": "ads_insights"},
                "stream_state": {ACCOUNT_ID: {"date_start": cursor_string, "slices": []}, "time_increment": 1},
            },
        }
    )
    http_mocker.get(get_account_request().build(), get_account_response())
    http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
    job_ids = []
    for index in range((end - start).days + 1):
        day = start + timedelta(days=index)
        job_id = str(100000 + index)
        job_ids.append(job_id)
        http_mocker.post(
            _job_start_request(
                since=day,
                until=day,
                fields=["date_start"],
                breakdowns=[],
                action_breakdowns=["action_type", "action_target_id", "action_destination"],
            ).build(),
            _job_start_response(job_id),
        )
        http_mocker.get(
            _get_insights_request(job_id).build(),
            build_response(body={"data": [] if empty_results else [{"date_start": day.strftime(DATE_FORMAT)}]}, status_code=HTTPStatus.OK),
        )
    http_mocker.post(_job_status_request(job_ids).build(), _job_status_response(job_ids))

    output = read_output(
        config_builder=config().with_start_date(start).with_end_date(end),
        stream_name="ads_insights",
        sync_mode=SyncMode.incremental,
        state=[state],
        json_schema={"type": "object", "properties": {"date_start": {"type": "string"}}},
    )

    assert len(output.records) == (0 if empty_results else len(job_ids))
    cursors = [
        AirbyteStreamStateSerializer.dump(message.state.stream)["stream_state"][ACCOUNT_ID]["date_start"]
        for message in output.state_messages
    ]
    assert len(cursors) >= len(job_ids)
    assert all(value >= cursor_string for value in cursors), cursors
    assert cursors[-1] == end.strftime(DATE_FORMAT)
