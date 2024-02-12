from __future__ import annotations

from datetime import timedelta, date
from itertools import tee
from typing import Generator, Iterable, List


def chunks(lst: list | set | tuple, n: int) -> Generator:
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def pairwise(iterable: Iterable) -> Iterable:
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def get_dates_between(date_from: date, date_to: date) -> List[str]:
    delta = date_to - date_from
    return [(date_from + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]
