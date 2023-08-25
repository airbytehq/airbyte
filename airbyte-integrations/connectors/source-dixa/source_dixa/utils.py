#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta, timezone


def validate_ms_timestamp(ms_timestamp: int) -> int:
    if type(ms_timestamp) != int or len(str(ms_timestamp)) != 13:
        msg = f"Not a millisecond-precision timestamp: {ms_timestamp}"
        raise ValueError(msg)
    return ms_timestamp


def ms_timestamp_to_datetime(ms_timestamp: int) -> datetime:
    """Converts a millisecond-precision timestamp to a datetime object."""
    return datetime.fromtimestamp(validate_ms_timestamp(ms_timestamp) / 1000, tz=timezone.utc)


def datetime_to_ms_timestamp(dt: datetime) -> int:
    """Converts a datetime object to a millisecond-precision timestamp."""
    return int(dt.timestamp() * 1000)


def add_days_to_ms_timestamp(days: int, ms_timestamp: int) -> int:
    return datetime_to_ms_timestamp(ms_timestamp_to_datetime(validate_ms_timestamp(ms_timestamp)) + timedelta(days=days))
