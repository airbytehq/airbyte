#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta
from http import HTTPStatus

import freezegun
import pytest

from airbyte_cdk.models import AirbyteStateMessageSerializer, AirbyteStreamStateSerializer, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ACCOUNT_ID
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


@freezegun.freeze_time("2023-02-01T00:00:00Z")
@pytest.mark.parametrize("interrupted", [True, False], ids=["interrupted", "successful"])
@pytest.mark.parametrize("empty_results", [False, True], ids=["records", "empty"])
def test_insights_cursor_never_regresses(interrupted, empty_results):
    cursor = "2023-01-29"
    start = datetime(2023, 1, 1)
    end = datetime(2023, 1, 30)
    fields = ["account_id", "date_start", "date_stop"]
    schema = {"type": "object", "properties": {field: {"type": "string"} for field in fields}}
    state = [
        AirbyteStateMessageSerializer.load(
            {
                "type": "STREAM",
                "stream": {
                    "stream_descriptor": {"name": "ads_insights"},
                    "stream_state": {ACCOUNT_ID: {"date_start": cursor}, "time_increment": 1},
                },
            }
        )
    ]
    job_ids = [str(1000 + day) for day in range(30)]
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        for day, job_id in enumerate(job_ids):
            slice_start = start + timedelta(days=day)
            http_mocker.post(
                _job_start_request(
                    since=slice_start,
                    until=slice_start,
                    fields=fields,
                    breakdowns=[],
                    action_breakdowns=["action_type", "action_target_id", "action_destination"],
                ).build(),
                _job_start_response(job_id),
            )
            if interrupted and day > 1:
                continue
            if interrupted and day == 1:
                response = build_response(
                    {"error": {"code": 100, "message": "Invalid parameter", "type": "OAuthException"}},
                    HTTPStatus.BAD_REQUEST,
                )
            else:
                records = (
                    []
                    if empty_results
                    else [
                        {
                            "account_id": ACCOUNT_ID,
                            "date_start": slice_start.strftime("%Y-%m-%d"),
                            "date_stop": slice_start.strftime("%Y-%m-%d"),
                        }
                    ]
                )
                response = build_response({"data": records}, HTTPStatus.OK)
            http_mocker.get(_get_insights_request(job_id).build(), response)
        http_mocker.post(_job_status_request(job_ids).build(), _job_status_response(job_ids))

        output = read_output(
            config().with_start_date(start).with_end_date(end),
            "ads_insights",
            SyncMode.incremental,
            state=state,
            expecting_exception=interrupted,
            json_schema=schema,
        )

    assert len(output.records) == (0 if empty_results else 1 if interrupted else 30)
    emitted_states = [message.state.stream for message in output.state_messages]
    assert emitted_states
    last_state = AirbyteStreamStateSerializer.dump(emitted_states[-1])["stream_state"]
    assert last_state[ACCOUNT_ID]["date_start"] >= cursor
    assert last_state[ACCOUNT_ID]["date_start"] == (cursor if interrupted else end.strftime("%Y-%m-%d"))
    assert last_state[ACCOUNT_ID]["slices"] == []
