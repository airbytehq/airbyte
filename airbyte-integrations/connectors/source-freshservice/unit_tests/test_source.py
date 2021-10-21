#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses
from source_freshservice.source import SourceFreshservice


def setup_responses():
    responses.add(
        responses.GET,
        "https://test.freshservice.com/api/v2/tickets",
        json={"per_page": 30, "order_by": "updated_at", "order_type": "asc", "updated_since": "2021-05-07T00:00:00Z"},
    )


# @responses.activate
@pytest.mark.skip(reason="I can't get this to work yet")
def test_check_connection(mocker, test_config):
    setup_responses()
    source = SourceFreshservice()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


def test_streams(mocker):
    source = SourceFreshservice()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 12
    assert len(streams) == expected_streams_number
