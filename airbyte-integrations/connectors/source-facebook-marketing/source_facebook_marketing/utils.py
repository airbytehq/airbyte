#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

import pendulum
from pendulum import DateTime

logger = logging.getLogger("airbyte")

# Facebook store metrics maximum of 37 months old. Any time range that
# older that 37 months from current date would result in 400 Bad request
# HTTP response.
# https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
DATA_RETENTION_PERIOD = 37


def validate_start_date(start_date: DateTime) -> DateTime:
    now = pendulum.now(tz=start_date.tzinfo)
    today = now.replace(microsecond=0, second=0, minute=0, hour=0)
    retention_date = today.subtract(months=DATA_RETENTION_PERIOD)

    if start_date > now:
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


def validate_end_date(start_date: DateTime, end_date: DateTime) -> DateTime:
    if start_date > end_date:
        message = f"The end date must be after start date. Set end date to {start_date}."
        logger.warning(message)
        return start_date
    return end_date
