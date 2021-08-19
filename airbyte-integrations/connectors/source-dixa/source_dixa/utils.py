#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from datetime import datetime, timedelta, timezone


def validate_ms_timestamp(ms_timestamp: int) -> int:
    if not type(ms_timestamp) == int or not len(str(ms_timestamp)) == 13:
        raise ValueError(f"Not a millisecond-precision timestamp: {ms_timestamp}")
    return ms_timestamp


def ms_timestamp_to_datetime(ms_timestamp: int) -> datetime:
    """
    Converts a millisecond-precision timestamp to a datetime object.
    """
    return datetime.fromtimestamp(validate_ms_timestamp(ms_timestamp) / 1000, tz=timezone.utc)


def datetime_to_ms_timestamp(dt: datetime) -> int:
    """
    Converts a datetime object to a millisecond-precision timestamp.
    """
    return int(dt.timestamp() * 1000)


def add_days_to_ms_timestamp(days: int, ms_timestamp: int) -> int:
    return datetime_to_ms_timestamp(ms_timestamp_to_datetime(validate_ms_timestamp(ms_timestamp)) + timedelta(days=days))
