# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.sources.streams.checkpoint import (
    FullRefreshCheckpointReader,
    IncrementalCheckpointReader,
    ResumableFullRefreshCheckpointReader,
)


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

    checkpoint_reader.observe({})
    assert checkpoint_reader.next() is None


def test_resumable_full_refresh_checkpoint_reader_no_incoming_state():
    checkpoint_reader = ResumableFullRefreshCheckpointReader(stream_state={})

    checkpoint_reader.observe({"synthetic_page_number": 1})
    assert checkpoint_reader.next() == {"synthetic_page_number": 1}

    checkpoint_reader.observe({"synthetic_page_number": 2})
    assert checkpoint_reader.next() == {"synthetic_page_number": 2}

    checkpoint_reader.observe({})
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
