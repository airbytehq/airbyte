#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_visma_economic.source import SourceVismaEconomic


@responses.activate
def test_check_connection(mocker):
    responses.add(responses.GET, "https://restapi.e-conomic.com/accounts?skippages=0&pagesize=1", json={"collection": []})

    source = SourceVismaEconomic()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceVismaEconomic()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 7
    assert len(streams) == expected_streams_number
