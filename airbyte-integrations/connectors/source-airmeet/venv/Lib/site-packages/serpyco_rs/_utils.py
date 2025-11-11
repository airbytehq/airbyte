import re
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from typing import Generic, Optional, Protocol, TypeVar

from attributes_doc import get_attributes_doc as _get_attributes_doc
from typing_extensions import Self


CAMELCASE_RE = re.compile(r'(?!^)_([a-zA-Z])')


def to_camelcase(s: str) -> str:
    return CAMELCASE_RE.sub(lambda m: m.group(1).upper(), s).rstrip('_')


get_attributes_doc = lru_cache(_get_attributes_doc)


_T = TypeVar('_T')


class _Stack(Generic[_T]):
    def __init__(self, init: Optional[_T] = None) -> None:
        self._stack = [init] if init is not None else []

    @contextmanager
    def push(self, val: _T) -> Iterator[None]:
        self._stack.append(val)
        yield
        self._stack.pop()

    def get(self) -> _T:
        return self._stack[-1]


class SupportsMerge(Protocol):
    def merge(self, other: Self) -> Self: ...


_T_Merge = TypeVar('_T_Merge', bound=SupportsMerge)


class _MergeStack(_Stack[_T_Merge]):
    @contextmanager
    def merge(self, other: _T_Merge) -> Iterator[_T_Merge]:
        current = self.get()
        with self.push(current.merge(other)):
            yield self.get()
