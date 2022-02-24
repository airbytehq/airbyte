#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from unittest.mock import MagicMock

from source_open_exchange_rates.source import SourceOpenExchangeRates


def test_check_connection_fails(mocker):
    source = SourceOpenExchangeRates()
    logger_mock = MagicMock()
    config = {"app_id": pytest.oxr_app_id, "start_date": pytest.oxr_start_date}

    results = source.check_connection(logger_mock, config)

    assert isinstance(results, tuple)
    assert not results[0]
    assert results[1].startswith("Error 401")


def test_streams(mocker):
    source = SourceOpenExchangeRates()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
