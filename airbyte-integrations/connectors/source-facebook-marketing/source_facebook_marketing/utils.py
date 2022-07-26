#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

import pendulum

# Facebook store metrics maximum of 37 months old. Any time range that
# older that 37 months from current date would result in 400 Bad request
# HTTP response.
# https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
DATA_RETENTION_PERIOD = pendulum.duration(months=37)


class ValidationDateException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super().__init__(self.message, *args, **kwargs)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.__str__()


def validate_date_field(field_name: str, date: datetime) -> datetime:
    pendulum_date = pendulum.instance(date)
    if pendulum_date.timestamp() > pendulum.now().timestamp():
        message = f"{field_name} cannot be in the future. Please set today's date or later."
        raise ValidationDateException(message)
    elif pendulum_date.timestamp() < (pendulum.now() - DATA_RETENTION_PERIOD).timestamp():
        message = f"{field_name} cannot be beyond {DATA_RETENTION_PERIOD.months} months from the current date."
        raise ValidationDateException(message)
    return date
