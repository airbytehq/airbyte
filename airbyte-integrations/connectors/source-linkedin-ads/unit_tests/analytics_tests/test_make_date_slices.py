#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_linkedin_ads.analytics import make_date_slices

TEST_START_DATE = "2021-08-01"
TEST_END_DATE = "2021-10-01"


def test_make_date_slices():
    """
    : By default we use the `WINDOW_SIZE = 30`, as it set in the analytics module
    : This value could be changed by setting the corresponding argument in the method.
    : The `end_date` is not specified by default, but for this test it was specified to have the test static.
    """

    expected_output = [
        {"dateRange": {"start.day": 1, "start.month": 8, "start.year": 2021, "end.day": 31, "end.month": 8, "end.year": 2021}},
        {"dateRange": {"start.day": 31, "start.month": 8, "start.year": 2021, "end.day": 30, "end.month": 9, "end.year": 2021}},
        {"dateRange": {"start.day": 30, "start.month": 9, "start.year": 2021, "end.day": 30, "end.month": 10, "end.year": 2021}},
    ]

    assert list(make_date_slices(TEST_START_DATE, TEST_END_DATE)) == expected_output
