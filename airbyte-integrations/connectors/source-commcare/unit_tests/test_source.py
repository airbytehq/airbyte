#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock

import pytest
from source_commcare.source import SourceCommcare


@pytest.fixture(name='config')
def config_fixture():
    return {'api_key': 'apikey', 'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}


def test_check_connection_ok(mocker, config):
    source = SourceCommcare()
    logger_mock = Mock()
    assert source.check_connection(logger_mock, config=config) == (True, None)


def test_check_connection_fail(mocker, config):
    source = SourceCommcare()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config={}) == (False, None)
