#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
