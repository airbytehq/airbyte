#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime

import pendulum

logger = logging.getLogger("airbyte")

# Facebook store metrics maximum of 37 months old. Any time range that
# older that 37 months from current date would result in 400 Bad request
# HTTP response.
# https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
DATA_RETENTION_PERIOD = 37


def validate_start_date(start_date: datetime) -> datetime:
    pendulum_date = pendulum.instance(start_date)
    time_zone = start_date.tzinfo
    current_date = pendulum.today(time_zone)
    if pendulum_date.timestamp() > pendulum.now().timestamp():
        message = f"The start date cannot be in the future. Set start date to today's date - {current_date}."
        logger.warning(message)
        return current_date
    elif pendulum_date.timestamp() < current_date.subtract(months=DATA_RETENTION_PERIOD).timestamp():
        current_date = pendulum.today(time_zone)
        message = (
            f"The start date cannot be beyond {DATA_RETENTION_PERIOD} months from the current date. "
            f"Set start date to {current_date.subtract(months=DATA_RETENTION_PERIOD)}."
        )
        logger.warning(message)
        return current_date.subtract(months=DATA_RETENTION_PERIOD)
    return start_date


def validate_end_date(start_date: datetime, end_date: datetime) -> datetime:
    if start_date > end_date:
        message = f"The end date must be after start date. Set end date to {start_date}."
        logger.warning(message)
        return start_date
    return end_date
