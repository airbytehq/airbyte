# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import date, datetime

import pytest
from freezegun import freeze_time
from source_facebook_marketing.streams import AdsInsights
from source_facebook_marketing.streams.async_job import InsightAsyncJob

from airbyte_cdk.models import SyncMode


@freeze_time("2026-04-01")
@pytest.mark.parametrize("time_increment", [1, 7])
@pytest.mark.parametrize("lookback,expected_start", [(28, "2026-02-01"), (0, "2026-03-01")])
def test_checkpoint_does_not_backtrack(mocker, some_config, time_increment, lookback, expected_start):
    account_id = some_config["account_ids"][0]
    api = mocker.Mock()
    mocker.patch.object(InsightAsyncJob, "get_result", return_value=[])
    starts = []

    def manager(**kwargs):
        def completed_jobs():
            jobs = iter(kwargs["jobs"])
            first = next(jobs)
            starts.append(first.interval.start.isoformat())
            yield first
            raise RuntimeError("interrupted while waiting for remaining AdReportRun jobs")

        return mocker.Mock(completed_jobs=completed_jobs)

    mocker.patch("source_facebook_marketing.streams.base_insight_streams.InsightAsyncJobManager", side_effect=manager)
    state = {account_id: {"date_start": "2026-03-01", "slices": []}, "time_increment": time_increment}
    checkpoints = []
    for _ in range(2):
        stream = AdsInsights(
            api=api,
            account_ids=[account_id],
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2026, 3, 31),
            insights_lookback_window=lookback,
            time_increment=time_increment,
        )

        def read():
            for stream_slice in stream.stream_slices(SyncMode.incremental, stream_state=state):
                list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))
                checkpoints.append(stream.state[account_id]["date_start"])

        with pytest.raises(RuntimeError, match="interrupted"):
            read()
        state = stream.state

    assert checkpoints == ["2026-03-01", "2026-03-01"]
    assert starts == [expected_start, expected_start]


@freeze_time("2026-04-01")
@pytest.mark.parametrize("cursor_values", [None, {}, {"other_account": date(2026, 3, 1)}, {"unknown_account": None}])
def test_advance_cursor_initializes_missing_account_cursor(mocker, some_config, cursor_values):
    account_id = some_config["account_ids"][0]
    stream = AdsInsights(
        api=mocker.Mock(),
        account_ids=[account_id],
        start_date=datetime(2026, 3, 1),
        end_date=datetime(2026, 3, 2),
        insights_lookback_window=28,
    )
    stream._cursor_values = cursor_values
    stream._completed_slices[account_id].add(date(2026, 3, 1))

    stream._advance_cursor(account_id)

    assert stream.state[account_id] == {"date_start": "2026-03-01", "slices": []}
    assert stream._next_cursor_values[account_id] == date(2026, 3, 2)
