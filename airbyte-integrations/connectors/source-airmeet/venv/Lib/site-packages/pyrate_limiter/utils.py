import random
import sqlite3
import string
from pathlib import Path
from tempfile import gettempdir
from typing import List

from .abstracts import Rate
from .abstracts import RateItem


def binary_search(items: List[RateItem], value: int) -> int:
    """Find the index of item in list where left.timestamp < value <= right.timestamp
    this is to determine the current size of some window that
    stretches from now back to  lower-boundary = value and
    """
    if not items:
        return 0

    if value == items[0].timestamp:
        return 0

    if value > items[-1].timestamp:
        return -1

    pivot = int(len(items) / 2)
    left, right = items[pivot - 1], items[pivot]

    if left.timestamp >= value:
        return binary_search(items[:pivot], value)

    if right.timestamp < value:
        return pivot + binary_search(items[pivot:], value)

    return pivot


def validate_rate_list(rates: List[Rate]) -> bool:
    """Raise false if rates are incorrectly ordered."""
    if not rates:
        return False

    for idx, current_rate in enumerate(rates[1:]):
        prev_rate = rates[idx]

        if current_rate.interval <= prev_rate.interval:
            return False

        if current_rate.limit <= prev_rate.limit:
            return False

        if (current_rate.limit / current_rate.interval) > (prev_rate.limit / prev_rate.interval):
            return False

    return True


def id_generator(
    size=6,
    chars=string.ascii_uppercase + string.digits + string.ascii_lowercase,
) -> str:
    return "".join(random.choice(chars) for _ in range(size))


def dedicated_sqlite_clock_connection():
    temp_dir = Path(gettempdir())
    default_db_path = temp_dir / "pyrate_limiter_clock_only.sqlite"

    conn = sqlite3.connect(
        default_db_path,
        isolation_level="EXCLUSIVE",
        check_same_thread=False,
    )
    return conn
