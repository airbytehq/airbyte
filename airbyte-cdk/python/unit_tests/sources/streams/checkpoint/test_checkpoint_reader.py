# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.streams.checkpoint import (
    CursorBasedCheckpointReader,
    FullRefreshCheckpointReader,
    IncrementalCheckpointReader,
    LegacyCursorBasedCheckpointReader,
    ResumableFullRefreshCheckpointReader,
)
from airbyte_cdk.sources.types import StreamSlice


def test_incremental_checkpoint_reader_next_slice():
    stream_slices = [
        {"start_date": "2024-01-01", "end_date": "2024-02-01"},
        {"start_date": "2024-02-01", "end_date": "2024-03-01"},
        {"start_date": "2024-03-01", "end_date": "2024-04-01"},
    ]
    checkpoint_reader = IncrementalCheckpointReader(stream_slices=stream_slices, stream_state={})

    assert checkpoint_reader.next() == stream_slices[0]
    checkpoint_reader.observe({"updated_at": "2024-01-15"})
    assert checkpoint_reader.get_checkpoint() == {"updated_at": "2024-01-15"}
    assert checkpoint_reader.next() == stream_slices[1]
    checkpoint_reader.observe({"updated_at": "2024-02-15"})
    assert checkpoint_reader.get_checkpoint() == {"updated_at": "2024-02-15"}
    assert checkpoint_reader.next() == stream_slices[2]
    checkpoint_reader.observe({"updated_at": "2024-03-15"})
    assert checkpoint_reader.get_checkpoint() == {"updated_at": "2024-03-15"}

    # Validate that after iterating over every slice, the final get_checkpoint() call is None so that
    # no duplicate final state message is emitted
    assert checkpoint_reader.next() is None
    assert checkpoint_reader.get_checkpoint() is None


def test_incremental_checkpoint_reader_incoming_state():
    incoming_state = {"updated_at": "2024-04-01"}
    checkpoint_reader = IncrementalCheckpointReader(stream_slices=[], stream_state=incoming_state)

    assert checkpoint_reader.get_checkpoint() == incoming_state

    expected_state = {"cursor": "new_state_value"}
    checkpoint_reader.observe(expected_state)

    assert checkpoint_reader.get_checkpoint() == expected_state


def test_resumable_full_refresh_checkpoint_reader_next():
    checkpoint_reader = ResumableFullRefreshCheckpointReader(stream_state={"synthetic_page_number": 55})

    checkpoint_reader.observe({"synthetic_page_number": 56})
    assert checkpoint_reader.next() == {"synthetic_page_number": 56}

    checkpoint_reader.observe({"synthetic_page_number": 57})
    assert checkpoint_reader.next() == {"synthetic_page_number": 57}

    checkpoint_reader.observe({"__ab_full_refresh_sync_complete": True})
    assert checkpoint_reader.next() is None


def test_resumable_full_refresh_checkpoint_reader_no_incoming_state():
    checkpoint_reader = ResumableFullRefreshCheckpointReader(stream_state={})

    checkpoint_reader.observe({"synthetic_page_number": 1})
    assert checkpoint_reader.next() == {"synthetic_page_number": 1}

    checkpoint_reader.observe({"synthetic_page_number": 2})
    assert checkpoint_reader.next() == {"synthetic_page_number": 2}

    checkpoint_reader.observe({"__ab_full_refresh_sync_complete": True})
    assert checkpoint_reader.next() is None


def test_full_refresh_checkpoint_reader_next():
    checkpoint_reader = FullRefreshCheckpointReader([{}])

    assert checkpoint_reader.next() == {}
    assert checkpoint_reader.get_checkpoint() is None
    assert checkpoint_reader.next() is None
    assert checkpoint_reader.get_checkpoint() == {"__ab_no_cursor_state_message": True}


def test_full_refresh_checkpoint_reader_substream():
    checkpoint_reader = FullRefreshCheckpointReader([{"partition": 1}, {"partition": 2}])

    assert checkpoint_reader.next() == {"partition": 1}
    assert checkpoint_reader.get_checkpoint() is None
    assert checkpoint_reader.next() == {"partition": 2}
    assert checkpoint_reader.get_checkpoint() is None
    assert checkpoint_reader.next() is None
    assert checkpoint_reader.get_checkpoint() == {"__ab_no_cursor_state_message": True}


