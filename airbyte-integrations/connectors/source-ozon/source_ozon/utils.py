from __future__ import annotations

from itertools import tee
from typing import Generator, Iterable


def chunks(lst: list | set | tuple, n: int) -> Generator:
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def pairwise(iterable: Iterable) -> Iterable:
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
