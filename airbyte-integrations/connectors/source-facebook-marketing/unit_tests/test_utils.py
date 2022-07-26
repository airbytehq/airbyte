#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from source_facebook_marketing.utils import DATA_RETENTION_PERIOD, ValidationDateException, validate_date_field


@pytest.mark.parametrize(
    "date, expected_message, raise_error",
    [
        (pendulum.now(), "", False),
        (
            pendulum.now() - pendulum.duration(months=DATA_RETENTION_PERIOD.months + 1),
            f" cannot be beyond {DATA_RETENTION_PERIOD.months} months from the current date.",
            True,
        ),
        (pendulum.now() + pendulum.duration(months=1), " cannot be in the future. Please set today's date or later.", True),
    ],
    ids=["valid_date", f"date in the past by {DATA_RETENTION_PERIOD.months} months", "date in future"],
)
def test_validate_date_field(date, expected_message, raise_error):
    field_name = "test_field_name"

    if raise_error:
        with pytest.raises(ValidationDateException) as error:
            assert validate_date_field(field_name, date)
        assert str(error.value) == field_name + expected_message
    else:
        assert validate_date_field(field_name, date)
