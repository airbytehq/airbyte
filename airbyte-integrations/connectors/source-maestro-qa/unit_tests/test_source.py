#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import responses
from unittest.mock import MagicMock

from .helpers import setup_good_response, setup_bad_response, data_url
from source_maestro_qa.source import SourceMaestroQA


def test_get_auth(mocker):
    source = SourceMaestroQA()
    config_mock = {"api_key": "hello"}
    auth = source.get_auth(config_mock)
    assert auth.get_auth_header() == {"apitoken": "hello"}

@responses.activate
def test_check_connection(mocker):
    setup_good_response()

    source = SourceMaestroQA()
    logger_mock, config_mock = MagicMock(), {"api_key": "hello"}
    assert source.check_connection(logger_mock, config_mock) == (True, None)

@responses.activate
def test_check_connection_fail(mocker):
    setup_bad_response()

    source = SourceMaestroQA()
    logger_mock, config_mock = MagicMock(), {"api_key": "hello"}
    check, msg = source.check_connection(logger_mock, config_mock)
    assert check is False



def test_streams(mocker):
    source = SourceMaestroQA()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 8
    assert len(streams) == expected_streams_number
