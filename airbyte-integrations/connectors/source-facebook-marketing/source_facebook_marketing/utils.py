#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Union

import pendulum
from pendulum import Date, DateTime

logger = logging.getLogger("airbyte")

# Facebook store metrics maximum of 37 months old. Any time range that
# older than 37 months from current date would result in 400 Bad request
# HTTP response.
# https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
DATA_RETENTION_PERIOD = 37
DateOrDateTime = Union[Date, DateTime]


def cast_to_type(input_date: DateOrDateTime, target_date: DateOrDateTime) -> DateOrDateTime:
    # casts `target_date` to the type of `input_date`
    if type(target_date) == type(input_date):
        return target_date
    if isinstance(target_date, DateTime):
        return target_date.date()
    return pendulum.datetime(target_date.year, target_date.month, target_date.day)


def validate_start_date(start_date: DateOrDateTime) -> DateOrDateTime:
    today = cast_to_type(start_date, pendulum.today(tz=pendulum.tz.UTC))
    retention_date = today.subtract(months=DATA_RETENTION_PERIOD)
    if retention_date.day != today.day:
        # `.subtract(months=37)` can be erroneous, for instance:
        # 2023-03-31 - 37 month = 2020-02-29 which is incorrect, should be 2020-03-01
        # that's why we're adjusting the date to the 1st day of the next month
        retention_date = retention_date.replace(month=retention_date.month + 1, day=1)

    # FB does not provide precise description of how we should calculate the 37 months datetime difference.
    # As timezone difference can result in an additional time delta, this is a reassurance we stay inside the 37 months limit.
    retention_date = retention_date.add(days=1)

    if start_date > today:
        message = f"The start date cannot be in the future. Set start date to today's date - {today}."
        logger.warning(message)
        return cast_to_type(start_date, today)
    elif start_date < retention_date:
        message = (
            f"The start date cannot be beyond {DATA_RETENTION_PERIOD} months from the current date. Set start date to {retention_date}."
        )
        logger.warning(message)
        return cast_to_type(start_date, retention_date)
    return start_date


def validate_end_date(start_date: DateOrDateTime, end_date: DateOrDateTime) -> DateOrDateTime:
    if start_date > end_date:
        message = f"The end date must be after start date. Set end date to {start_date}."
        logger.warning(message)
        return start_date
    return end_date
