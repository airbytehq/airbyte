#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from source_open_exchange_rates.source import SourceOpenExchangeRates

logger = logging.getLogger("airbyte")


def test_check_connection(config, mock_stream):
    response = {
        "status": 200,
        "data": {
            "app_id": "KEY",
            "status": "active",
            "plan": {
                "name": "Free",
                "quota": "1000 requests / month",
                "update_frequency": "3600s",
                "features": {
                    "base": False,
                    "symbols": False,
                    "experimental": True,
                    "time-series": False,
                    "convert": False,
                    "bid-ask": False,
                    "ohlc": False,
                    "spot": False
                }
            },
            "usage": {
                "requests": 27,
                "requests_quota": 1000,
                "requests_remaining": 973,
                "days_elapsed": 1,
                "days_remaining": 29,
                "daily_average": 27
            }
        }
    }

    mock_stream(path="usage", response=response)
    ok, error_msg = SourceOpenExchangeRates().check_connection(logger, config=config)
    logger.info(error_msg)
    assert ok
    assert error_msg is None


def test_check_connection_quota_exceeded_exception(config, mock_stream):
    response = {
        "status": 200,
        "data": {
            "app_id": "KEY",
            "status": "active",
            "plan": {
                "name": "Free",
                "quota": "1000 requests / month",
                "update_frequency": "3600s",
                "features": {
                    "base": False,
                    "symbols": False,
                    "experimental": True,
                    "time-series": False,
                    "convert": False,
                    "bid-ask": False,
                    "ohlc": False,
                    "spot": False
                }
            },
            "usage": {
                "requests": 1000,
                "requests_quota": 1000,
                "requests_remaining": 0,
                "days_elapsed": 1,
                "days_remaining": 29,
                "daily_average": 27
            }
        }
    }

    mock_stream(path="usage", response=response, status_code=200)
    ok, error_msg = SourceOpenExchangeRates().check_connection(logger, config=config)

    assert not ok
    assert error_msg == "Quota exceeded"


def test_check_connection_invalid_appid_exception(config, mock_stream):
    response = {
        "error": True,
        "status": 401,
        "message": "invalid_app_id",
        "description": "Invalid App ID - please sign up at https://openexchangerates.org/signup, or contact support@openexchangerates.org."
    }

    mock_stream(path="usage", response=response, status_code=401)
    ok, error_msg = SourceOpenExchangeRates().check_connection(logger, config=config)

    assert not ok
    assert error_msg == response['description']
