# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
from airbyte_cdk.sources.streams.checkpoint.substream_resumable_full_refresh_cursor import SubstreamResumableFullRefreshCursor
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.utils import AirbyteTracedException


def test_substream_resumable_full_refresh_cursor():
    """
    Test scenario where a set of parent record partitions are iterated over by the cursor resulting in a completed sync
    """
    expected_starting_state = {"states": []}

    expected_ending_state = {
        "states": [
            {"partition": {"musician_id": "kousei_arima"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"musician_id": "kaori_miyazono"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
        ]
    }

    partitions = [
        StreamSlice(partition={"musician_id": "kousei_arima"}, cursor_slice={}),
        StreamSlice(partition={"musician_id": "kaori_miyazono"}, cursor_slice={}),
    ]

    cursor = SubstreamResumableFullRefreshCursor()

    starting_state = cursor.get_stream_state()
    assert starting_state == expected_starting_state

    for partition in partitions:
        partition_state = cursor.select_state(partition)
        assert partition_state is None
        cursor.close_slice(partition)

    ending_state = cursor.get_stream_state()
    assert ending_state == expected_ending_state


def test_substream_resumable_full_refresh_cursor_with_state():
    """
    Test scenario where a set of parent record partitions are iterated over and previously completed parents are skipped
    """
    initial_state = {
        "states": [
            {"partition": {"musician_id": "kousei_arima"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"musician_id": "kaori_miyazono"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"musician_id": "takeshi_aiza"}, "cursor": {}},
        ]
    }

    expected_ending_state = {
        "states": [
            {"partition": {"musician_id": "kousei_arima"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"musician_id": "kaori_miyazono"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"musician_id": "takeshi_aiza"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"musician_id": "emi_igawa"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
        ]
    }

    partitions = [
        StreamSlice(partition={"musician_id": "kousei_arima"}, cursor_slice={}),
        StreamSlice(partition={"musician_id": "kaori_miyazono"}, cursor_slice={}),
        StreamSlice(partition={"musician_id": "takeshi_aiza"}, cursor_slice={}),
        StreamSlice(partition={"musician_id": "emi_igawa"}, cursor_slice={}),
    ]

    cursor = SubstreamResumableFullRefreshCursor()
    cursor.set_initial_state(initial_state)

    starting_state = cursor.get_stream_state()
    assert starting_state == initial_state

    for i, partition in enumerate(partitions):
        partition_state = cursor.select_state(partition)
        if i < len(initial_state.get("states")):
            assert partition_state == initial_state.get("states")[i].get("cursor")
        else:
            assert partition_state is None
        cursor.close_slice(partition)

    ending_state = cursor.get_stream_state()
    assert ending_state == expected_ending_state


def test_set_initial_state_invalid_incoming_state():
    bad_state = {"next_page_token": 2}
    cursor = SubstreamResumableFullRefreshCursor()

    with pytest.raises(AirbyteTracedException):
        cursor.set_initial_state(bad_state)


def test_select_state_without_slice():
    cursor = SubstreamResumableFullRefreshCursor()

    with pytest.raises(ValueError):
        cursor.select_state()