def test_cursor_based_checkpoint_reader_incremental():
    expected_slices = [
        StreamSlice(cursor_slice={"start_date": "2024-01-01", "end_date": "2024-02-01"}, partition={}),
        StreamSlice(cursor_slice={"start_date": "2024-02-01", "end_date": "2024-03-01"}, partition={}),
        StreamSlice(cursor_slice={"start_date": "2024-03-01", "end_date": "2024-04-01"}, partition={}),
    ]

    expected_stream_state = {"end_date": "2024-02-01"}

    incremental_cursor = Mock()
    incremental_cursor.stream_slices.return_value = expected_slices
    incremental_cursor.select_state.return_value = expected_stream_state
    incremental_cursor.get_stream_state.return_value = expected_stream_state

    checkpoint_reader = CursorBasedCheckpointReader(
        cursor=incremental_cursor, stream_slices=incremental_cursor.stream_slices(), read_state_from_cursor=False
    )

    assert checkpoint_reader.next() == expected_slices[0]
    actual_state = checkpoint_reader.get_checkpoint()
    assert actual_state == expected_stream_state
    assert checkpoint_reader.next() == expected_slices[1]
    assert checkpoint_reader.next() == expected_slices[2]
    finished = checkpoint_reader.next()
    assert finished is None

    # A finished checkpoint_reader should return None for the final checkpoint to avoid emitting duplicate state
    assert checkpoint_reader.get_checkpoint() is None


def test_cursor_based_checkpoint_reader_resumable_full_refresh():
    expected_slices = [
        StreamSlice(cursor_slice={}, partition={}),
        StreamSlice(cursor_slice={"next_page_token": 2}, partition={}),
        StreamSlice(cursor_slice={"next_page_token": 3}, partition={}),
        StreamSlice(cursor_slice={"next_page_token": 4}, partition={}),
        StreamSlice(cursor_slice={"__ab_full_refresh_sync_complete": True}, partition={}),
    ]

    expected_stream_state = {"next_page_token": 2}

    rfr_cursor = Mock()
    rfr_cursor.stream_slices.return_value = [StreamSlice(cursor_slice={}, partition={})]
    rfr_cursor.select_state.side_effect = expected_slices
    rfr_cursor.get_stream_state.return_value = expected_stream_state

    checkpoint_reader = CursorBasedCheckpointReader(
        cursor=rfr_cursor, stream_slices=rfr_cursor.stream_slices(), read_state_from_cursor=True
    )

    assert checkpoint_reader.next() == expected_slices[0]
    actual_state = checkpoint_reader.get_checkpoint()
    assert actual_state == expected_stream_state
    assert checkpoint_reader.next() == expected_slices[1]
    assert checkpoint_reader.next() == expected_slices[2]
    assert checkpoint_reader.next() == expected_slices[3]
    finished = checkpoint_reader.next()
    assert finished is None

    # A finished checkpoint_reader should return None for the final checkpoint to avoid emitting duplicate state
    assert checkpoint_reader.get_checkpoint() is None


def test_cursor_based_checkpoint_reader_resumable_full_refresh_parents():
    expected_slices = [
        StreamSlice(cursor_slice={"next_page_token": 2}, partition={"parent_id": "zaheer"}),
        StreamSlice(cursor_slice={"next_page_token": 3}, partition={"parent_id": "zaheer"}),
        StreamSlice(cursor_slice={"next_page_token": 2}, partition={"parent_id": "pli"}),
        StreamSlice(cursor_slice={"next_page_token": 3}, partition={"parent_id": "pli"}),
    ]

    expected_stream_state = {"next_page_token": 2}

    rfr_cursor = Mock()
    rfr_cursor.stream_slices.return_value = [
        StreamSlice(cursor_slice={}, partition={"parent_id": "zaheer"}),
        StreamSlice(cursor_slice={}, partition={"parent_id": "pli"}),
    ]
    rfr_cursor.select_state.side_effect = [
        {"next_page_token": 2},
        {"next_page_token": 3},
        {"__ab_full_refresh_sync_complete": True},
        {"next_page_token": 2},
        {"next_page_token": 3},
        {"__ab_full_refresh_sync_complete": True},
    ]
    rfr_cursor.get_stream_state.return_value = expected_stream_state

    checkpoint_reader = CursorBasedCheckpointReader(
        cursor=rfr_cursor, stream_slices=rfr_cursor.stream_slices(), read_state_from_cursor=True
    )

    assert checkpoint_reader.next() == expected_slices[0]
    actual_state = checkpoint_reader.get_checkpoint()
    assert actual_state == expected_stream_state
    assert checkpoint_reader.next() == expected_slices[1]
    assert checkpoint_reader.next() == expected_slices[2]
    assert checkpoint_reader.next() == expected_slices[3]
    finished = checkpoint_reader.next()
    assert finished is None

    # A finished checkpoint_reader should return None for the final checkpoint to avoid emitting duplicate state
    assert checkpoint_reader.get_checkpoint() is None


