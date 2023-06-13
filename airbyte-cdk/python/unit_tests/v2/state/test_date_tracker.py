from typing import Tuple, List

import pytest
from datetime import datetime, timedelta

from airbyte_cdk.v2.state import DatetimeRangeTracker


@pytest.mark.parametrize("input_ranges,expected_output_range", [
    pytest.param(
        [(datetime(2023, 10, 1), datetime(2023, 10, 30))],
        [(datetime(2023, 10, 1), datetime(2023, 10, 30))],  # expected
        id="Simple addition"
    ),
    pytest.param(
        [
            (datetime(2023, 9, 5), datetime(2023, 9, 25)),
            (datetime(2023, 10, 1), datetime(2023, 10, 30)),
        ],
        [
            (datetime(2023, 9, 5), datetime(2023, 9, 25)),
            (datetime(2023, 10, 1), datetime(2023, 10, 30)),
        ],  # expected
        id="Multiple non-overlapping ranges"
    ),
    pytest.param(
        [
            (datetime(2023, 9, 1), datetime(2023, 9, 20)),
            (datetime(2023, 9, 10), datetime(2023, 9, 25)),
        ],
        [
            (datetime(2023, 9, 1), datetime(2023, 9, 25)),
        ],  # expected
        id="Test that one overlapping range is merged correctly."
    ),
    pytest.param(
        [
            (datetime(2023, 9, 1), datetime(2023, 9, 20)),
            (datetime(2023, 9, 10), datetime(2023, 9, 15)),
        ],
        [
            (datetime(2023, 9, 1), datetime(2023, 9, 20)),
        ],  # expected
        id="Test merging of one range contained in another."
    ),
    pytest.param(
        [
            (datetime(2023, 9, 1), datetime(2023, 9, 10)),
            (datetime(2023, 9, 10), datetime(2023, 9, 20))
        ],
        [
            (datetime(2023, 9, 1), datetime(2023, 9, 20))
        ],
        id="Test merging of two ranges which overlap exactly on the boundary"
    ),
    pytest.param(
        [
            (datetime(2023, 9, 1), datetime(2023, 9, 10)),
            (datetime(2023, 9, 10), datetime(2023, 9, 20)),
            (datetime(2023, 9, 16), datetime(2023, 9, 23)),
            (datetime(2023, 10, 1), datetime(2023, 10, 23)),
            (datetime(2023, 10, 20), datetime(2023, 10, 27)),
        ],
        [
            (datetime(2023, 9, 1), datetime(2023, 9, 23)),
            (datetime(2023, 10, 1), datetime(2023, 10, 27)),
        ],
        id="Test merging of three overlapping ranges which overlap exactly on the boundary"
    )
])
def test_mark_range_as_copied(input_ranges: List[Tuple[datetime, datetime]], expected_output_range: List[Tuple[datetime, datetime]]):
    tracker = DatetimeRangeTracker()
    for input_range in input_ranges:
        tracker.mark_range_as_copied(*input_range)
    assert tracker.get_copied_ranges() == expected_output_range


@pytest.mark.parametrize("copied_ranges,total_start,total_end,expected,preferred_range_size", [
    pytest.param(
        [(datetime(2023, 9, 1), datetime(2023, 9, 10))],  # copied ranges
        datetime(2023, 9, 1), datetime(2023, 9, 30),  # start,end
        [(datetime(2023, 9, 10), datetime(2023, 9, 30))],
        None,
        id="Test a simple range"
    ),
    pytest.param(
        [(datetime(2023, 9, 1), datetime(2023, 9, 10))],  # copied ranges
        datetime(2023, 9, 1), datetime(2023, 9, 30),  # start,end
        [ # Expected
            (datetime(2023, 9, 10), datetime(2023, 9, 20)),
            (datetime(2023, 9, 20), datetime(2023, 9, 30))
        ],
        timedelta(days=10),
        id="Test a simple range with preferred range size"
    ),
    # TODO add like, way more test cases
])
def test_get_uncopied_ranges(copied_ranges, total_start, total_end, expected, preferred_range_size):
    tracker = DatetimeRangeTracker()
    for r in copied_ranges:
        tracker.mark_range_as_copied(*r)
    uncopied = tracker.get_uncopied_ranges(total_start, total_end, preferred_range_size, False)
    assert uncopied == expected
