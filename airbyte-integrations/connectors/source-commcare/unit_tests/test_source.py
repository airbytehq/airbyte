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
    update_case_request_params,
    mk_case_record,
    mk_form_record,
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
        "import_all_cases": False,
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
        "import_all_cases": False,
        "include_archived": True,
    }


@pytest.fixture(name="config_import_all_cases")
def config_fixture_3():
    """import_all_cases=True config"""
    return {
        "api_key": "apikey",
        "app_id": "appid",
        "project_space": "project_space",
        "start_date": "2022-01-01T00:00:00Z",
        "form_fields_to_exclude": [],
        "import_all_cases": True,
        "include_archived": False,
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
    assert streams[0].include_archived is False


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
    assert streams[0].include_archived is True


def test_import_all_cases_true(config_import_all_cases):
    """tests generate_streams with import_all_cases as True"""
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
    streams = source.generate_streams({}, config_import_all_cases, appdata)
    assert len(streams) == 2

    # case
    assert streams[1].import_all_cases is True


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


def test_update_case_request_params():
    """tests update_case_request_params"""
    assert update_case_request_params(
        {
            "indexed_on_start": "2022-01-01T00:00:00",
            "offset": "10",
        },
        {
            "format": ["json"],
            "indexed_on_start": ["2024-12-01T00:00:00.000000"],
            "order_by": ["indexed_on"],
            "limit": ["5000"],
            "offset": ["5000"],
        },
        "2022-01-01T00:00:00Z",
    ) == {
        "format": ["json"],
        "indexed_on_start": ["2024-12-01T00:00:00.000000"],
        "order_by": ["indexed_on"],
        "limit": ["5000"],
        "offset": ["5000"],
    }
    assert update_case_request_params(
        {
            "indexed_on_start": "2022-01-01T00:00:00",
            "offset": "0",
        },
        {
            "format": ["json"],
            "indexed_on_start": ["2024-12-01T00:00:00.000000"],
            "order_by": ["indexed_on"],
            "limit": ["5000"],
            "offset": ["900000"],
        },
        "2022-02-01T00:00:00Z",
    ) == {
        "format": ["json"],
        "indexed_on_start": "2022-02-01T00:00:00",
        "order_by": ["indexed_on"],
        "limit": ["5000"],
        "offset": "0",
    }


def test_mk_case_record():
    """tests mk_case_record"""
    assert mk_case_record(
        {
            "k1": "v1",
            "indexed_on": "2022-01-01T00:00:00",
            "id": "record-id",
            "xform_ids": ["form-1", "form-2", "form-3"],
        }
    ) == {
        "id": "record-id",
        "indexed_on": "2022-01-01T00:00:00Z",
        "data": {
            "k1": "v1",
            "streamname": "case",
            "indexed_on": "2022-01-01T00:00:00Z",
            "id": "record-id",
            "xform_ids": "form-1,form-2,form-3",
        },
    }


def test_mk_form_record():
    """tests mk_form_record"""
    assert mk_form_record(
        {
            "exclude": "this field",
            "k1": "v1",
            "id": "form-id",
            "indexed_on": "2022-01-01T00:00:00",
        },
        {"exclude": True},
        "indexed_on",
    ) == {
        "id": "form-id",
        "indexed_on": "2022-01-01T00:00:00Z",
        "data": {
            "id": "form-id",
            "k1": "v1",
            "indexed_on": "2022-01-01T00:00:00Z",
        },
    }
