#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pytest
from source_shopify.source import OrderRefunds, Orders
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

# Define the Stream instances for the tests
SHOPIFY_STREAM = Orders(config={"authenticator": None})
SHOPIFY_SUB_STREAM = OrderRefunds(config={"authenticator": None})


@pytest.mark.parametrize(
    "stream, cur_stream_state, state_object, expected_output",
    [
        # When Full-Refresh: state_object: empty.
        (
            SHOPIFY_STREAM,
            {SHOPIFY_STREAM.cursor_field: ""},
            {},
            {SHOPIFY_STREAM.name: {SHOPIFY_STREAM.cursor_field: ""}},
        ),
        (
            SHOPIFY_SUB_STREAM,
            {SHOPIFY_SUB_STREAM.cursor_field: ""},
            {},
            {SHOPIFY_SUB_STREAM.name: {SHOPIFY_SUB_STREAM.cursor_field: ""}},
        ),
    ],
    ids=["Sync Started. Parent.", "Sync Started. Child."],
)
def test_full_refresh(stream, cur_stream_state, state_object, expected_output):
    """
    When Sync = Full-Refresh: we don't have any state yet, so we need to keep the state_object at min value, thus empty.
    """
    # create the fixure for *args based on input
    args = [stream]
    # use the external tmp_state_object for this test
    actual = stream_state_cache.stream_state_to_tmp(*args, state_object=state_object, stream_state=cur_stream_state)
    assert actual == expected_output


@pytest.mark.parametrize(
    "stream, cur_stream_state, state_object, expected_output",
    [
        # When start the incremental refresh, assuming we have the state of STREAM.
        (
            SHOPIFY_STREAM,
            {SHOPIFY_STREAM.cursor_field: "2021-01-01T01-01-01"},
            {},
            {SHOPIFY_STREAM.name: {SHOPIFY_STREAM.cursor_field: "2021-01-01T01-01-01"}},
        ),
        (
            SHOPIFY_SUB_STREAM,
            {SHOPIFY_SUB_STREAM.cursor_field: "2021-01-01T01-01-01"},
            {},
            {SHOPIFY_SUB_STREAM.name: {SHOPIFY_SUB_STREAM.cursor_field: "2021-01-01T01-01-01"}},
        ),
        # While doing the incremental refresh, we keeping the original state, even if the state is updated during the sync.
        (
            SHOPIFY_STREAM,
            {SHOPIFY_STREAM.cursor_field: "2021-01-05T02-02-02"},
            {},
            {SHOPIFY_STREAM.name: {SHOPIFY_STREAM.cursor_field: "2021-01-05T02-02-02"}},
        ),
        (
            SHOPIFY_SUB_STREAM,
            {SHOPIFY_SUB_STREAM.cursor_field: "2021-01-05T02-02-02"},
            {},
            {SHOPIFY_SUB_STREAM.name: {SHOPIFY_SUB_STREAM.cursor_field: "2021-01-05T02-02-02"}},
        ),
    ],
    ids=["Sync Started. Parent", "Sync Started. Child", "Sync in progress. Parent", "Sync in progress. Child"],
)
def test_incremental_sync(stream, cur_stream_state, state_object, expected_output):
    """
    When Sync = Incremental Refresh: we already have the saved state from Full-Refresh sync,
    we have it passed as input to the Incremental Sync, so we need to back it up and reuse.
    """
    # create the fixure for *args based on input
    args = [stream]
    actual = stream_state_cache.stream_state_to_tmp(*args, state_object=state_object, stream_state=cur_stream_state)
    assert actual == expected_output
