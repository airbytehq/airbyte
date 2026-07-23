#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from source_shiftbase.streams import Absentees, Availabilities, IncrementalShiftbaseStream

from airbyte_cdk.models import SyncMode


@pytest.fixture
def mock_accounts():
    """Fixture providing mock account configuration."""
    return [{"access_token": "test_token_123", "account_name": "test_account"}]


@pytest.fixture
def mock_start_date():
    """Fixture providing a mock start date."""
    return "2024-01-01"


@pytest.fixture
def patch_incremental_base_class(mocker):
    """Mock abstract methods to enable instantiating abstract class."""
    mocker.patch.object(IncrementalShiftbaseStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalShiftbaseStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalShiftbaseStream, "cursor_field", "updated")
    mocker.patch.object(IncrementalShiftbaseStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class, mock_accounts, mock_start_date):
    """Test that cursor_field is properly set."""
    stream = IncrementalShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    assert stream.cursor_field == "updated"


def test_get_updated_state(patch_incremental_base_class, mock_accounts, mock_start_date):
    """Test state update with new record."""
    stream = IncrementalShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)

    current_state = {}
    latest_record = {"account_name": "test_account", "updated": "2024-06-15T10:00:00Z"}

    new_state = stream.get_updated_state(current_state, latest_record)

    assert "test_account" in new_state
    assert new_state["test_account"]["updated"] == "2024-06-15T10:00:00Z"


def test_get_updated_state_preserves_newer(patch_incremental_base_class, mock_accounts, mock_start_date):
    """Test that state preserves newer cursor value."""
    stream = IncrementalShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)

    current_state = {"test_account": {"updated": "2024-07-01T10:00:00Z"}}
    latest_record = {
        "account_name": "test_account",
        "updated": "2024-06-15T10:00:00Z",  # Older than current state
    }

    new_state = stream.get_updated_state(current_state, latest_record)

    # Should keep the newer date
    assert new_state["test_account"]["updated"] == "2024-07-01T10:00:00Z"


def test_supports_incremental(patch_incremental_base_class, mock_accounts, mock_start_date):
    """Test that incremental stream supports incremental sync."""
    stream = IncrementalShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class, mock_accounts, mock_start_date):
    """Test that source_defined_cursor is True."""
    stream = IncrementalShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    assert stream.source_defined_cursor is True


def test_stream_checkpoint_interval(patch_incremental_base_class, mock_accounts, mock_start_date):
    """Test checkpoint interval is set."""
    stream = IncrementalShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    assert stream.state_checkpoint_interval == 100


def test_supported_sync_modes(patch_incremental_base_class, mock_accounts, mock_start_date):
    """Test that incremental streams support both full_refresh and incremental."""
    stream = IncrementalShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)

    assert SyncMode.full_refresh in stream.supported_sync_modes
    assert SyncMode.incremental in stream.supported_sync_modes


def test_absentees_cursor_field(mock_accounts, mock_start_date):
    """Test Absentees stream cursor field."""
    stream = Absentees(accounts=mock_accounts, start_date=mock_start_date)
    assert stream.cursor_field == "updated"


def test_availabilities_cursor_field(mock_accounts, mock_start_date):
    """Test Availabilities stream cursor field."""
    stream = Availabilities(accounts=mock_accounts, start_date=mock_start_date)
    assert stream.cursor_field == "date"


def test_request_params_with_state(patch_incremental_base_class, mock_accounts, mock_start_date):
    """Test that request_params uses state for filtering."""
    stream = IncrementalShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)

    stream_state = {"test_account": {"updated": "2024-06-01T00:00:00Z"}}

    params = stream.request_params(stream_state=stream_state)

    assert params["min_date"] == "2024-06-01T00:00:00Z"


def test_request_params_without_state(patch_incremental_base_class, mock_accounts, mock_start_date):
    """Test that request_params uses start_date when no state."""
    stream = IncrementalShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)

    params = stream.request_params(stream_state={})

    assert params["min_date"] == mock_start_date
