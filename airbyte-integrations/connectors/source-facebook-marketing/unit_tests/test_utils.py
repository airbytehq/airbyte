#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from source_facebook_marketing.utils import DATA_RETENTION_PERIOD, validate_end_date, validate_start_date


@pytest.mark.parametrize(
    "field_name, date, expected_date, expected_messages",
    [
        (
            "start_date",
            pendulum.today().subtract(months=DATA_RETENTION_PERIOD - 1),
            pendulum.today().subtract(months=DATA_RETENTION_PERIOD - 1),
            [],
        ),
        (
            "start_date",
            pendulum.today().subtract(months=DATA_RETENTION_PERIOD + 1),
            pendulum.today().subtract(months=DATA_RETENTION_PERIOD),
            [
                f"The start date cannot be beyond 37 months from the current date. "
                f"Set start date to {pendulum.today().subtract(months=DATA_RETENTION_PERIOD)}."
            ],
        ),
        (
            "start_date",
            pendulum.today() + pendulum.duration(months=1),
            pendulum.today(),
            [f"The start date cannot be in the future. Set start date to today's date - {pendulum.today()}."],
        ),
        (
            "end_date",
            pendulum.today().subtract(months=DATA_RETENTION_PERIOD),
            pendulum.today(),
            [f"The end date must be after start date. Set end date to {pendulum.today()}."],
        ),
    ],
)
def test_date_validators(caplog, field_name, date, expected_date, expected_messages):
    if field_name == "start_date":
        assert validate_start_date(date) == expected_date
    elif field_name == "end_date":
        assert validate_end_date(expected_date, date) == expected_date
    assert caplog.messages == expected_messages
