#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_shopify.streams.base_streams import IncrementalShopifyStream


class MockIncrementalShopifyStream(IncrementalShopifyStream):
    """A minimal mock implementation of IncrementalShopifyStream for testing."""

    data_field = "mock_data"

    def __init__(self, config):
        self.config = config
        self._transformer = None

    def get_json_schema(self):
        return {}


@pytest.mark.parametrize(
    "state_value,lookback_days,start_date,expected_result",
    [
        pytest.param(
            "2025-12-15T10:00:00+00:00",
            0,
            None,
            "2025-12-15T10:00:00+00:00",
            id="no_lookback_returns_original",
        ),
        pytest.param(
            "2025-12-15T10:00:00+00:00",
            1,
            None,
            "2025-12-14T10:00:00+00:00",
            id="1_day_lookback",
        ),
        pytest.param(
            "2025-12-15T10:00:00+00:00",
            7,
            None,
            "2025-12-08T10:00:00+00:00",
            id="7_days_lookback",
        ),
        pytest.param(
            "2025-12-15T10:00:00-08:00",
            3,
            None,
            "2025-12-12T10:00:00-08:00",
            id="lookback_preserves_timezone_offset",
        ),
        pytest.param(
            "2025-01-05T10:00:00+00:00",
            10,
            "2025-01-01",
            "2025-01-01T00:00:00+00:00",
            id="lookback_clamped_to_start_date",
        ),
        pytest.param(
            "2025-01-15T10:00:00+00:00",
            5,
            "2025-01-01",
            "2025-01-10T10:00:00+00:00",
            id="lookback_not_clamped_when_after_start_date",
        ),
        pytest.param(
            "2025-12-15T10:00:00+00:00",
            30,
            None,
            "2025-11-15T10:00:00+00:00",
            id="max_30_days_lookback",
        ),
    ],
)
def test_apply_lookback_window(state_value, lookback_days, start_date, expected_result):
    """Test that _apply_lookback_window correctly adjusts the state value."""
    config = {
        "shop": "test_shop",
        "lookback_window_in_days": lookback_days,
    }
    if start_date:
        config["start_date"] = start_date

    stream = MockIncrementalShopifyStream(config)
    result = stream._apply_lookback_window(state_value)

    assert result == expected_result


def test_apply_lookback_window_default_zero():
    """Test that lookback_window_in_days defaults to 0 when not configured."""
    config = {
        "shop": "test_shop",
    }
    stream = MockIncrementalShopifyStream(config)
    state_value = "2025-12-15T10:00:00+00:00"

    result = stream._apply_lookback_window(state_value)

    assert result == state_value


def test_request_params_applies_lookback_window():
    """Test that request_params applies the lookback window when stream_state exists."""
    config = {
        "shop": "test_shop",
        "lookback_window_in_days": 3,
        "authenticator": None,
    }
    stream = MockIncrementalShopifyStream(config)
    stream_state = {"updated_at": "2025-12-15T10:00:00+00:00"}

    params = stream.request_params(stream_state=stream_state)

    assert params["updated_at_min"] == "2025-12-12T10:00:00+00:00"


def test_request_params_no_lookback_without_state():
    """Test that request_params does not apply lookback when no stream_state exists."""
    config = {
        "shop": "test_shop",
        "lookback_window_in_days": 3,
        "authenticator": None,
    }
    stream = MockIncrementalShopifyStream(config)

    params = stream.request_params(stream_state=None)

    assert "updated_at_min" not in params or params.get("updated_at_min") == ""


def test_request_params_no_lookback_for_since_id():
    """Test that request_params does not apply lookback for since_id filter field."""
    config = {
        "shop": "test_shop",
        "lookback_window_in_days": 3,
        "authenticator": None,
    }
    stream = MockIncrementalShopifyStream(config)
    stream.filter_field = "since_id"
    stream.cursor_field = "id"
    stream_state = {"id": 12345}

    params = stream.request_params(stream_state=stream_state)

    assert params["since_id"] == 12345


def test_request_params_no_lookback_with_next_page_token():
    """Test that request_params does not apply lookback when next_page_token exists."""
    config = {
        "shop": "test_shop",
        "lookback_window_in_days": 3,
        "authenticator": None,
    }
    stream = MockIncrementalShopifyStream(config)
    stream_state = {"updated_at": "2025-12-15T10:00:00+00:00"}
    next_page_token = {"page_info": "abc123"}

    params = stream.request_params(stream_state=stream_state, next_page_token=next_page_token)

    assert "updated_at_min" not in params
    assert params.get("page_info") == "abc123"
