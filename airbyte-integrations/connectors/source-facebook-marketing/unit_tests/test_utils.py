#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta

import freezegun
import pytest
from source_facebook_marketing.utils import DATA_RETENTION_PERIOD, validate_end_date, validate_start_date

from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime


TODAY = AirbyteDateTime(2023, 3, 31)


@pytest.mark.parametrize(
    "field_name, date, expected_date, expected_messages",
    [
        (
            "start_date",
            TODAY - timedelta(days=(DATA_RETENTION_PERIOD - 1) * 30),
            TODAY - timedelta(days=(DATA_RETENTION_PERIOD - 1) * 30),
            [],
        ),
        (
            "start_date",
            AirbyteDateTime(2019, 1, 1),
            AirbyteDateTime(2020, 3, 4),
            [f"The start date cannot be beyond 37 months from the current date. " f"Set start date to {AirbyteDateTime(2020, 3, 4)}."],
        ),
        (
            "start_date",
            TODAY + timedelta(days=30),
            TODAY,
            [f"The start date cannot be in the future. Set start date to today's date - {TODAY}."],
        ),
        (
            "end_date",
            TODAY - timedelta(days=DATA_RETENTION_PERIOD * 30),
            TODAY,
            [f"The end date must be after start date. Set end date to {TODAY}."],
        ),
    ],
)
@freezegun.freeze_time("2023-03-31")
def test_date_validators(caplog, field_name, date, expected_date, expected_messages):
    if field_name == "start_date":
        assert validate_start_date(date) == expected_date
    elif field_name == "end_date":
        assert validate_end_date(expected_date, date) == expected_date
    assert caplog.messages == expected_messages
