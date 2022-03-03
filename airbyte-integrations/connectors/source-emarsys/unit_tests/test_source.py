#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import requests
import pytest
from source_emarsys.source import SourceEmarsys


@pytest.fixture
def config():
    return {
        "username": "user1",
        "password": "secret",
        "contact_fields": ["field_a", "field_b"],
        "limit": 10,
        "recurring_contact_lists": [],
    }


def test_check_connection(mocker, config):
    source = SourceEmarsys()
    logger_mock = MagicMock()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"string_id": "field_a"}, {"string_id": "field_b"}, {"string_id": "field_c"}]
    }
    mocker.patch("source_emarsys.source.requests.get", return_value=mock_response)
    assert source.check_connection(logger_mock, config) == (True, None)


def test_check_connection__field_not_exist__false_raise(mocker, config):
    source = SourceEmarsys()
    logger_mock = MagicMock()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"string_id": "field_a"}]
    }
    mocker.patch("source_emarsys.source.requests.get", return_value=mock_response)
    result, exc = source.check_connection(logger_mock, config)
    assert not result
    assert isinstance(exc, ValueError)


def test_check_connection__no_field__false_no_raise(mocker, config):
    source = SourceEmarsys()
    logger_mock = MagicMock()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": []
    }
    mocker.patch("source_emarsys.source.requests.get", return_value=mock_response)
    assert source.check_connection(logger_mock, config) == (False, None)


def test_check_connection__request_fail__false_raise(mocker, config):
    source = SourceEmarsys()
    logger_mock = MagicMock()
    mocker.patch("source_emarsys.source.requests.get", side_effect=requests.exceptions.HTTPError)
    result, exc = source.check_connection(logger_mock, config)
    assert not result
    assert isinstance(exc, requests.exceptions.HTTPError)


def test_streams(config):
    source = SourceEmarsys()
    streams = source.streams(config)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
