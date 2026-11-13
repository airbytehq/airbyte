#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from integration.request_builder import StripeRequestBuilder


# Frozen early in 2010 so the fixed-start accounts cursor yields exactly three 30-day windows.
NOW_2010 = datetime(2010, 3, 15, 12, 0, 0, 123456, tzinfo=timezone.utc)
WINDOW_START = datetime(2010, 1, 1, tzinfo=timezone.utc)
WINDOW = timedelta(days=30)
WINDOW_COUNT = 3


def windows_from(start: datetime) -> List[Tuple[datetime, datetime]]:
    """The 30-day windows the accounts cursor reads from `start` to the 2010 clock, each ending a second before the next."""
    now = NOW_2010.replace(microsecond=0)
    windows = []
    while start < now:
        windows.append((start, min(start + WINDOW - timedelta(seconds=1), now)))
        start += WINDOW
    return windows


def window_bounds(index: int) -> Tuple[datetime, datetime]:
    return windows_from(WINDOW_START)[index]


def created_inside_window(index: int) -> int:
    start, _ = window_bounds(index)
    return int((start + timedelta(days=1)).timestamp())


def request_for_window(accounts_request: StripeRequestBuilder, start: datetime, end: datetime) -> StripeRequestBuilder:
    return accounts_request.with_created_gte(start).with_created_lte(end).with_limit(100)


def window_request(accounts_request: StripeRequestBuilder, index: int) -> StripeRequestBuilder:
    return request_for_window(accounts_request, *window_bounds(index))
