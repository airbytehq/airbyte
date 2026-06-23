#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from freezegun import freeze_time
from source_shopify.streams.streams import Orders, TransactionsGraphql


def _make_stream(config):
    """Create an `Orders` stream instance for testing lookback window behavior."""
    return Orders(config)


def _base_config(**overrides):
    config = {
        "shop": "test_shop",
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "start_date": "2023-01-01",
        "authenticator": None,
    }
    config.update(overrides)
    return config


@pytest.mark.parametrize(
    "lookback_days,state_value,start_date,expected_substring",
    [
        pytest.param(None, "2025-03-15T00:00:00+00:00", "2023-01-01", "2025-03-15", id="no_lookback_configured"),
        pytest.param(0, "2025-03-15T00:00:00+00:00", "2023-01-01", "2025-03-15", id="lookback_zero"),
        pytest.param(3, "2025-03-15T00:00:00+00:00", "2023-01-01", "2025-03-12", id="lookback_3_days"),
        pytest.param(1, "2025-04-09T12:00:00+00:00", "2023-01-01", "2025-04-08", id="lookback_1_day_recommended"),
        pytest.param(30, "2025-04-09T00:00:00+00:00", "2023-01-01", "2025-03-10", id="lookback_30_days_max"),
        pytest.param(10, "2025-03-15T00:00:00+00:00", "2025-03-10", "2025-03-10", id="clamped_to_start_date"),
        pytest.param(5, "2025-03-15T00:00:00+00:00", None, "2025-03-10", id="no_start_date_no_clamp"),
    ],
)
def test_apply_lookback_window(lookback_days, state_value, start_date, expected_substring):
    """Verify `_apply_lookback_window` shifts state back by configured days, clamped to `start_date`."""
    overrides = {}
    if lookback_days is not None:
        overrides["lookback_window_in_days"] = lookback_days
    if start_date is not None:
        overrides["start_date"] = start_date

    config = _base_config(**overrides)
    if start_date is None:
        del config["start_date"]

    stream = _make_stream(config)
    result = stream._apply_lookback_window(state_value)
    assert expected_substring in result


@pytest.mark.parametrize(
    "lookback_days,stream_state,expected_filter_substring",
    [
        pytest.param(
            2,
            {"updated_at": "2025-03-15T00:00:00+00:00"},
            "2025-03-13",
            id="lookback_applied_to_filter",
        ),
        pytest.param(
            0,
            {"updated_at": "2025-03-15T00:00:00+00:00"},
            "2025-03-15",
            id="no_lookback_state_unchanged",
        ),
        pytest.param(
            2,
            None,
            "2023-01-01",
            id="no_state_uses_default_start_date",
        ),
    ],
)
def test_request_params_with_lookback(lookback_days, stream_state, expected_filter_substring):
    """Verify `request_params` applies (or skips) lookback for REST incremental streams."""
    config = _base_config(lookback_window_in_days=lookback_days)
    stream = _make_stream(config)
    params = stream.request_params(stream_state=stream_state)

    if expected_filter_substring is None:
        assert stream.filter_field not in params or params.get(stream.filter_field) is None
    else:
        filter_value = params.get(stream.filter_field, "")
        assert expected_filter_substring in filter_value


@freeze_time("2025-03-20T00:00:00Z")
def test_graphql_bulk_stream_slices_apply_lookback_window():
    """Verify `stream_slices` applies lookback for GraphQL BULK incremental streams."""
    config = _base_config(lookback_window_in_days=2)
    stream = TransactionsGraphql(config)
    stream.job_manager._job_size = 1000

    first_slice = next(stream.stream_slices(stream_state={"created_at": "2025-03-15T00:00:00Z"}))

    assert first_slice["start"] == "2025-03-13T00:00:00+00:00"
    assert first_slice["end"] == "2025-03-20T00:00:00+00:00"
