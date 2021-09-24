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

from source_linkedin_ads.analytics import chunk_analytics_fields

# Test chunk size for each field set
TEST_FIELDS_CHUNK_SIZE = 3
# Test fields assuming they are really available for the fetch
TEST_ANALYTICS_FIELDS = [
    "field_1",
    "base_field_1",
    "field_2",
    "base_field_2",
    "field_3",
    "field_4",
    "field_5",
    "field_6",
    "field_7",
    "field_8",
]
# Fields that are always present in fields_set chunks
TEST_BASE_ANALLYTICS_FIELDS = ["base_field_1", "base_field_2"]


def test_chunk_analytics_fields():
    """
    We expect to truncate the fields list into the chunks of equal size,
    with TEST_BASE_ANALLYTICS_FIELDS presence in each chunk,
    order is not matter.
    """
    expected_output = [
        ["field_1", "base_field_1", "field_2", "base_field_2"],
        ["base_field_2", "field_3", "field_4", "base_field_1"],
        ["field_5", "field_6", "field_7", "base_field_1", "base_field_2"],
        ["field_8", "base_field_1", "base_field_2"],
    ]

    assert list(chunk_analytics_fields(TEST_ANALYTICS_FIELDS, TEST_BASE_ANALLYTICS_FIELDS, TEST_FIELDS_CHUNK_SIZE)) == expected_output
