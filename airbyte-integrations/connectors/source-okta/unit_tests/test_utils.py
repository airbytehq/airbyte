#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from source_okta.utils import get_start_date


@pytest.mark.parametrize(
    "config, expected_date, expected_messages",
    [
        (
            {"start_date": "2022-07-22T00:00:00Z"},
            pendulum.parse("2022-07-22T00:00:00Z"),
            [],
        ),
        (
            {"start_date": "3033-07-22T00:00:00Z"},
            pendulum.now().subtract(days=7).replace(microsecond=0),
            ["The start date cannot be in the future. Set the start date to default 7 days prior current date."],
        ),
        (
            {},
            pendulum.now().subtract(days=7).replace(microsecond=0),
            ["Set the start date to default 7 days prior current date."],
        ),
    ],
)
def test_get_start_date(caplog, config, expected_date, expected_messages):
    assert get_start_date(config).date() == expected_date.date()
    assert caplog.messages == expected_messages
