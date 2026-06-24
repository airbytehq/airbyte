#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_facebook_marketing.streams.patches import CursorPatch

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException


def _make_cursor(api_response_json, headers=None):
    """Create a CursorPatch instance with a mocked API that returns the given json value."""
    mock_response_obj = MagicMock()
    mock_response_obj.json.return_value = api_response_json
    mock_response_obj.headers.return_value = headers or {}

    mock_api = MagicMock()
    mock_api.call.return_value = mock_response_obj

    cursor = object.__new__(CursorPatch)
    cursor._api = mock_api
    cursor._path = "/test/path"
    cursor.params = {}
    cursor._finished_iteration = False
    cursor._include_summary = False
    cursor._queue = []
    cursor.build_objects_from_response = MagicMock(return_value=[])
    return cursor


@pytest.mark.parametrize(
    "non_dict_response",
    [
        pytest.param(
            "<html><body>Service Unavailable</body></html>",
            id="html_error_page",
        ),
        pytest.param(
            "Internal Server Error",
            id="plain_text_error",
        ),
        pytest.param(
            "",
            id="empty_string",
        ),
        pytest.param(
            '{"paging": {"next": "http://example.com"}}',
            id="json_string_not_parsed",
        ),
    ],
)
def test_load_next_page_raises_on_non_dict_response(non_dict_response):
    """CursorPatch.load_next_page() raises AirbyteTracedException when response is not a dict."""
    cursor = _make_cursor(non_dict_response)

    with pytest.raises(AirbyteTracedException) as exc_info:
        cursor.load_next_page()

    assert exc_info.value.failure_type == FailureType.transient_error
    assert "non-JSON response" in exc_info.value.message
    assert "str" in exc_info.value.internal_message


def test_load_next_page_raises_on_list_response():
    """CursorPatch.load_next_page() raises AirbyteTracedException when response is a list."""
    cursor = _make_cursor([{"id": "1"}])

    with pytest.raises(AirbyteTracedException) as exc_info:
        cursor.load_next_page()

    assert exc_info.value.failure_type == FailureType.transient_error
    assert "list" in exc_info.value.internal_message


def test_load_next_page_raises_on_none_response():
    """CursorPatch.load_next_page() raises AirbyteTracedException when response is None."""
    cursor = _make_cursor(None)

    with pytest.raises(AirbyteTracedException) as exc_info:
        cursor.load_next_page()

    assert exc_info.value.failure_type == FailureType.transient_error
    assert "NoneType" in exc_info.value.internal_message


def test_load_next_page_succeeds_with_valid_dict_response():
    """CursorPatch.load_next_page() processes a valid dict response without raising."""
    valid_response = {
        "data": [{"id": "123", "name": "test"}],
        "paging": {"next": "https://graph.facebook.com/v25.0/act_123/ads?after=abc&limit=25"},
    }
    cursor = _make_cursor(valid_response)
    cursor.build_objects_from_response = MagicMock(return_value=[{"id": "123"}])

    result = cursor.load_next_page()

    assert result is True
    assert cursor._finished_iteration is False
    assert "limit" in cursor.params


def test_load_next_page_last_page_sets_finished_iteration():
    """CursorPatch.load_next_page() sets _finished_iteration when no paging.next."""
    valid_response = {
        "data": [{"id": "123"}],
    }
    cursor = _make_cursor(valid_response)
    cursor.build_objects_from_response = MagicMock(return_value=[])

    result = cursor.load_next_page()

    assert result is False
    assert cursor._finished_iteration is True
