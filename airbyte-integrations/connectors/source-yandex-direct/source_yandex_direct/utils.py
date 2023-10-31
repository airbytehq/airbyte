import random
import string
from typing import Iterable, Tuple
from datetime import datetime, timedelta
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy as _HttpAvailabilityStrategy


class HttpAvailabilityStrategy(_HttpAvailabilityStrategy):
    def check_availability(self, *args, **kwargs):
        return True, None


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


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def find_by_key(data, target):
    """Search for target values in nested dict"""
    for key, value in data.items():
        if isinstance(value, dict):
            yield from find_by_key(value, target)
        elif key == target:
            yield value


def concat_multiple_lists(list_of_lists):
    return sum(list_of_lists, [])


def get_unique(list1):
    return list(set(list1))
