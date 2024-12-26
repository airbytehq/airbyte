import pytest
from unittest.mock import MagicMock
from source_google_directory_v2.source import IncrementalGoogleDirectoryV2Stream


@pytest.fixture
def mock_credentials():
    return MagicMock()


class TestIncrementalStream(IncrementalGoogleDirectoryV2Stream):
    primary_key = "test_id"
    cursor_field = "creationTime"

    def path(self, **kwargs):
        return "test"


def test_cursor_field(mock_credentials):
    stream = TestIncrementalStream(credentials=mock_credentials)
    assert stream.cursor_field == "creationTime"


def test_get_updated_state(mock_credentials):
    stream = TestIncrementalStream(credentials=mock_credentials)
    current_stream_state = {"creationTime": "2021-01-01T00:00:00+00:00"}
    latest_record = {"creationTime": "2021-02-01T00:00:00+00:00"}
    expected_state = {"creationTime": "2021-02-01T00:00:00+00:00"}
    assert stream.get_updated_state(current_stream_state, latest_record) == expected_state


def test_stream_slices(mock_credentials):
    stream = TestIncrementalStream(credentials=mock_credentials)
    assert list(stream.stream_slices(
        sync_mode="incremental",
        cursor_field=None,
        stream_state=None
    )) == [{}]


def test_supports_incremental(mock_credentials):
    stream = TestIncrementalStream(credentials=mock_credentials)
    assert stream.supports_incremental


def test_source_defined_cursor(mock_credentials):
    stream = TestIncrementalStream(credentials=mock_credentials)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(mock_credentials):
    stream = TestIncrementalStream(credentials=mock_credentials)
    assert stream.state_checkpoint_interval == 100
