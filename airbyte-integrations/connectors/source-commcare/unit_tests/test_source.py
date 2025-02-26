#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock, patch

import pytest
from source_commcare.source import SourceCommcare
from source_commcare.source import (
    scrub_unwanted_fields_,
    ensure_single_trailing_z,
    parse_datetime_with_microseconds,
)
from datetime import datetime


@pytest.fixture(name="config")
def config_fixture_1():
    """config fixture"""
    return {
        "api_key": "apikey",
        "app_id": "appid",
        "project_space": "project_space",
        "start_date": "2022-01-01T00:00:00Z",
        "form_fields_to_exclude": [],
        "include_archived": False,
    }


@pytest.fixture(name="config_include_archived")
def config_fixture_2():
    """include_archived=True config"""
    return {
        "api_key": "apikey",
        "app_id": "appid",
        "project_space": "project_space",
        "start_date": "2022-01-01T00:00:00Z",
        "form_fields_to_exclude": [],
        "include_archived": True,
    }


@patch("source_commcare.source.Application.read_records")
def test_check_connection_success(mock_read_records, config):
    """passing test for check_connection"""
    mock_read_records.return_value = iter(["dummy_record"])

    source = SourceCommcare()
    logger_mock = Mock()

    result = source.check_connection(logger_mock, config=config)

    assert result == (True, None)
    mock_read_records.assert_called_once()


def test_check_connection_fail(mocker, config):
    """failing test for check_connection"""
    source = SourceCommcare()
    logger_mock = MagicMock()
    excepted_outcome = " Invalid apikey, project_space or app_id : 'api_key'"
    assert source.check_connection(logger_mock, config={}) == (False, excepted_outcome)


def test_ensure_single_trailing_z():
    """tests ensure_single_trailing_z"""
    assert ensure_single_trailing_z("2022-01-01T00:00:00Z") == "2022-01-01T00:00:00Z"
    assert ensure_single_trailing_z("2022-01-01T00:00:00") == "2022-01-01T00:00:00Z"


def test_parse_datetime_with_microseconds():
    """tests parse_datetime_with_microseconds"""
    assert parse_datetime_with_microseconds("2022-01-01T00:00:00Z") == datetime(
        2022, 1, 1, 0, 0, 0
    )
    assert parse_datetime_with_microseconds("2022-01-01T00:00:00.123Z") == datetime(
        2022, 1, 1, 0, 0, 0, 123000
    )
    assert parse_datetime_with_microseconds("2022-01-01T00:00:00.123") == datetime(
        2022, 1, 1, 0, 0, 0, 123000
    )
    with pytest.raises(ValueError) as exinfo:
        parse_datetime_with_microseconds("hello")
    assert str(exinfo.value) == "Could not parse datetime string hello"


def test_include_archived_false(config):
    """tests generate_streams with include_archived as False"""
    source = SourceCommcare()
    appdata = [
        {
            "modules": [
                {
                    "forms": [
                        {
                            "xmlns": "namespace",
                            "name": {"en": "english_name"},
                        }
                    ]
                }
            ]
        }
    ]
    streams = source.generate_streams({}, config, appdata)
    assert len(streams) == 2

    # form
    assert streams[0].name == "english_name"
    assert streams[0].xmlns == "namespace"
    assert streams[0].include_archived == False


def test_include_archived_true(config_include_archived):
    """tests generate_streams with include_archived as True"""
    source = SourceCommcare()
    appdata = [
        {
            "modules": [
                {
                    "forms": [
                        {
                            "xmlns": "namespace",
                            "name": {"en": "english_name"},
                        }
                    ]
                }
            ]
        }
    ]
    streams = source.generate_streams({}, config_include_archived, appdata)
    assert len(streams) == 2

    # form
    assert streams[0].name == "english_name"
    assert streams[0].xmlns == "namespace"
    assert streams[0].include_archived == True


def test_scrub_unwanted_fields_1():
    """tests scrub_unwanted_fields"""
    retval = scrub_unwanted_fields_(
        {
            "_id": True,
            "name": True,
        },
        {
            "_id": "id",
            "name": "name",
            "age": 25,
        },
    )

    assert retval == {"age": 25}


def test_scrub_unwanted_fields_2():
    """tests scrub_unwanted_fields"""
    retval = scrub_unwanted_fields_(
        {
            "_id": True,
            "name": True,
        },
        {
            "_id": "id",
            "nameFirst": "name",
            "nameLast": "name",
            "nameMiddle": "name",
            "age": 25,
        },
    )
    assert retval == {"age": 25}


def test_scrub_unwanted_fields_3():
    """tests scrub_unwanted_fields"""
    retval = scrub_unwanted_fields_(
        {
            "_id": True,
            "name": True,
        },
        {
            "_id": "id",
            "subobj": {
                "nameFirst": "name",
                "nameLast": "name",
                "nameMiddle": "name",
            },
            "age": 25,
        },
    )
    assert retval == {"age": 25, "subobj": {}}
