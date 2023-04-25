#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock, patch

import pendulum
import pytest
import source_stripe
from source_stripe import SourceStripe
from source_stripe.source import Invoices

now_dt = pendulum.now()

SECONDS_IN_DAY = 24 * 60 * 60


@pytest.mark.parametrize(
    "lookback_window_days, current_state, expected, message",
    [
        (None, now_dt.timestamp(), now_dt.timestamp(), "if lookback_window_days is not set should not affect cursor value"),
        (0, now_dt.timestamp(), now_dt.timestamp(), "if lookback_window_days is not set should not affect cursor value"),
        (10, now_dt.timestamp(), int(now_dt.timestamp() - SECONDS_IN_DAY * 10), "Should calculate cursor value as expected"),
        # ignore sign
        (-10, now_dt.timestamp(), int(now_dt.timestamp() - SECONDS_IN_DAY * 10), "Should not care for the sign, use the module"),
    ],
)
def test_lookback_window(lookback_window_days, current_state, expected, message):
    inv_stream = Invoices(account_id=213, start_date=1577836800, lookback_window_days=lookback_window_days)
    inv_stream.cursor_field = "created"
    assert inv_stream.get_start_timestamp({"created": current_state}) == expected, message


def test_source_streams():
    with open("sample_files/config.json") as f:
        config = json.load(f)
    streams = SourceStripe().streams(config=config)
    assert len(streams) == 27


@pytest.fixture(name="config")
def config_fixture():
    config = {"client_secret": "sk_test(live)_<secret>", "account_id": "<account_id>", "start_date": "2020-05-01T00:00:00Z"}
    return config


@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return patch("source_tiktok_marketing.source.logger")


@patch.object(source_stripe.source, "stripe")
def test_source_check_connection_ok(mocked_client, config, logger_mock):
    assert SourceStripe().check_connection(logger_mock, config=config) == (True, None)


@patch.object(source_stripe.source, "stripe")
def test_source_check_connection_failure(mocked_client, config, logger_mock):
    exception = Exception("Test")
    mocked_client.Account.retrieve = Mock(side_effect=exception)
    assert SourceStripe().check_connection(logger_mock, config=config) == (False, exception)
