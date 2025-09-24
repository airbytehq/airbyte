#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import timedelta

from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now


logger = logging.getLogger("airbyte")

# Facebook store metrics maximum of 37 months old. Any time range that
# older than 37 months from current date would result in 400 Bad request
# HTTP response.
# https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
DATA_RETENTION_PERIOD = 37
# Min number of days in 37 months (1123)
INSIGHTS_RETENTION_PERIOD_DAYS = 1123


def validate_start_date(start_date: AirbyteDateTime) -> AirbyteDateTime:
    today = AirbyteDateTime.from_datetime(ab_datetime_now())
    retention_date = today - timedelta(days=INSIGHTS_RETENTION_PERIOD_DAYS)
    # FB does not provide precise description of how we should calculate the 37 months datetime difference.
    # As timezone difference can result in an additional time delta, this is a reassurance we stay inside the 37 months limit.
    retention_date = retention_date + timedelta(days=1)

    if start_date > today:
        message = f"The start date cannot be in the future. Set start date to today's date - {today}."
        logger.warning(message)
        return today
    elif start_date < retention_date:
        message = (
            f"The start date cannot be beyond {DATA_RETENTION_PERIOD} months from the current date. Set start date to {retention_date}."
        )
        logger.warning(message)
        return retention_date
    return start_date


def validate_end_date(start_date: AirbyteDateTime, end_date: AirbyteDateTime) -> AirbyteDateTime:
    if start_date > end_date:
        message = f"The end date must be after start date. Set end date to {start_date}."
        logger.warning(message)
        return start_date
    return end_date
