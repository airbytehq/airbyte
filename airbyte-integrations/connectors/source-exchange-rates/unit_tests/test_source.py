#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

from source_exchange_rates.source import SourceExchangeRates

logger = logging.getLogger("airbyte")


def test_check_connection_ok(config, mock_stream):
    response = {"success": True, "timestamp": 1662681599, "historical": True, "base": "USD", "date": "2022-09-08", "rates": {"AED": 1}}
    mock_stream(config["start_date"], response=response)
    ok, error_msg = SourceExchangeRates().check_connection(logger, config=config)

    assert ok
    assert not error_msg


def test_check_connection_exception(config, mock_stream):
    message = (
        "You have exceeded your daily/monthly API rate limit. Please review and upgrade your subscription plan at "
        "https://promptapi.com/subscriptions to continue. "
    )
    response = {"message": message}
    mock_stream(config["start_date"], response=response, status_code=429)
    ok, error_msg = SourceExchangeRates().check_connection(logger, config=config)

    assert not ok
    assert error_msg == message


def test_streams(config):
    streams = SourceExchangeRates().streams(config)

    assert len(streams) == 1
