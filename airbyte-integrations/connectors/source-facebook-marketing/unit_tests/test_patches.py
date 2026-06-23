#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Tests for CursorPatch.load_next_page malformed response filtering."""

import logging
from unittest.mock import MagicMock, patch

import pytest
from source_facebook_marketing.streams.patches import CursorPatch


class FakeResponseObj:
    """Minimal fake for FacebookResponse returned by api.call()."""

    def __init__(self, json_data):
        self._json = json_data

    def json(self):
        return self._json

    def headers(self):
        return {}


def _make_cursor(response_json):
    """Create a CursorPatch instance with a mocked API that returns the given response."""
    mock_api = MagicMock()
    mock_api.call.return_value = FakeResponseObj(response_json)

    # Minimal params needed by Cursor.__init__
    target_objects_class = MagicMock()
    target_objects_class._default_read_fields = []

    cursor = CursorPatch.__new__(CursorPatch)
    cursor._api = mock_api
    cursor._path = "/test/path"
    cursor.params = {}
    cursor._finished_iteration = False
    cursor._include_summary = False
    cursor._total_count = None
    cursor._summary = None
    cursor._headers = {}
    cursor._queue = []
    cursor._source_object = None
    cursor._target_objects_class = target_objects_class

    return cursor


@pytest.mark.parametrize(
    "response_data,expected_filtered_count,expected_queue_len",
    [
        pytest.param(
            [{"id": "1", "name": "ad1"}, {"id": "2", "name": "ad2"}],
            0,
            2,
            id="all_valid_dicts",
        ),
        pytest.param(
            ["malformed_string", {"id": "1", "name": "ad1"}, {"id": "2", "name": "ad2"}],
            1,
            2,
            id="one_malformed_string_at_start",
        ),
        pytest.param(
            [{"id": "1", "name": "ad1"}, "bad_item", {"id": "2", "name": "ad2"}, "another_bad"],
            2,
            2,
            id="multiple_malformed_strings_scattered",
        ),
        pytest.param(
            ["only_strings", "no_dicts"],
            2,
            0,
            id="all_malformed_strings",
        ),
        pytest.param(
            [],
            0,
            0,
            id="empty_data_array",
        ),
    ],
)
def test_load_next_page_filters_malformed_items(response_data, expected_filtered_count, expected_queue_len, caplog):
    """CursorPatch.load_next_page filters non-dict items from response['data'] and logs a warning."""
    response_json = {
        "data": response_data,
        "paging": {"cursors": {"before": "abc", "after": "def"}},
    }
    cursor = _make_cursor(response_json)

    # Mock build_objects_from_response to return the filtered data items as-is
    def fake_build(response):
        return response.get("data", [])

    with patch.object(cursor, "build_objects_from_response", side_effect=fake_build):
        with caplog.at_level(logging.WARNING, logger="airbyte"):
            result = cursor.load_next_page()

    if expected_queue_len > 0:
        assert result is True
    else:
        assert result is False

    assert len(cursor._queue) == expected_queue_len

    if expected_filtered_count > 0:
        assert "Filtered" in caplog.text
        assert str(expected_filtered_count) in caplog.text
        assert "malformed non-dict item(s)" in caplog.text
        assert "facebook-python-business-sdk#641" in caplog.text
    else:
        assert "Filtered" not in caplog.text


def test_load_next_page_preserves_pagination():
    """CursorPatch.load_next_page correctly parses paging.next even with malformed data items."""
    response_json = {
        "data": ["bad_item", {"id": "1"}],
        "paging": {"next": "https://graph.facebook.com/v25.0/act_123/ads?limit=50&after=cursor_xyz"},
    }
    cursor = _make_cursor(response_json)

    with patch.object(cursor, "build_objects_from_response", return_value=[{"id": "1"}]):
        cursor.load_next_page()

    # Pagination should be parsed correctly
    assert "after" in cursor.params
    assert cursor.params["after"] == "cursor_xyz"
    assert not cursor._finished_iteration


def test_load_next_page_no_data_key():
    """CursorPatch.load_next_page handles responses without a 'data' key gracefully."""
    response_json = {
        "paging": {"cursors": {"before": "abc", "after": "def"}},
    }
    cursor = _make_cursor(response_json)

    with patch.object(cursor, "build_objects_from_response", return_value=[]):
        result = cursor.load_next_page()

    assert result is False
    assert cursor._finished_iteration is True
