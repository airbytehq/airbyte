#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pytest
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_intercom.source import ConversationParts, Conversations
from source_intercom.utils import EagerlyCachedStreamState as stream_state_cache

# Define the Stream instances for the tests
INTERCOM_STREAM = Conversations(authenticator=NoAuth(), start_date=0)
INTERCOM_SUB_STREAM = ConversationParts(authenticator=NoAuth(), start_date=0)


@pytest.mark.parametrize(
    "stream, cur_stream_state, state_object, expected_output",
    [
        # When Full-Refresh: state_object: empty.
        (INTERCOM_STREAM, {INTERCOM_STREAM.cursor_field: ""}, {}, {INTERCOM_STREAM.name: {INTERCOM_STREAM.cursor_field: ""}}),
        (
            INTERCOM_SUB_STREAM,
            {INTERCOM_SUB_STREAM.cursor_field: ""},
            {},
            {INTERCOM_SUB_STREAM.name: {INTERCOM_SUB_STREAM.cursor_field: ""}},
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
            INTERCOM_STREAM,
            {INTERCOM_STREAM.cursor_field: "2021-01-01T01-01-01"},
            {},
            {INTERCOM_STREAM.name: {INTERCOM_STREAM.cursor_field: "2021-01-01T01-01-01"}},
        ),
        (
            INTERCOM_SUB_STREAM,
            {INTERCOM_SUB_STREAM.cursor_field: "2021-01-01T01-01-01"},
            {},
            {INTERCOM_SUB_STREAM.name: {INTERCOM_SUB_STREAM.cursor_field: "2021-01-01T01-01-01"}},
        ),
        # While doing the incremental refresh, we keeping the original state, even if the state is updated during the sync.
        (
            INTERCOM_STREAM,
            {INTERCOM_STREAM.cursor_field: "2021-01-05T02-02-02"},
            {},
            {INTERCOM_STREAM.name: {INTERCOM_STREAM.cursor_field: "2021-01-05T02-02-02"}},
        ),
        (
            INTERCOM_SUB_STREAM,
            {INTERCOM_SUB_STREAM.cursor_field: "2021-01-05T02-02-02"},
            {},
            {INTERCOM_SUB_STREAM.name: {INTERCOM_SUB_STREAM.cursor_field: "2021-01-05T02-02-02"}},
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
