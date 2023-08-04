#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from source_avni.source import SourceAvni


def test_check_connection_success(mocker):
    with patch('source_avni.source.SourceAvni.get_client_id') as get_client_id_mock, \
         patch('source_avni.source.SourceAvni.get_token') as get_token_mock, \
         patch('source_avni.source.Subjects.read_records') as read_records_mock:
        get_client_id_mock.return_value = "ClientID"
        get_token_mock.return_value = "Token"
        read_records_mock.return_value = iter(["record1", "record2"])
        source = SourceAvni()
        config_mock = {"username": "test_user", "password": "test_password", "start_date": "2000-06-27T04:18:36.914Z"}
        result,msg = source.check_connection(None, config_mock)
        assert result is True


def test_streams(mocker):

    mocker.patch('source_avni.source.SourceAvni.get_token').return_value = 'fake_token'
    source = SourceAvni()
    config_mock = {"username": "test_user", "password": "test_password", "start_date": "2000-06-27T04:18:36.914Z"}
    streams = source.streams(config_mock)
    excepted_outcome = 4
    assert len(streams) == excepted_outcome


def test_get_client_id(mocker):

    source = SourceAvni()
    client_id = source.get_client_id()
    expected_length = 26
    assert len(client_id) == expected_length
