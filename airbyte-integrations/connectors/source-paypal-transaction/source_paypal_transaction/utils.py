#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime


def to_datetime_str(date: datetime) -> datetime:
    """
    Returns the formated datetime string.
    :: Output example: '2021-07-15T0:0:0+00:00' FORMAT : "%Y-%m-%dT%H:%M:%S%z"
    """
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")


def middle_date_slices(stream_slice):
    """Returns the mid-split datetime slices."""
    start_date, end_date = to_datetime_str(stream_slice["start_date"]), to_datetime_str(stream_slice["end_date"])
    if start_date < end_date:
        middle_date = start_date + (end_date - start_date) / 2
        return [
            {
                "start_date": start_date.isoformat(),
                "end_date": middle_date.isoformat(),
            },
            {
                "start_date": middle_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        ]
