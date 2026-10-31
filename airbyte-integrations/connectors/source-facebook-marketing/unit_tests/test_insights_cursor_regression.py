# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import date, datetime, timedelta

import pytest
from freezegun import freeze_time
from source_facebook_marketing.streams import AdsInsights
from source_facebook_marketing.utils import DateInterval

from airbyte_cdk.models import SyncMode


def make_stream(mocker, **kwargs):
    return AdsInsights(
        api=mocker.Mock(),
        account_ids=["a", "b"],
        start_date=datetime(2026, 1, 15),
        end_date=datetime(2026, 10, 10),
        insights_lookback_window=30,
        **kwargs,
    )


def consume_empty_slice(stream, mocker, start, end=None):
    job = mocker.Mock(interval=DateInterval(start=start, end=end or start))
    job.get_result.return_value = []
    assert list(stream.read_records(SyncMode.incremental, stream_slice={"account_id": "a", "insight_job": job})) == []


@freeze_time("2026-10-10")
def test_interrupted_attempt_does_not_rewind_checkpoint(mocker):
    stream = make_stream(mocker)
    stream.state = {"a": {"date_start": "2026-09-20", "slices": []}, "b": {"date_start": "2026-09-20"}, "time_increment": 1}
    initial_start = stream._next_cursor_values["a"]
    for offset in range(8):
        consume_empty_slice(stream, mocker, initial_start + timedelta(days=offset))

    failed_job = mocker.Mock(interval=DateInterval(start=date(2026, 8, 29), end=date(2026, 8, 29)))
    failed_job.get_result.side_effect = RuntimeError("interrupted AdReportRun")
    with pytest.raises(RuntimeError, match="interrupted AdReportRun"):
        list(stream.read_records(SyncMode.incremental, stream_slice={"account_id": "a", "insight_job": failed_job}))

    checkpoint = stream.state
    resumed = make_stream(mocker)
    resumed.state = checkpoint
    assert checkpoint["b"]["date_start"] == "2026-09-20"
    assert checkpoint["a"]["date_start"] == "2026-09-20"
    assert (
        resumed._next_cursor_values["a"] == initial_start
    ), f"checkpoint={checkpoint['a']['date_start']}, first start={initial_start}, resumed start={resumed._next_cursor_values['a']}"


@freeze_time("2026-10-10")
def test_completed_replay_slices_are_not_saved_before_cursor(mocker):
    stream = make_stream(mocker)
    stream.state = {
        "a": {"date_start": "2026-09-24", "slices": ["2026-09-05", "2026-09-24", "2026-09-26"]},
        "time_increment": 1,
    }
    consume_empty_slice(stream, mocker, date(2026, 9, 5))
    assert stream.state["a"]["slices"] == ["2026-09-26"]
    assert stream._completed_slices["a"] == {date(2026, 9, 5), date(2026, 9, 24), date(2026, 9, 26)}


@freeze_time("2026-10-10")
@pytest.mark.parametrize("options", [{"time_increment": 30}, {"time_increment_period": "monthly"}, {"time_increment_period": "weekly"}])
def test_multiday_cursor_advances_after_all_slices(mocker, options):
    stream = make_stream(mocker, **options)
    starts = list(stream._date_intervals("a"))
    for start in starts:
        consume_empty_slice(stream, mocker, start, stream._compute_interval_end(start))
    assert stream.state["a"].get("date_start") == starts[-1].isoformat()


@freeze_time("2026-10-10")
@pytest.mark.parametrize("with_state", [False, True])
def test_forward_sync_completing_out_of_order(mocker, with_state):
    stream = make_stream(mocker)
    if with_state:
        stream.state = {"a": {"date_start": "2026-09-20"}, "time_increment": 1}
    starts = list(stream._date_intervals("a"))
    for start in reversed(starts):
        consume_empty_slice(stream, mocker, start)
    assert stream.state["a"]["date_start"] == starts[-1].isoformat()
    assert stream.state["a"]["slices"] == []


@freeze_time("2026-10-10")
def test_alignment_check_uses_cached_account_end_date(mocker):
    stream = make_stream(mocker)
    stream._end_date = date(2026, 10, 10)
    starts = list(stream._date_intervals("a"))
    for start in starts[:2]:
        consume_empty_slice(stream, mocker, start)
    stream._api.get_account.assert_called_once_with(account_id="a")
