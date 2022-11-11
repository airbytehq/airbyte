# #
# # Copyright (c) 2022 Airbyte, Inc., all rights reserved.
# #
import pytest
from unittest.mock import Mock, MagicMock

from source_surveycto.source import SourceSurveycto
from source_surveycto.helpers import Helpers

@pytest.fixture(name='config')
def config_fixture():
    return {'server_name': 'server_name', 'form_id': 'form_id', 'start_date': 'Jan 09, 2022 00:00:00 AM', 'password': 'password', 'username': 'username'}

def test_check_connection(config):
    source = SourceSurveycto()
    logger_mock=Mock()
    assert source.check_connection(logger_mock, config=config) == (True, None)

def test_check_connection_fail(config):
    source = SourceSurveycto()
    logger_mock =MagicMock()
    assert source.check_connection(logger_mock, config={}) == (False, None)

def test_streams(config):
    source = SourceSurveycto()
    Helpers.call_survey_cto = MagicMock()
    streams = source.streams(config)

    expected_streams_number = 7
    assert len(streams) == expected_streams_number
