#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta

import pytest
from freezegun import freeze_time
from source_facebook_marketing.streams.async_job_manager import InsightAsyncJobManager

from airbyte_cdk.models import AirbyteStateMessageSerializer, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse

from .config import ACCOUNT_ID
from .request_builder import get_account_request
from .response_builder import get_account_response
from .test_ads_insights_action_product_id import (
    _ads_insights_action_product_id_record,
    _get_insights_request,
    _insights_response,
    _job_start_request,
    _job_start_response,
    _job_status_request,
    _job_status_response,
    _update_api_throttle_limit_request,
    _update_api_throttle_limit_response,
)
from .utils import config, read_output


@freeze_time("2026-11-12")
@pytest.mark.parametrize("out_of_order", [False, True], ids=["in_order", "out_of_order"])
@pytest.mark.parametrize("empty_results", [False, True], ids=["records", "empty"])
def test_lookback_state_never_regresses(mocker, out_of_order, empty_results):
    cursor = ab_datetime_parse("2026-09-20")
    start = cursor - timedelta(days=28)
    end = cursor + timedelta(days=2)
    dates = [start + timedelta(days=i) for i in range(31)]
    report_ids = [str(1000 + i) for i in range(31)]
    job_ids = [str(2000 + i) for i in range(31)]
    stream_name = "ads_insights_action_product_id"
    state = AirbyteStateMessageSerializer.load(
        {
            "type": "STREAM",
            "stream": {
                "stream_descriptor": {"name": stream_name},
                "stream_state": {ACCOUNT_ID: {"date_start": "2026-09-20"}, "time_increment": 1},
            },
        }
    )
    check_status = InsightAsyncJobManager._check_jobs_status

    def ordered_completions(manager):
        completed = check_status(manager)
        if out_of_order:
            return completed[1::2] + completed[::2]
        return completed

    mocker.patch.object(InsightAsyncJobManager, "_check_jobs_status", ordered_completions)
    with HttpMocker() as http_mocker:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(_update_api_throttle_limit_request().build(), _update_api_throttle_limit_response())
        for day, report_id, job_id in zip(dates, report_ids, job_ids):
            http_mocker.post(_job_start_request(since=day, until=day).build(), _job_start_response(report_id))
            response = _insights_response()
            if not empty_results:
                response = response.with_record(_ads_insights_action_product_id_record())
            http_mocker.get(_get_insights_request(job_id).build(), response.build())
        http_mocker.post(_job_status_request(report_ids).build(), _job_status_response(job_ids))
        output = read_output(
            config().with_start_date(start).with_end_date(end),
            stream_name,
            SyncMode.incremental,
            state=[state],
        )

    states = [AirbyteStateMessageSerializer.dump(message.state)["stream"]["stream_state"][ACCOUNT_ID] for message in output.state_messages]
    assert len(states) >= len(dates)
    for emitted_state in states:
        assert emitted_state["date_start"] >= "2026-09-20"
        assert all(day > emitted_state["date_start"] for day in emitted_state["slices"])
    assert states[-1]["date_start"] == "2026-09-22"
    assert states[-1]["slices"] == []
    assert len(output.records) == (0 if empty_results else len(dates))
