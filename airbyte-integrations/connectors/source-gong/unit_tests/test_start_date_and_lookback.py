# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for 1.4.0 start-date and lookback-window behavior.

1.4.0 adds a `ConfigMigration` that pins `start_date: 1970-01-01T00:00:00Z` on
configs that omit it (preserving the pre-1.4.0 "sync all history" scope) and an
optional `lookback_window_days` that rewinds the saved cursor at the start of
each incremental sync. These tests assert the `fromDateTime` request parameter
the `calls` stream actually sends in each scenario, including that state
written by 1.3.5 (a plain `started` cursor) is honored unchanged by default.
"""

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CREDENTIALS = {
    "auth_type": "APIKey",
    "access_key": "test_access_key",
    "access_key_secret": "test_access_key_secret",
}

_CALLS_URL = "https://api.gong.io/v2/calls"

_EMPTY_RESPONSE = {
    "calls": [],
    "records": {"totalRecords": 0, "currentPageSize": 0, "currentPageNumber": 0},
}


def _sent_from_datetime(config, state=None) -> str:
    """Run an incremental read of `calls` and return the `fromDateTime` param sent."""
    source = get_source(config=config, state=state)
    catalog = CatalogBuilder().with_stream("calls", SyncMode.incremental).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(_CALLS_URL, json=_EMPTY_RESPONSE)
        read(source, config, catalog, state=state)
        requests_made = [r for r in mocker.request_history if r.path == "/v2/calls"]
        assert requests_made, "expected at least one request to /v2/calls"
        # requests_mock lowercases parsed query-string keys and values
        return requests_made[0].qs["fromdatetime"][0]


def test_config_without_start_date_is_pinned_to_epoch():
    """The ConfigMigration pins 1970-01-01 so the data scope stays 'all history'."""
    config = {"credentials": _CREDENTIALS}
    assert _sent_from_datetime(config) == "1970-01-01t00:00:00z"


def test_explicit_start_date_is_used_verbatim():
    config = {"credentials": _CREDENTIALS, "start_date": "2024-01-01T00:00:00Z"}
    assert _sent_from_datetime(config) == "2024-01-01t00:00:00z"


def test_saved_state_is_honored_unchanged_by_default():
    """With lookback unset (default 0), a 1.3.5-written cursor is used as-is."""
    config = {"credentials": _CREDENTIALS, "start_date": "2024-01-01T00:00:00Z"}
    state = StateBuilder().with_stream_state("calls", {"started": "2024-06-10T00:00:00Z"}).build()
    assert _sent_from_datetime(config, state) == "2024-06-10t00:00:00z"


def test_lookback_window_rewinds_saved_state():
    """`lookback_window_days: 7` re-opens the last 7 days before the saved cursor."""
    config = {
        "credentials": _CREDENTIALS,
        "start_date": "2024-01-01T00:00:00Z",
        "lookback_window_days": 7,
    }
    state = StateBuilder().with_stream_state("calls", {"started": "2024-06-10T00:00:00Z"}).build()
    assert _sent_from_datetime(config, state) == "2024-06-03t00:00:00z"


def test_lookback_window_never_rewinds_past_start_date():
    """The lookback is clamped to the configured start date."""
    config = {
        "credentials": _CREDENTIALS,
        "start_date": "2024-06-08T00:00:00Z",
        "lookback_window_days": 7,
    }
    state = StateBuilder().with_stream_state("calls", {"started": "2024-06-10T00:00:00Z"}).build()
    assert _sent_from_datetime(config, state) == "2024-06-08t00:00:00z"
