#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Tests for CursorPatch.load_next_page() type guards.

These tests verify that CursorPatch handles malformed Facebook API responses
gracefully instead of raising TypeError when response data is not dict-typed.
"""

from unittest.mock import MagicMock

import pytest
from source_facebook_marketing.streams.patches import CursorPatch

from airbyte_cdk.utils import AirbyteTracedException


def _make_cursor_patch(response_json, include_summary=False):
    """Create a CursorPatch instance with a mocked API call returning the given response."""
    api = MagicMock()
    response_obj = MagicMock()
    response_obj.json.return_value = response_json
    response_obj.headers.return_value = {}
    api.call.return_value = response_obj

    cursor = object.__new__(CursorPatch)
    cursor._api = api
    cursor._path = "/test"
    cursor.params = {}
    cursor._finished_iteration = False
    cursor._include_summary = include_summary
    cursor._queue = []
    cursor._headers = {}
    cursor._total_count = 0
    cursor._summary = {}
    cursor._object_parser = MagicMock()
    cursor._object_parser.parse_multiple.return_value = []
    return cursor


class TestCursorPatchResponseTypeGuard:
    """Test that non-dict responses raise AirbyteTracedException."""

    def test_string_response_raises_traced_exception(self):
        cursor = _make_cursor_patch("some string response")
        with pytest.raises(AirbyteTracedException) as exc_info:
            cursor.load_next_page()
        assert exc_info.value.failure_type.value == "transient_error"
        assert "not a JSON object" in exc_info.value.message

    def test_none_response_raises_traced_exception(self):
        cursor = _make_cursor_patch(None)
        with pytest.raises(AirbyteTracedException) as exc_info:
            cursor.load_next_page()
        assert exc_info.value.failure_type.value == "transient_error"

    def test_list_response_raises_traced_exception(self):
        cursor = _make_cursor_patch([{"data": "item"}])
        with pytest.raises(AirbyteTracedException) as exc_info:
            cursor.load_next_page()
        assert exc_info.value.failure_type.value == "transient_error"

    def test_integer_response_raises_traced_exception(self):
        cursor = _make_cursor_patch(12345)
        with pytest.raises(AirbyteTracedException) as exc_info:
            cursor.load_next_page()
        assert exc_info.value.failure_type.value == "transient_error"


class TestCursorPatchPagingTypeGuard:
    """Test that non-dict 'paging' values are handled safely."""

    def test_paging_as_string_marks_finished(self):
        response = {"data": [], "paging": "not-a-dict"}
        cursor = _make_cursor_patch(response)
        cursor.load_next_page()
        assert cursor._finished_iteration is True

    def test_paging_as_none_marks_finished(self):
        response = {"data": [], "paging": None}
        cursor = _make_cursor_patch(response)
        cursor.load_next_page()
        assert cursor._finished_iteration is True

    def test_paging_as_list_marks_finished(self):
        response = {"data": [], "paging": ["next"]}
        cursor = _make_cursor_patch(response)
        cursor.load_next_page()
        assert cursor._finished_iteration is True

    def test_valid_paging_extracts_next_url(self):
        response = {
            "data": [{"id": "1"}],
            "paging": {"next": "https://graph.facebook.com/v25.0/act_123/ads?after=cursor123&limit=25"},
        }
        cursor = _make_cursor_patch(response)
        cursor.load_next_page()
        assert cursor._finished_iteration is False
        assert "after" in cursor.params
        assert cursor.params["after"] == "cursor123"

    def test_paging_without_next_marks_finished(self):
        response = {"data": [{"id": "1"}], "paging": {"cursors": {"before": "abc"}}}
        cursor = _make_cursor_patch(response)
        cursor.load_next_page()
        assert cursor._finished_iteration is True


class TestCursorPatchDataItemsTypeGuard:
    """Test that non-dict items in 'data' array are filtered out."""

    def test_string_items_filtered_from_data(self):
        response = {"data": ["bad_string", {"id": "1"}, "another_bad"]}
        cursor = _make_cursor_patch(response)
        cursor.load_next_page()
        # After filtering, only the dict item should remain
        assert response["data"] == [{"id": "1"}]

    def test_mixed_non_dict_items_filtered(self):
        response = {"data": [123, None, {"id": "2"}, True, {"id": "3"}]}
        cursor = _make_cursor_patch(response)
        cursor.load_next_page()
        assert response["data"] == [{"id": "2"}, {"id": "3"}]

    def test_all_dict_items_preserved(self):
        response = {"data": [{"id": "1"}, {"id": "2"}, {"id": "3"}]}
        cursor = _make_cursor_patch(response)
        cursor.load_next_page()
        assert response["data"] == [{"id": "1"}, {"id": "2"}, {"id": "3"}]

    def test_empty_data_list_no_error(self):
        response = {"data": []}
        cursor = _make_cursor_patch(response)
        result = cursor.load_next_page()
        assert result is False

    def test_data_not_a_list_passes_through(self):
        """When data is not a list, let SDK's parse_multiple handle it."""
        response = {"data": {"id": "single"}}
        cursor = _make_cursor_patch(response)
        cursor.load_next_page()
        # No filtering applied, parse_multiple called with original response
        cursor._object_parser.parse_multiple.assert_called_once_with(response)


class TestCursorPatchSummaryTypeGuard:
    """Test that non-dict 'summary' values are handled safely."""

    def test_summary_as_string_ignored(self):
        response = {"data": [], "summary": "not-a-dict"}
        cursor = _make_cursor_patch(response, include_summary=True)
        cursor.load_next_page()
        assert cursor._summary == {}
        assert cursor._total_count == 0

    def test_summary_as_none_ignored(self):
        response = {"data": [], "summary": None}
        cursor = _make_cursor_patch(response, include_summary=True)
        cursor.load_next_page()
        assert cursor._summary == {}

    def test_valid_summary_extracted(self):
        response = {"data": [], "summary": {"total_count": 42}}
        cursor = _make_cursor_patch(response, include_summary=True)
        cursor.load_next_page()
        assert cursor._total_count == 42
        assert cursor._summary == {"total_count": 42}

    def test_summary_not_extracted_when_include_summary_false(self):
        response = {"data": [], "summary": {"total_count": 42}}
        cursor = _make_cursor_patch(response, include_summary=False)
        cursor.load_next_page()
        assert cursor._total_count == 0
        assert cursor._summary == {}


class TestCursorPatchNormalOperation:
    """Test that normal/valid responses still work correctly."""

    def test_normal_response_with_data_and_paging(self):
        response = {
            "data": [{"id": "1"}, {"id": "2"}],
            "paging": {"next": "https://graph.facebook.com/v25.0/act_123/ads?after=xyz&limit=50"},
        }
        cursor = _make_cursor_patch(response)
        cursor._object_parser.parse_multiple.return_value = [MagicMock(), MagicMock()]
        result = cursor.load_next_page()
        assert result is True
        assert cursor._finished_iteration is False

    def test_last_page_response(self):
        response = {"data": [{"id": "1"}]}
        cursor = _make_cursor_patch(response)
        cursor._object_parser.parse_multiple.return_value = [MagicMock()]
        result = cursor.load_next_page()
        assert result is True
        assert cursor._finished_iteration is True

    def test_finished_iteration_returns_false(self):
        cursor = _make_cursor_patch({"data": []})
        cursor._finished_iteration = True
        result = cursor.load_next_page()
        assert result is False