def test_cursor_based_checkpoint_reader_skip_completed_parent_slices():
    expected_slices = [
        StreamSlice(cursor_slice={"next_page_token": 2}, partition={"parent_id": "bolin"}),
        StreamSlice(cursor_slice={"next_page_token": 3}, partition={"parent_id": "bolin"}),
        StreamSlice(cursor_slice={"next_page_token": 7}, partition={"parent_id": "pabu"}),
        StreamSlice(cursor_slice={"next_page_token": 8}, partition={"parent_id": "pabu"}),
    ]

    expected_stream_state = {"next_page_token": 2}

    rfr_cursor = Mock()
    rfr_cursor.stream_slices.return_value = [
        StreamSlice(cursor_slice={}, partition={"parent_id": "korra"}),
        StreamSlice(cursor_slice={}, partition={"parent_id": "mako"}),
        StreamSlice(cursor_slice={}, partition={"parent_id": "bolin"}),
        StreamSlice(cursor_slice={}, partition={"parent_id": "asami"}),
        StreamSlice(cursor_slice={}, partition={"parent_id": "naga"}),
        StreamSlice(cursor_slice={}, partition={"parent_id": "pabu"}),
    ]
    rfr_cursor.select_state.side_effect = [
        {"__ab_full_refresh_sync_complete": True},
        {"__ab_full_refresh_sync_complete": True},
        {"next_page_token": 2},
        {"next_page_token": 3},
        {"__ab_full_refresh_sync_complete": True},
        {"__ab_full_refresh_sync_complete": True},
        {"__ab_full_refresh_sync_complete": True},
        {"next_page_token": 7},
        {"next_page_token": 8},
    ]
    rfr_cursor.get_stream_state.return_value = expected_stream_state

    checkpoint_reader = CursorBasedCheckpointReader(
        cursor=rfr_cursor, stream_slices=rfr_cursor.stream_slices(), read_state_from_cursor=True
    )

    assert checkpoint_reader.next() == expected_slices[0]
    actual_state = checkpoint_reader.get_checkpoint()
    assert actual_state == expected_stream_state
    assert checkpoint_reader.next() == expected_slices[1]
    assert checkpoint_reader.next() == expected_slices[2]
    assert checkpoint_reader.next() == expected_slices[3]
    finished = checkpoint_reader.next()
    assert finished is None

    # A finished checkpoint_reader should return None for the final checkpoint to avoid emitting duplicate state
    assert checkpoint_reader.get_checkpoint() is None


