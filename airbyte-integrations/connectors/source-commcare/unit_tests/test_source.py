#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock, patch

import pytest
from source_commcare.source import SourceCommcare


@pytest.fixture(name="config")
def config_fixture():
    return {"api_key": "apikey", "app_id": "appid", "project_space": "project_space", "start_date": "2022-01-01T00:00:00Z"}


@patch("source_commcare.source.Application.check_availability", return_value="true")
def test_check_connection_ok(mocker, config):
    source = SourceCommcare()
    logger_mock = Mock()
    assert source.check_connection(logger_mock, config=config) == (True, None)


def test_check_connection_fail(mocker, config):
    source = SourceCommcare()
    logger_mock = MagicMock()
    excepted_outcome = " Invalid apikey, project_space or app_id : 'api_key'"
    assert source.check_connection(logger_mock, config={}) == (False, excepted_outcome)
