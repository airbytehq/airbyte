import random
import string
from typing import Iterable, Tuple
from datetime import datetime, timedelta


def random_name(n: int) -> str:
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


def split_date_by_chunks(date_from: datetime, date_to: datetime, chunk_size_in_days: int) -> Iterable[Tuple[str, str]]:
    print("split_date_by_chunks,", date_from, date_to)
    cursor = date_from
    delta = timedelta(days=chunk_size_in_days)
    while cursor < date_to:
        if cursor + delta > date_to:
            yield (cursor, date_to)
            break
        yield (cursor, cursor + delta)
        cursor += delta + timedelta(days=1)


def last_n_days_dates(last_n_days: int) -> Tuple[datetime, datetime]:
    yesterday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    return (yesterday - timedelta(days=last_n_days), yesterday)


def yesterday():
    return (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).date()


def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date()
