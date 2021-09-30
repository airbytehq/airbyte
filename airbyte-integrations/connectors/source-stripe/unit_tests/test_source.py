#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
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
    inv_stream = Invoices(account_id=213, start_date="2020", lookback_window_days=lookback_window_days)
    inv_stream.cursor_field = "created"
    assert inv_stream.get_start_timestamp({"created": current_state}) == expected, message
