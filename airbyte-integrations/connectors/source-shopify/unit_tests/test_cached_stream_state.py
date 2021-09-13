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
from source_shopify.source import Orders
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

# Define the Stream class for the test
STREAM = Orders(config={"authenticator": "token"})


@pytest.mark.parametrize(
    "stream, cur_stream_state, latest_record, state_object, expected_output",
    [
        # When Full-Refresh: state_object: empty.
        (STREAM, {STREAM.cursor_field: ""}, {STREAM.cursor_field: ""}, {}, {STREAM.name: {STREAM.cursor_field: ""}}),
        (STREAM, {STREAM.cursor_field: ""}, {STREAM.cursor_field: "2021-01-01T01-01-01"}, {}, {STREAM.name: {STREAM.cursor_field: ""}}),
    ],
    ids=["Sync Started", "Sync in progress"],
)
def test_full_refresh(stream, cur_stream_state, latest_record, state_object, expected_output):
    """
    When Sync = Full-Refresh: we don't have any state yet, so we need to keep the state_object at min value, thus empty.
    """
    # create the fixure for *args based on input
    args = [stream, cur_stream_state, latest_record]
    # use the external tmp_state_object for this test
    actual = stream_state_cache.stream_state_to_tmp(*args, state_object=state_object)
    assert actual == expected_output


@pytest.mark.parametrize(
    "stream, cur_stream_state, latest_record, state_object, expected_output",
    [
        # When start the incremental refresh, assuming we have the state of STREAM.
        (
            STREAM,
            {STREAM.cursor_field: "2021-01-01T01-01-01"},
            {STREAM.cursor_field: "2021-01-05T02-02-02"},
            {},
            {STREAM.name: {STREAM.cursor_field: "2021-01-01T01-01-01"}},
        ),
        # While doing the incremental refresh, we keeping the original state, even if the state is updated during the sync.
        (
            STREAM,
            {STREAM.cursor_field: "2021-01-05T02-02-02"},
            {STREAM.cursor_field: "2021-01-10T10-10-10"},
            {},
            {STREAM.name: {STREAM.cursor_field: "2021-01-05T02-02-02"}},
        ),
    ],
    ids=["Sync Started", "Sync in progress"],
)
def test_incremental_sync(stream, cur_stream_state, latest_record, state_object, expected_output):
    """
    When Sync = Incremental Refresh: we already have the saved state from Full-Refresh sync,
    we have it passed as input to the Incremental Sync, so we need to back it up and reuse.
    """
    # create the fixure for *args based on input
    args = [stream, cur_stream_state, latest_record]
    actual = stream_state_cache.stream_state_to_tmp(*args, state_object=state_object)
    assert actual == expected_output
