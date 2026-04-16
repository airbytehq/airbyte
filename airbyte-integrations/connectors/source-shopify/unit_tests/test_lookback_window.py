#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum as pdm
import pytest
from source_shopify.streams.base_streams import IncrementalShopifyStream


class ConcreteIncrementalStream(IncrementalShopifyStream):
    """Minimal concrete subclass for testing `_apply_lookback_window` and `request_params`."""

    data_field = "test_records"

    def get_json_schema(self):
        return {}


def _make_config(**overrides):
    base = {
        "shop": "test_shop",
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "authenticator": None,
        "start_date": "2023-01-01",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# _apply_lookback_window
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "lookback_days, start_date, state_value, expected_date",
    [
        pytest.param(None, "2023-01-01", "2023-06-15T10:00:00+00:00", "2023-06-15", id="no_lookback_config"),
        pytest.param(0, "2023-01-01", "2023-06-15T10:00:00+00:00", "2023-06-15", id="lookback_zero"),
        pytest.param(1, "2023-01-01", "2023-06-15T10:00:00+00:00", "2023-06-14", id="1_day"),
        pytest.param(3, "2023-01-01", "2023-06-15T10:00:00+00:00", "2023-06-12", id="3_days"),
        pytest.param(7, "2023-01-01", "2023-06-15T10:00:00+00:00", "2023-06-08", id="7_days"),
        pytest.param(30, "2023-01-01", "2023-06-15T10:00:00+00:00", "2023-05-16", id="30_days"),
        pytest.param(30, "2023-06-10", "2023-06-15T10:00:00+00:00", "2023-06-10", id="clamped_to_start_date"),
        pytest.param(5, None, "2023-06-15T10:00:00+00:00", "2023-06-10", id="no_start_date"),
    ],
)
def test_apply_lookback_window(lookback_days, start_date, state_value, expected_date):
    config_overrides = {}
    if lookback_days is not None:
        config_overrides["lookback_window_in_days"] = lookback_days
    if start_date is not None:
        config_overrides["start_date"] = start_date
    else:
        config_overrides["start_date"] = None

    config = _make_config(**config_overrides)
    if start_date is None:
        config.pop("start_date", None)

    stream = ConcreteIncrementalStream(config)
    result = stream._apply_lookback_window(state_value)
    result_date = pdm.parse(result)
    assert result_date.format("YYYY-MM-DD") == expected_date


# ---------------------------------------------------------------------------
# request_params integration with lookback
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "lookback_days, stream_state, expected_filter_value",
    [
        pytest.param(
            3,
            {"updated_at": "2023-06-15T10:00:00+00:00"},
            "2023-06-12",
            id="lookback_applied",
        ),
        pytest.param(
            None,
            {"updated_at": "2023-06-15T10:00:00+00:00"},
            "2023-06-15",
            id="no_lookback",
        ),
        pytest.param(
            3,
            None,
            None,
            id="no_state_uses_default",
        ),
    ],
)
def test_request_params_lookback(lookback_days, stream_state, expected_filter_value):
    config_overrides = {}
    if lookback_days is not None:
        config_overrides["lookback_window_in_days"] = lookback_days
    config = _make_config(**config_overrides)
    stream = ConcreteIncrementalStream(config)
    params = stream.request_params(stream_state=stream_state)

    if stream_state is None:
        # Falls back to start_date default
        assert params["updated_at_min"] == "2023-01-01"
    else:
        result_date = pdm.parse(params["updated_at_min"])
        assert result_date.format("YYYY-MM-DD") == expected_filter_value


def test_request_params_since_id_skips_lookback():
    """Lookback is NOT applied for streams using `since_id` filter."""
    config = _make_config(lookback_window_in_days=3)
    stream = ConcreteIncrementalStream(config)
    stream.filter_field = "since_id"
    stream.cursor_field = "id"
    state = {"id": 12345}
    params = stream.request_params(stream_state=state)
    assert params["since_id"] == 12345
