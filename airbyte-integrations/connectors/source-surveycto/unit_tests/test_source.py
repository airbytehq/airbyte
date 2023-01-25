#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.models import ConnectorSpecification
from source_surveycto.helpers import Helpers
from source_surveycto.source import SourceSurveycto


@pytest.fixture(name='config')
def config_fixture():
    return {'server_name': 'server_name', 'form_id': 'form_id', 'start_date': 'Jan 09, 2022 00:00:00 AM', 'password': 'password', 'username': 'username'}


def test_spec():
    source = SourceSurveycto()
    logger_mock = MagicMock()
    spec = source.spec(logger_mock)
    assert source.check_connection(spec, ConnectorSpecification)


@patch("requests.get")
def test_check_connection(config):
    source = SourceSurveycto()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(config):
    source = SourceSurveycto()
    Helpers.call_survey_cto = MagicMock()
    streams = source.streams(config)
    assert len(streams) == 7
