#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging

import pytest
from source_adjust.source import SourceAdjust

from airbyte_cdk.models import Status


def mock_response():
    return {"rows": [{"mock1": "value1", "mock2": "value2"}]}


def test_check_connection(requests_mock, config_pass, report_url, auth_token):
    requests_mock.get(url=report_url, status_code=200, json=mock_response())
    source = SourceAdjust(config=config_pass, catalog=None, state=None)
    status = source.check(logging.getLogger(), config_pass)
    assert status.status == Status.SUCCEEDED


@pytest.mark.parametrize("until_today", [True, False])
def test_streams(config_pass, until_today):
    config = {**config_pass, "until_today": until_today}
    source = SourceAdjust(config=config, catalog=None, state=None)
    streams = source.streams(config)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
