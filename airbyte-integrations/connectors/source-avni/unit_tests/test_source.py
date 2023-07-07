#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_avni.source import SourceAvni


def test_check_connection(mocker):
    
    mocker.patch('source_avni.source.SourceAvni.get_token').return_value="Token"
    mocker.patch('source_avni.source.requests.get').return_value.status_code=200
    source = SourceAvni()
    logger_mock= MagicMock()
    config_mock = {"username": "test_user", "password": "test_password"}
    result, error = source.check_connection(logger_mock, config_mock)
    assert result is True


def test_streams(mocker):

    mocker.patch('source_avni.source.SourceAvni.get_token').return_value = 'fake_token'
    source = SourceAvni()
    config_mock = {"username": "test_user", "password": "test_password", "lastModifiedDateTime": "2000-06-27T04:18:36.914Z"}
    streams = source.streams(config_mock)
    excepted_outcome=1
    assert len(streams)==excepted_outcome
    
def test_get_client_id(mocker):
    
    source = SourceAvni()
    client_id=source.get_client_id()
    expected_length=26
    assert len(client_id)==expected_length