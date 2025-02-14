#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock, patch

import pytest
from source_commcare.source import SourceCommcare


@pytest.fixture(name="config")
def config_fixture_1():
    return {"api_key": "apikey", "app_id": "appid", "project_space": "project_space", "start_date": "2022-01-01T00:00:00Z",'form_fields_to_exclude':[], "include_archived": False}

@pytest.fixture(name="config_include_archived")
def config_fixture_2():
    return {"api_key": "apikey", "app_id": "appid", "project_space": "project_space", "start_date": "2022-01-01T00:00:00Z",'form_fields_to_exclude':[], "include_archived": True}


@patch("source_commcare.source.Application.read_records")
def test_check_connection_success(mock_read_records,config):
    mock_read_records.return_value = iter(["dummy_record"])

    source = SourceCommcare()
    logger_mock = Mock()

    result = source.check_connection(logger_mock, config=config)

    assert result == (True, None)
    mock_read_records.assert_called_once()

def test_check_connection_fail(mocker, config):
    source = SourceCommcare()
    logger_mock = MagicMock()
    excepted_outcome = " Invalid apikey, project_space or app_id : 'api_key'"
    assert source.check_connection(logger_mock, config={}) == (False, excepted_outcome)

def test_include_archived_false(config):
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

    # case 
    assert streams[1].app_id == "appid"
    assert streams[1].project_space == "project_space"
    assert streams[1].start_date == "2022-01-01T00:00:00Z"

def test_include_archived_true(config_include_archived):
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

    # case 
    assert streams[1].app_id == "appid"
    assert streams[1].project_space == "project_space"
    assert streams[1].start_date == "2022-01-01T00:00:00Z"
