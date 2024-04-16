#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta

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
    assert reduced_slice.end_date == datetime(2022, 1, 31)