def test_cursor_based_checkpoint_reader_sync_first_parent_slice():
    expected_slices = [
        StreamSlice(cursor_slice={"next_page_token": 3}, partition={"parent_id": "bolin"}),
        StreamSlice(cursor_slice={"next_page_token": 4}, partition={"parent_id": "bolin"}),
        StreamSlice(cursor_slice={"next_page_token": 4}, partition={"parent_id": "bolin"}),
    ]

    expected_stream_state = {"next_page_token": 3}

    rfr_cursor = Mock()
    rfr_cursor.stream_slices.return_value = [
        StreamSlice(cursor_slice={}, partition={"parent_id": "bolin"}),
        StreamSlice(cursor_slice={}, partition={"parent_id": "asami"}),
        StreamSlice(cursor_slice={}, partition={"parent_id": "naga"}),
    ]
    rfr_cursor.select_state.side_effect = [
        {"next_page_token": 3},  # Accounts for the first invocation when checking if partition was already successful
        {"next_page_token": 4},
        {"next_page_token": 4},
        {"__ab_full_refresh_sync_complete": True},
        {"__ab_full_refresh_sync_complete": True},
        {"__ab_full_refresh_sync_complete": True},
    ]
    rfr_cursor.get_stream_state.return_value = expected_stream_state

    checkpoint_reader = CursorBasedCheckpointReader(
        cursor=rfr_cursor, stream_slices=rfr_cursor.stream_slices(), read_state_from_cursor=True
    )

    assert checkpoint_reader.next() == expected_slices[0]
    actual_state = checkpoint_reader.get_checkpoint()
    assert actual_state == expected_stream_state
    assert checkpoint_reader.next() == expected_slices[1]
    assert checkpoint_reader.next() == expected_slices[2]
    finished = checkpoint_reader.next()
    assert finished is None

    # A finished checkpoint_reader should return None for the final checkpoint to avoid emitting duplicate state
    assert checkpoint_reader.get_checkpoint() is None


def test_cursor_based_checkpoint_reader_resumable_full_refresh_invalid_slice():
    rfr_cursor = Mock()
    rfr_cursor.stream_slices.return_value = [{"invalid": "stream_slice"}]
    rfr_cursor.select_state.side_effect = [StreamSlice(cursor_slice={"invalid": "stream_slice"}, partition={})]

    checkpoint_reader = CursorBasedCheckpointReader(
        cursor=rfr_cursor, stream_slices=rfr_cursor.stream_slices(), read_state_from_cursor=True
    )

    with pytest.raises(ValueError):
        checkpoint_reader.next()


def test_legacy_cursor_based_checkpoint_reader_resumable_full_refresh():
    expected_mapping_slices = [
        {"parent_id": 400, "partition": {"parent_id": 400}, "cursor_slice": {}},
        {"parent_id": 400, "next_page_token": 2, "partition": {"parent_id": 400}, "cursor_slice": {"next_page_token": 2}},
        {"parent_id": 400, "next_page_token": 2, "partition": {"parent_id": 400}, "cursor_slice": {"next_page_token": 2}},
        {"parent_id": 400, "next_page_token": 3, "partition": {"parent_id": 400}, "cursor_slice": {"next_page_token": 3}},
        {"parent_id": 400, "next_page_token": 4, "partition": {"parent_id": 400}, "cursor_slice": {"next_page_token": 4}},
        {
            "parent_id": 400,
            "__ab_full_refresh_sync_complete": True,
            "partition": {"parent_id": 400},
            "cursor_slice": {"__ab_full_refresh_sync_complete": True},
        },
    ]

    mocked_state = [
        {},
        {"next_page_token": 2},
        {"next_page_token": 3},
        {"next_page_token": 4},
        {"__ab_full_refresh_sync_complete": True},
    ]

    expected_stream_state = {"next_page_token": 2}

    rfr_cursor = Mock()
    rfr_cursor.stream_slices.return_value = [{"parent_id": 400}]
    rfr_cursor.select_state.side_effect = mocked_state
    rfr_cursor.get_stream_state.return_value = expected_stream_state

    checkpoint_reader = LegacyCursorBasedCheckpointReader(
        cursor=rfr_cursor, stream_slices=rfr_cursor.stream_slices(), read_state_from_cursor=True
    )

    assert checkpoint_reader.next() == expected_mapping_slices[0]
    actual_state = checkpoint_reader.get_checkpoint()
    assert actual_state == expected_stream_state
    assert checkpoint_reader.next() == expected_mapping_slices[2]
    assert checkpoint_reader.next() == expected_mapping_slices[3]
    assert checkpoint_reader.next() == expected_mapping_slices[4]
    finished = checkpoint_reader.next()
    assert finished is None

    # A finished checkpoint_reader should return None for the final checkpoint to avoid emitting duplicate state
    assert checkpoint_reader.get_checkpoint() is None
