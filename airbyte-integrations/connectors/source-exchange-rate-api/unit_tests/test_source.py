#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime
from unittest.mock import MagicMock

from source_exchange_rate_api.source import SourceExchangeRateApi
from airbyte_cdk.sources.streams.http import HttpStream


def test_check_connection(mocker):
    source = SourceExchangeRateApi()
    logger_mock, config_mock = MagicMock(), MagicMock()
    record = {
        'success': True,
        'timestamp': int(datetime.datetime.now().timestamp()),
        'base': '<base>',
        'date': str(datetime.date.today()),
        'rates': {'<base>': 1}
    }
    mocker.patch.object(
        HttpStream,
        "read_records",
        return_value=[record]
    )
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceExchangeRateApi()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
