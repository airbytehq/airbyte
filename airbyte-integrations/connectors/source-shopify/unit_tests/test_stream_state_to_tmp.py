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

import pytest
from source_shopify.source import IncrementalShopifyStream

test_state_object = {}


@pytest.mark.parametrize(
    "stream_name, current_stream_state, latest_record, cursor_field, state_object, output",
    [
        # When Full-Refresh: state_object: empty
        (
            "test_stream",
            {"test_cursor": ""},
            {"test_cursor": "2021-01-01T01-01-01"},
            "test_cursor",
            {},
            {"test_stream": {"test_cursor": ""}},
        ),
        # When start the 1st incremental refresh, assuming we have the state of stream
        (
            "test_stream",
            {"test_cursor": "2021-01-01T01-01-01"},
            {"test_cursor": "2021-01-02T02-02-02"},
            "test_cursor",
            {},
            {"test_stream": {"test_cursor": "2021-01-01T01-01-01"}},
        ),
        # While doing the 1st sequence of incremental refresh, we keeping the original state
        (
            "test_stream",
            {"test_cursor": "2021-01-02T02-02-02"},
            {"test_cursor": "2021-01-10T10-10-10"},
            "test_cursor",
            {"test_stream": {"test_cursor": "2021-01-01T01-01-01"}},
            {"test_stream": {"test_cursor": "2021-01-01T01-01-01"}},
        ),
        # The 1st Incremental is finished with some state, it's state is passed as `current_stream_state` to the new sync
        # when start 2nd and all sequential incremental refreshes
        (
            "test_stream",
            {"test_cursor": "2021-01-10T10-10-10"},
            {"test_cursor": "2021-01-11T00-00-00"},
            "test_cursor",
            {},
            {"test_stream": {"test_cursor": "2021-01-10T10-10-10"}},
        ),
    ],
    ids=["When Full-Refresh", "1st Incr. Sync", "While 1st Incr. Sync is going", "2sn Incr. Sync"],
)
def test_test(stream_name, current_stream_state, latest_record, cursor_field, state_object, output):
    actual = IncrementalShopifyStream.stream_state_to_tmp(stream_name, current_stream_state, latest_record, state_object, cursor_field)
    assert actual == output
