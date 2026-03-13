#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

import freezegun
import pendulum
import pytest
from source_iterable.slice_generators import AdjustableSliceGenerator, RangeSliceGenerator


TEST_DATE = pendulum.parse("2020-01-01")


def test_slice_gen():
    start_date = TEST_DATE
    generator = AdjustableSliceGenerator(start_date)
    dates = []
    for i in generator:
        dates.append(i)
        generator.adjust_range(pendulum.Period(start=start_date, end=start_date))
    assert dates
    days = [(slice.end_date - slice.start_date).total_days() for slice in dates]
    assert days[1] == AdjustableSliceGenerator.DEFAULT_RANGE_DAYS


@freezegun.freeze_time(TEST_DATE + pendulum.Duration(days=1000))
def test_slice_gen_no_range_adjust():
    start_date = TEST_DATE
    generator = AdjustableSliceGenerator(start_date)
    dates = []
    for i in generator:
        dates.append(i)
    assert dates
    days = [(slice.end_date - slice.start_date).total_days() for slice in dates]
    assert days
    assert days[1] == AdjustableSliceGenerator.MAX_RANGE_DAYS


@pytest.mark.parametrize(
    "start_day,end_day,days,range",
    [
        (
            "2020-01-01",
            "2020-01-10",
            5,
            [
                (pendulum.parse("2020-01-01"), pendulum.parse("2020-01-06")),
                (pendulum.parse("2020-01-06"), pendulum.parse("2020-01-10")),
            ],
        ),
        (
            "2020-01-01",
            "2020-01-10 20:00:12",
            5,
            [
                (pendulum.parse("2020-01-01"), pendulum.parse("2020-01-06")),
                (pendulum.parse("2020-01-06"), pendulum.parse("2020-01-10 20:00:12")),
            ],
        ),
        (
            "2020-01-01",
            "2020-01-01 20:00:12",
            5,
            [
                (pendulum.parse("2020-01-01"), pendulum.parse("2020-01-01 20:00:12")),
            ],
        ),
        (
            "2020-01-01",
            "2020-01-10",
            50,
            [(pendulum.parse("2020-01-01"), pendulum.parse("2020-01-10"))],
        ),
        (
            "2020-01-01",
            "2020-01-01",
            50,
            [],
        ),
    ],
)
def test_datetime_ranges(start_day, end_day, days, range):
    start_day = pendulum.parse(start_day)
    with freezegun.freeze_time(end_day):
        end_day = pendulum.parse(end_day)
        RangeSliceGenerator.RANGE_LENGTH_DAYS = days
        generator = RangeSliceGenerator(start_day)
        assert [(slice.start_date, slice.end_date) for slice in generator] == range


def test_datetime_wrong_range():
    start_day = pendulum.parse("2020")
    end_day = pendulum.parse("2000")
    with pytest.raises(StopIteration):
        next(RangeSliceGenerator.make_datetime_ranges(start_day, end_day, 1))


def test_reduce_range():
    slice_generator = AdjustableSliceGenerator(start_date=datetime(2022, 1, 1), end_date=datetime(2022, 1, 31))
    next(slice_generator)
    reduced_slice = slice_generator.reduce_range()
    assert reduced_slice.start_date == datetime(2022, 1, 1)
    # 30-day window halved by RANGE_REDUCE_FACTOR (2) = 15 days
    assert reduced_slice.end_date == datetime(2022, 1, 16)


def test_reduce_range_actually_shrinks_slice_within_small_window():
    """With a 6-hour window, reduce_range should produce a smaller slice."""
    start = pendulum.parse("2026-03-09 18:00:00")
    end = pendulum.parse("2026-03-10 00:00:00")  # 6 hours

    gen = AdjustableSliceGenerator(start_date=start, end_date=end)
    first_slice = next(gen)

    assert first_slice.start_date == start
    assert first_slice.end_date == end
    first_duration = (first_slice.end_date - first_slice.start_date).total_seconds()

    reduced_slice = gen.reduce_range()
    reduced_duration = (reduced_slice.end_date - reduced_slice.start_date).total_seconds()

    assert reduced_duration < first_duration, (
        f"reduce_range() did not shrink the slice! "
        f"Original: {first_duration}s, Reduced: {reduced_duration}s"
    )


def test_repeated_reduce_range_produces_progressively_smaller_slices():
    """6 calls to reduce_range should produce 6 progressively smaller slices."""
    start = pendulum.parse("2026-03-09 18:00:00")
    end = pendulum.parse("2026-03-10 00:00:00")  # 6 hours

    gen = AdjustableSliceGenerator(start_date=start, end_date=end)
    next(gen)

    durations = []
    for _ in range(6):
        reduced = gen.reduce_range()
        duration = (reduced.end_date - reduced.start_date).total_seconds()
        durations.append(duration)

    for i in range(1, len(durations)):
        assert durations[i] < durations[i - 1], (
            f"Retry {i+1} did not shrink vs retry {i}: "
            f"{durations[i]}s >= {durations[i-1]}s"
        )


def test_reduce_range_with_5_minute_window():
    """Even a 5-minute sync window should be reducible."""
    start = pendulum.parse("2026-03-09 22:30:00")
    end = pendulum.parse("2026-03-09 22:35:00")

    gen = AdjustableSliceGenerator(start_date=start, end_date=end)
    first_slice = next(gen)
    assert first_slice.end_date == end

    reduced = gen.reduce_range()
    reduced_duration = (reduced.end_date - reduced.start_date).total_seconds()
    assert reduced_duration < 5 * 60, (
        f"reduce_range() could not shrink a 5-minute window! "
        f"Reduced duration: {reduced_duration}s"
    )


def test_reduce_range_slices_stay_within_bounds():
    """Reduced slices should stay within the original window."""
    start = pendulum.parse("2026-03-09 20:00:00")
    end = pendulum.parse("2026-03-09 22:00:00")  # 2 hours

    gen = AdjustableSliceGenerator(start_date=start, end_date=end)
    next(gen)

    for _ in range(6):
        reduced = gen.reduce_range()
        assert reduced.start_date == start
        assert reduced.end_date <= end
        assert reduced.end_date > reduced.start_date


def test_reduce_range_after_adjust_does_not_expand():
    """When adjust_range set _current_range small, reduce_range should not expand it."""
    start = pendulum.parse("2026-03-09 00:00:00")
    end = pendulum.parse("2026-03-09 12:00:00")  # 12 hours

    gen = AdjustableSliceGenerator(start_date=start, end_date=end)
    next(gen)

    gen.adjust_range(pendulum.Duration(minutes=30))

    reduced = gen.reduce_range()
    reduced_duration_days = (reduced.end_date - reduced.start_date).total_seconds() / 86400

    assert reduced_duration_days <= 0.5, (
        f"reduce_range() produced a {reduced_duration_days}-day slice "
        f"after adjust_range set _current_range to {gen._current_range}"
    )
