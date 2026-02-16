"""Unit tests for SourceTulip."""

import json
import pytest
import requests
import requests_mock

from source_tulip.source import SourceTulip


@pytest.fixture
def source():
    return SourceTulip()


class TestCheckConnection:
    def test_success(self, source, mock_config):
        with requests_mock.Mocker() as m:
            m.get(
                "https://test.tulip.co/api/v3/w/W456/tables",
                json=[{"id": "T1", "label": "Table 1"}],
            )
            ok, err = source.check_connection(None, mock_config)
            assert ok is True
            assert err is None

    def test_success_without_workspace(self, source, mock_config_minimal):
        with requests_mock.Mocker() as m:
            m.get(
                "https://test.tulip.co/api/v3/tables",
                json=[{"id": "T1", "label": "Table 1"}],
            )
            ok, err = source.check_connection(None, mock_config_minimal)
            assert ok is True
            assert err is None

    def test_invalid_creds(self, source, mock_config):
        with requests_mock.Mocker() as m:
            m.get(
                "https://test.tulip.co/api/v3/w/W456/tables",
                status_code=401,
                json={"error": "Unauthorized"},
            )
            ok, err = source.check_connection(None, mock_config)
            assert ok is False
            assert "401" in err

    def test_missing_subdomain(self, source):
        config = {"api_key": "k", "api_secret": "s"}
        ok, err = source.check_connection(None, config)
        assert ok is False
        assert "subdomain" in err

    def test_missing_api_key(self, source):
        config = {"subdomain": "test", "api_secret": "s"}
        ok, err = source.check_connection(None, config)
        assert ok is False
        assert "api_key" in err

    def test_missing_api_secret(self, source):
        config = {"subdomain": "test", "api_key": "k"}
        ok, err = source.check_connection(None, config)
        assert ok is False
        assert "api_secret" in err

    def test_connection_error(self, source, mock_config):
        with requests_mock.Mocker() as m:
            m.get(
                "https://test.tulip.co/api/v3/w/W456/tables",
                exc=requests.exceptions.ConnectionError("refused"),
            )
            ok, err = source.check_connection(None, mock_config)
            assert ok is False
            assert "connect" in err.lower() or "Connect" in err


class TestStreams:
    def test_returns_multiple_streams(self, source, mock_config, mock_tables_list):
        with requests_mock.Mocker() as m:
            m.get(
                "https://test.tulip.co/api/v3/w/W456/tables",
                json=mock_tables_list,
            )
            streams = source.streams(mock_config)
            assert len(streams) == 2

    def test_stream_names_match_tables(self, source, mock_config, mock_tables_list):
        with requests_mock.Mocker() as m:
            m.get(
                "https://test.tulip.co/api/v3/w/W456/tables",
                json=mock_tables_list,
            )
            streams = source.streams(mock_config)
            names = [s.name for s in streams]
            # Each name should be generate_column_name(table_id, table_label)
            assert len(names) == 2
            assert all("__" in name for name in names)

    def test_streams_without_workspace(self, source, mock_config_minimal, mock_tables_list):
        with requests_mock.Mocker() as m:
            m.get(
                "https://test.tulip.co/api/v3/tables",
                json=mock_tables_list,
            )
            streams = source.streams(mock_config_minimal)
            assert len(streams) == 2

    def test_empty_tables(self, source, mock_config):
        with requests_mock.Mocker() as m:
            m.get(
                "https://test.tulip.co/api/v3/w/W456/tables",
                json=[],
            )
            streams = source.streams(mock_config)
            assert streams == []
