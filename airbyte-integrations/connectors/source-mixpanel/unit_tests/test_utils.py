#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_mixpanel.utils import fix_date_time


@pytest.mark.parametrize(
    "input_record, expected_record",
    [
        # Test with a dictionary containing recognized date formats.
        (
            {"last_seen": "2022-09-27 12:34:56", "created": "2022-09-27T12:34:56"},
            {"last_seen": "2022-09-27T12:34:56", "created": "2022-09-27T12:34:56"},
        ),
        # Test with a dictionary containing unrecognized date formats.
        (
            {"last_seen": "09/27/2022 12:34:56", "created": "September 27, 2022"},
            {"last_seen": "09/27/2022 12:34:56", "created": "September 27, 2022"},
        ),
        # Test with nested dictionaries.
        (
            {"user": {"last_seen": "2022-09-27 12:34:56", "created": "2022-09-27T12:34:56"}},
            {"user": {"last_seen": "2022-09-27T12:34:56", "created": "2022-09-27T12:34:56"}},
        ),
        # Test with a list of dictionaries.
        (
            [{"last_seen": "2022-09-27 12:34:56"}, {"created": "2022-09-27T12:34:56"}],
            [{"last_seen": "2022-09-27T12:34:56"}, {"created": "2022-09-27T12:34:56"}],
        ),
        # Test with mixed data structures.
        (
            {"users": [{"last_seen": "2022-09-27 12:34:56"}, {"created": "2022-09-27T12:34:56"}]},
            {"users": [{"last_seen": "2022-09-27T12:34:56"}, {"created": "2022-09-27T12:34:56"}]},
        ),
        # Test with a dictionary containing ISO strings with offsets.
        (
            {"last_seen": "2022-09-27 12:34:56+05:00", "created": "2022-09-27T12:34:56-03:00"},
            {"last_seen": "2022-09-27 12:34:56+05:00", "created": "2022-09-27T12:34:56-03:00"},
        ),
    ],
)
def test_fix_date_time(input_record, expected_record):
    fix_date_time(input_record)
    assert input_record == expected_record
