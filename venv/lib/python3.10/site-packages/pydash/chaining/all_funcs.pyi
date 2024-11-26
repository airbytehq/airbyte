# mypy: disable-error-code=misc
"""Generated from the `scripts/chaining_type_generator.py` script."""

import re
import typing as t

from _typeshed import (
    SupportsAdd,
    SupportsDunderGE,
    SupportsDunderGT,
    SupportsDunderLE,
    SupportsDunderLT,
    SupportsRichComparison,
    SupportsRichComparisonT,
    SupportsSub,
)
from typing_extensions import Concatenate, Literal, ParamSpec, Type

import pydash as pyd
from pydash.chaining.chaining import Chain
from pydash.functions import (
    After,
    Ary,
    Before,
    CurryFive,
    CurryFour,
    CurryOne,
    CurryRightFive,
    CurryRightFour,
    CurryRightOne,
    CurryRightThree,
    CurryRightTwo,
    CurryThree,
    CurryTwo,
    Debounce,
    Disjoin,
    Flow,
    Iterated,
    Juxtapose,
    Negate,
    Once,
    Partial,
    Rearg,
    Spread,
    Throttle,
)
from pydash.helpers import UNSET, Unset
from pydash.types import *
from pydash.utilities import MemoizedFunc

Value_coT = t.TypeVar("Value_coT", covariant=True)
T = t.TypeVar("T")
T1 = t.TypeVar("T1")
T2 = t.TypeVar("T2")
T3 = t.TypeVar("T3")
T4 = t.TypeVar("T4")
T5 = t.TypeVar("T5")
NumT = t.TypeVar("NumT", int, float, "Decimal")
NumT2 = t.TypeVar("NumT2", int, float, "Decimal")
NumT3 = t.TypeVar("NumT3", int, float, "Decimal")
CallableT = t.TypeVar("CallableT", bound=t.Callable)
SequenceT = t.TypeVar("SequenceT", bound=t.Sequence)
MutableSequenceT = t.TypeVar("MutableSequenceT", bound=t.MutableSequence)
P = ParamSpec("P")

class AllFuncs:
    def chunk(self: "Chain[t.Sequence[T]]", size: int = 1) -> "Chain[t.List[t.Sequence[T]]]":
        return self._wrap(pyd.chunk)(size)
    def compact(self: "Chain[t.Iterable[t.Union[T, None]]]") -> "Chain[t.List[T]]":
        return self._wrap(pyd.compact)()
    def concat(self: "Chain[t.Iterable[T]]", *arrays: t.Iterable[T]) -> "Chain[t.List[T]]":
        return self._wrap(pyd.concat)(*arrays)
    def difference(self: "Chain[t.Iterable[T]]", *others: t.Iterable[T]) -> "Chain[t.List[T]]":
        return self._wrap(pyd.difference)(*others)
    @t.overload
    def difference_by(
        self: "Chain[t.Iterable[T]]",
        *others: t.Iterable[T],
        iteratee: t.Union[IterateeObjT, t.Callable[[T], t.Any], None]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def difference_by(
        self: "Chain[t.Iterable[T]]",
        *others: t.Union[IterateeObjT, t.Iterable[T], t.Callable[[T], t.Any]]
    ) -> "Chain[t.List[T]]": ...
    def difference_by(self, *others, **kwargs):
        return self._wrap(pyd.difference_by)(*others, **kwargs)
    @t.overload
    def difference_with(
        self: "Chain[t.Iterable[T]]",
        *others: t.Iterable[T2],
        comparator: t.Union[t.Callable[[T, T2], t.Any], None]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def difference_with(
        self: "Chain[t.Iterable[T]]", *others: t.Union[t.Iterable[T2], t.Callable[[T, T2], t.Any]]
    ) -> "Chain[t.List[T]]": ...
    def difference_with(self, *others, **kwargs):
        return self._wrap(pyd.difference_with)(*others, **kwargs)
    def drop(self: "Chain[t.Sequence[T]]", n: int = 1) -> "Chain[t.List[T]]":
        return self._wrap(pyd.drop)(n)
    def drop_right(self: "Chain[t.Sequence[T]]", n: int = 1) -> "Chain[t.List[T]]":
        return self._wrap(pyd.drop_right)(n)
    @t.overload
    def drop_right_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def drop_right_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def drop_right_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def drop_right_while(
        self: "Chain[t.Sequence[T]]", predicate: None = None
    ) -> "Chain[t.List[T]]": ...
    def drop_right_while(self, predicate=None):
        return self._wrap(pyd.drop_right_while)(predicate)
    @t.overload
    def drop_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def drop_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def drop_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def drop_while(self: "Chain[t.Sequence[T]]", predicate: None = None) -> "Chain[t.List[T]]": ...
    def drop_while(self, predicate=None):
        return self._wrap(pyd.drop_while)(predicate)
    def duplicates(
        self: "Chain[t.Sequence[T]]",
        iteratee: t.Union[t.Callable[[T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]":
        return self._wrap(pyd.duplicates)(iteratee)
    def fill(
        self: "Chain[t.Sequence[T]]", value: T2, start: int = 0, end: t.Union[int, None] = None
    ) -> "Chain[t.List[t.Union[T, T2]]]":
        return self._wrap(pyd.fill)(value, start, end)
    @t.overload
    def find_index(
        self: "Chain[t.Iterable[T]]", predicate: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[int]": ...
    @t.overload
    def find_index(
        self: "Chain[t.Iterable[T]]", predicate: t.Callable[[T, int], t.Any]
    ) -> "Chain[int]": ...
    @t.overload
    def find_index(
        self: "Chain[t.Iterable[T]]", predicate: t.Callable[[T], t.Any]
    ) -> "Chain[int]": ...
    @t.overload
    def find_index(self: "Chain[t.Iterable[t.Any]]", predicate: IterateeObjT) -> "Chain[int]": ...
    @t.overload
    def find_index(self: "Chain[t.Iterable[t.Any]]", predicate: None = None) -> "Chain[int]": ...
    def find_index(self, predicate=None):
        return self._wrap(pyd.find_index)(predicate)
    @t.overload
    def find_last_index(
        self: "Chain[t.Iterable[T]]", predicate: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[int]": ...
    @t.overload
    def find_last_index(
        self: "Chain[t.Iterable[T]]", predicate: t.Callable[[T, int], t.Any]
    ) -> "Chain[int]": ...
    @t.overload
    def find_last_index(
        self: "Chain[t.Iterable[T]]", predicate: t.Callable[[T], t.Any]
    ) -> "Chain[int]": ...
    @t.overload
    def find_last_index(
        self: "Chain[t.Iterable[t.Any]]", predicate: IterateeObjT
    ) -> "Chain[int]": ...
    @t.overload
    def find_last_index(
        self: "Chain[t.Iterable[t.Any]]", predicate: None = None
    ) -> "Chain[int]": ...
    def find_last_index(self, predicate=None):
        return self._wrap(pyd.find_last_index)(predicate)
    @t.overload
    def flatten(self: "Chain[t.Iterable[t.Iterable[T]]]") -> "Chain[t.List[T]]": ...
    @t.overload
    def flatten(self: "Chain[t.Iterable[T]]") -> "Chain[t.List[T]]": ...
    def flatten(self):
        return self._wrap(pyd.flatten)()
    def flatten_deep(self: "Chain[t.Iterable]") -> "Chain[t.List]":
        return self._wrap(pyd.flatten_deep)()
    def flatten_depth(self: "Chain[t.Iterable]", depth: int = 1) -> "Chain[t.List]":
        return self._wrap(pyd.flatten_depth)(depth)
    @t.overload
    def from_pairs(self: "Chain[t.Iterable[t.Tuple[T, T2]]]") -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def from_pairs(
        self: "Chain[t.Iterable[t.List[t.Union[T, T2]]]]",
    ) -> "Chain[t.Dict[t.Union[T, T2], t.Union[T, T2]]]": ...
    def from_pairs(self):
        return self._wrap(pyd.from_pairs)()
    def head(self: "Chain[t.Sequence[T]]") -> "Chain[t.Union[T, None]]":
        return self._wrap(pyd.head)()
    def index_of(self: "Chain[t.Sequence[T]]", value: T, from_index: int = 0) -> "Chain[int]":
        return self._wrap(pyd.index_of)(value, from_index)
    def initial(self: "Chain[t.Sequence[T]]") -> "Chain[t.Sequence[T]]":
        return self._wrap(pyd.initial)()
    @t.overload
    def intercalate(
        self: "Chain[t.Iterable[t.Iterable[T]]]", separator: T2
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    @t.overload
    def intercalate(
        self: "Chain[t.Iterable[T]]", separator: T2
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    def intercalate(self, separator):
        return self._wrap(pyd.intercalate)(separator)
    def interleave(self: "Chain[t.Iterable[T]]", *arrays: t.Iterable[T]) -> "Chain[t.List[T]]":
        return self._wrap(pyd.interleave)(*arrays)
    def intersection(
        self: "Chain[t.Sequence[T]]", *others: t.Iterable[t.Any]
    ) -> "Chain[t.List[T]]":
        return self._wrap(pyd.intersection)(*others)
    @t.overload
    def intersection_by(
        self: "Chain[t.Sequence[T]]",
        *others: t.Iterable[t.Any],
        iteratee: t.Union[t.Callable[[T], t.Any], IterateeObjT]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def intersection_by(
        self: "Chain[t.Sequence[T]]",
        *others: t.Union[t.Iterable[t.Any], t.Callable[[T], t.Any], IterateeObjT]
    ) -> "Chain[t.List[T]]": ...
    def intersection_by(self, *others, **kwargs):
        return self._wrap(pyd.intersection_by)(*others, **kwargs)
    @t.overload
    def intersection_with(
        self: "Chain[t.Sequence[T]]",
        *others: t.Iterable[T2],
        comparator: t.Callable[[T, T2], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def intersection_with(
        self: "Chain[t.Sequence[T]]", *others: t.Union[t.Iterable[T2], t.Callable[[T, T2], t.Any]]
    ) -> "Chain[t.List[T]]": ...
    def intersection_with(self, *others, **kwargs):
        return self._wrap(pyd.intersection_with)(*others, **kwargs)
    def intersperse(self: "Chain[t.Iterable[T]]", separator: T2) -> "Chain[t.List[t.Union[T, T2]]]":
        return self._wrap(pyd.intersperse)(separator)
    def last(self: "Chain[t.Sequence[T]]") -> "Chain[t.Union[T, None]]":
        return self._wrap(pyd.last)()
    def last_index_of(
        self: "Chain[t.Sequence[t.Any]]", value: t.Any, from_index: t.Union[int, None] = None
    ) -> "Chain[int]":
        return self._wrap(pyd.last_index_of)(value, from_index)
    @t.overload
    def mapcat(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T, int, t.List[T]], t.Union[t.List[T2], t.List[t.List[T2]]]],
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def mapcat(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], T2]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def mapcat(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T, int], t.Union[t.List[T2], t.List[t.List[T2]]]],
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def mapcat(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], T2]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def mapcat(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T], t.Union[t.List[T2], t.List[t.List[T2]]]],
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def mapcat(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], T2]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def mapcat(
        self: "Chain[t.Iterable[t.Union[t.List[T], t.List[t.List[T]]]]]", iteratee: None = None
    ) -> "Chain[t.List[t.Union[T, t.List[T]]]]": ...
    def mapcat(self, iteratee=None):
        return self._wrap(pyd.mapcat)(iteratee)
    def nth(self: "Chain[t.Iterable[T]]", pos: int = 0) -> "Chain[t.Union[T, None]]":
        return self._wrap(pyd.nth)(pos)
    def pop(self: "Chain[t.List[T]]", index: int = -1) -> "Chain[T]":
        return self._wrap(pyd.pop)(index)
    def pull(self: "Chain[t.List[T]]", *values: T) -> "Chain[t.List[T]]":
        return self._wrap(pyd.pull)(*values)
    def pull_all(self: "Chain[t.List[T]]", values: t.Iterable[T]) -> "Chain[t.List[T]]":
        return self._wrap(pyd.pull_all)(values)
    def pull_all_by(
        self: "Chain[t.List[T]]",
        values: t.Iterable[T],
        iteratee: t.Union[IterateeObjT, t.Callable[[T], t.Any], None] = None,
    ) -> "Chain[t.List[T]]":
        return self._wrap(pyd.pull_all_by)(values, iteratee)
    def pull_all_with(
        self: "Chain[t.List[T]]",
        values: t.Iterable[T],
        comparator: t.Union[t.Callable[[T, T], t.Any], None] = None,
    ) -> "Chain[t.List[T]]":
        return self._wrap(pyd.pull_all_with)(values, comparator)
    def pull_at(self: "Chain[t.List[T]]", *indexes: int) -> "Chain[t.List[T]]":
        return self._wrap(pyd.pull_at)(*indexes)
    def push(self: "Chain[t.List[T]]", *items: T2) -> "Chain[t.List[t.Union[T, T2]]]":
        return self._wrap(pyd.push)(*items)
    def remove(
        self: "Chain[t.List[T]]",
        predicate: t.Union[
            t.Callable[[T, int, t.List[T]], t.Any],
            t.Callable[[T, int], t.Any],
            t.Callable[[T], t.Any],
            None,
        ] = None,
    ) -> "Chain[t.List[T]]":
        return self._wrap(pyd.remove)(predicate)
    def reverse(self: "Chain[SequenceT]") -> "Chain[SequenceT]":
        return self._wrap(pyd.reverse)()
    def shift(self: "Chain[t.List[T]]") -> "Chain[T]":
        return self._wrap(pyd.shift)()
    def slice_(
        self: "Chain[SequenceT]", start: int = 0, end: t.Union[int, None] = None
    ) -> "Chain[SequenceT]":
        return self._wrap(pyd.slice_)(start, end)
    slice = slice_

    @t.overload
    def sort(
        self: "Chain[t.List['SupportsRichComparisonT']]",
        comparator: None = None,
        key: None = None,
        reverse: bool = False,
    ) -> "Chain[t.List['SupportsRichComparisonT']]": ...
    @t.overload
    def sort(
        self: "Chain[t.List[T]]", comparator: t.Callable[[T, T], int], *, reverse: bool = False
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def sort(
        self: "Chain[t.List[T]]",
        *,
        key: t.Callable[[T], "SupportsRichComparisonT"],
        reverse: bool = False
    ) -> "Chain[t.List[T]]": ...
    def sort(self, comparator=None, key=None, reverse=False):
        return self._wrap(pyd.sort)(comparator, key, reverse)
    def sorted_index(
        self: "Chain[t.Sequence['SupportsRichComparisonT']]", value: "SupportsRichComparisonT"
    ) -> "Chain[int]":
        return self._wrap(pyd.sorted_index)(value)
    @t.overload
    def sorted_index_by(
        self: "Chain[t.Sequence[T]]",
        value: T,
        iteratee: t.Union[IterateeObjT, t.Callable[[T], "SupportsRichComparisonT"]],
    ) -> "Chain[int]": ...
    @t.overload
    def sorted_index_by(
        self: "Chain[t.Sequence['SupportsRichComparisonT']]",
        value: "SupportsRichComparisonT",
        iteratee: None = None,
    ) -> "Chain[int]": ...
    def sorted_index_by(self, value, iteratee=None):
        return self._wrap(pyd.sorted_index_by)(value, iteratee)
    def sorted_index_of(
        self: "Chain[t.Sequence['SupportsRichComparisonT']]", value: "SupportsRichComparisonT"
    ) -> "Chain[int]":
        return self._wrap(pyd.sorted_index_of)(value)
    def sorted_last_index(
        self: "Chain[t.Sequence['SupportsRichComparisonT']]", value: "SupportsRichComparisonT"
    ) -> "Chain[int]":
        return self._wrap(pyd.sorted_last_index)(value)
    @t.overload
    def sorted_last_index_by(
        self: "Chain[t.Sequence[T]]",
        value: T,
        iteratee: t.Union[IterateeObjT, t.Callable[[T], "SupportsRichComparisonT"]],
    ) -> "Chain[int]": ...
    @t.overload
    def sorted_last_index_by(
        self: "Chain[t.Sequence['SupportsRichComparisonT']]",
        value: "SupportsRichComparisonT",
        iteratee: None = None,
    ) -> "Chain[int]": ...
    def sorted_last_index_by(self, value, iteratee=None):
        return self._wrap(pyd.sorted_last_index_by)(value, iteratee)
    def sorted_last_index_of(
        self: "Chain[t.Sequence['SupportsRichComparisonT']]", value: "SupportsRichComparisonT"
    ) -> "Chain[int]":
        return self._wrap(pyd.sorted_last_index_of)(value)
    def sorted_uniq(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]",
    ) -> "Chain[t.List['SupportsRichComparisonT']]":
        return self._wrap(pyd.sorted_uniq)()
    def sorted_uniq_by(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]",
        iteratee: t.Union[
            t.Callable[["SupportsRichComparisonT"], "SupportsRichComparisonT"], None
        ] = None,
    ) -> "Chain[t.List['SupportsRichComparisonT']]":
        return self._wrap(pyd.sorted_uniq_by)(iteratee)
    def splice(
        self: "Chain[MutableSequenceT]", start: int, count: t.Union[int, None] = None, *items: t.Any
    ) -> "Chain[MutableSequenceT]":
        return self._wrap(pyd.splice)(start, count, *items)
    def split_at(self: "Chain[t.Sequence[T]]", index: int) -> "Chain[t.List[t.Sequence[T]]]":
        return self._wrap(pyd.split_at)(index)
    def tail(self: "Chain[t.Sequence[T]]") -> "Chain[t.Sequence[T]]":
        return self._wrap(pyd.tail)()
    def take(self: "Chain[t.Sequence[T]]", n: int = 1) -> "Chain[t.Sequence[T]]":
        return self._wrap(pyd.take)(n)
    def take_right(self: "Chain[t.Sequence[T]]", n: int = 1) -> "Chain[t.Sequence[T]]":
        return self._wrap(pyd.take_right)(n)
    @t.overload
    def take_right_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[t.Sequence[T]]": ...
    @t.overload
    def take_right_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.Sequence[T]]": ...
    @t.overload
    def take_right_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T], t.Any]
    ) -> "Chain[t.Sequence[T]]": ...
    @t.overload
    def take_right_while(
        self: "Chain[t.Sequence[T]]", predicate: None = None
    ) -> "Chain[t.Sequence[T]]": ...
    def take_right_while(self, predicate=None):
        return self._wrap(pyd.take_right_while)(predicate)
    @t.overload
    def take_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def take_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def take_while(
        self: "Chain[t.Sequence[T]]", predicate: t.Callable[[T], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def take_while(self: "Chain[t.Sequence[T]]", predicate: None = None) -> "Chain[t.List[T]]": ...
    def take_while(self, predicate=None):
        return self._wrap(pyd.take_while)(predicate)
    @t.overload
    def union(self: "Chain[t.Sequence[T]]") -> "Chain[t.List[T]]": ...
    @t.overload
    def union(
        self: "Chain[t.Sequence[T]]", *others: t.Sequence[T2]
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    def union(self, *others):
        return self._wrap(pyd.union)(*others)
    @t.overload
    def union_by(
        self: "Chain[t.Sequence[T]]", *others: t.Iterable[T], iteratee: t.Callable[[T], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def union_by(
        self: "Chain[t.Sequence[T]]", *others: t.Union[t.Iterable[T], t.Callable[[T], t.Any]]
    ) -> "Chain[t.List[T]]": ...
    def union_by(self, *others, **kwargs):
        return self._wrap(pyd.union_by)(*others, **kwargs)
    @t.overload
    def union_with(
        self: "Chain[t.Sequence[T]]",
        *others: t.Iterable[T2],
        comparator: t.Callable[[T, T2], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def union_with(
        self: "Chain[t.Sequence[T]]", *others: t.Union[t.Iterable[T2], t.Callable[[T, T2], t.Any]]
    ) -> "Chain[t.List[T]]": ...
    def union_with(self, *others, **kwargs):
        return self._wrap(pyd.union_with)(*others, **kwargs)
    def uniq(self: "Chain[t.Iterable[T]]") -> "Chain[t.List[T]]":
        return self._wrap(pyd.uniq)()
    def uniq_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Union[t.Callable[[T], t.Any], None] = None
    ) -> "Chain[t.List[T]]":
        return self._wrap(pyd.uniq_by)(iteratee)
    def uniq_with(
        self: "Chain[t.Sequence[T]]", comparator: t.Union[t.Callable[[T, T], t.Any], None] = None
    ) -> "Chain[t.List[T]]":
        return self._wrap(pyd.uniq_with)(comparator)
    def unshift(self: "Chain[t.List[T]]", *items: T2) -> "Chain[t.List[t.Union[T, T2]]]":
        return self._wrap(pyd.unshift)(*items)
    def unzip(self: "Chain[t.Iterable[t.Iterable[T]]]") -> "Chain[t.List[t.List[T]]]":
        return self._wrap(pyd.unzip)()
    @t.overload
    def unzip_with(
        self: "Chain[t.Iterable[t.Iterable[T]]]",
        iteratee: t.Union[
            t.Callable[[T, T, int, t.List[T]], T2],
            t.Callable[[T, T, int], T2],
            t.Callable[[T, T], T2],
            t.Callable[[T], T2],
        ],
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def unzip_with(
        self: "Chain[t.Iterable[t.Iterable[T]]]", iteratee: None = None
    ) -> "Chain[t.List[t.List[T]]]": ...
    def unzip_with(self, iteratee=None):
        return self._wrap(pyd.unzip_with)(iteratee)
    def without(self: "Chain[t.Iterable[T]]", *values: T) -> "Chain[t.List[T]]":
        return self._wrap(pyd.without)(*values)
    def xor(self: "Chain[t.Iterable[T]]", *lists: t.Iterable[T]) -> "Chain[t.List[T]]":
        return self._wrap(pyd.xor)(*lists)
    @t.overload
    def xor_by(
        self: "Chain[t.Iterable[T]]",
        *lists: t.Iterable[T],
        iteratee: t.Union[t.Callable[[T], t.Any], IterateeObjT]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def xor_by(
        self: "Chain[t.Iterable[T]]", *lists: t.Union[t.Iterable[T], t.Callable[[T], t.Any]]
    ) -> "Chain[t.List[T]]": ...
    def xor_by(self, *lists, **kwargs):
        return self._wrap(pyd.xor_by)(*lists, **kwargs)
    @t.overload
    def xor_with(
        self: "Chain[t.Sequence[T]]", *lists: t.Iterable[T2], comparator: t.Callable[[T, T2], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def xor_with(
        self: "Chain[t.Sequence[T]]", *lists: t.Union[t.Iterable[T2], t.Callable[[T, T2], t.Any]]
    ) -> "Chain[t.List[T]]": ...
    def xor_with(self, *lists, **kwargs):
        return self._wrap(pyd.xor_with)(*lists, **kwargs)
    def zip_(self: "Chain[t.Iterable[T]]", *arrays: t.Iterable[T]) -> "Chain[t.List[t.List[T]]]":
        return self._wrap(pyd.zip_)(*arrays)
    zip = zip_

    @t.overload
    def zip_object(
        self: "Chain[t.Iterable[t.Tuple[T, T2]]]", values: None = None
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def zip_object(
        self: "Chain[t.Iterable[t.List[t.Union[T, T2]]]]", values: None = None
    ) -> "Chain[t.Dict[t.Union[T, T2], t.Union[T, T2]]]": ...
    @t.overload
    def zip_object(self: "Chain[t.Iterable[T]]", values: t.List[T2]) -> "Chain[t.Dict[T, T2]]": ...
    def zip_object(self, values=None):
        return self._wrap(pyd.zip_object)(values)
    def zip_object_deep(
        self: "Chain[t.Iterable[t.Any]]", values: t.Union[t.List[t.Any], None] = None
    ) -> "Chain[t.Dict]":
        return self._wrap(pyd.zip_object_deep)(values)
    @t.overload
    def zip_with(
        self: "Chain[t.Iterable[T]]",
        *arrays: t.Iterable[T],
        iteratee: t.Union[
            t.Callable[[T, T, int, t.List[T]], T2],
            t.Callable[[T, T, int], T2],
            t.Callable[[T, T], T2],
            t.Callable[[T], T2],
        ]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def zip_with(
        self: "Chain[t.Iterable[T]]", *arrays: t.Iterable[T]
    ) -> "Chain[t.List[t.List[T]]]": ...
    @t.overload
    def zip_with(
        self: "Chain[t.Union[t.Iterable[T], t.Callable[[T, T, int, t.List[T]], T2], t.Callable[[T, T, int], T2], t.Callable[[T, T], T2], t.Callable[[T], T2]]]",
        *arrays: t.Union[
            t.Iterable[T],
            t.Callable[[T, T, int, t.List[T]], T2],
            t.Callable[[T, T, int], T2],
            t.Callable[[T, T], T2],
            t.Callable[[T], T2],
        ]
    ) -> "Chain[t.List[t.Union[t.List[T], T2]]]": ...
    def zip_with(self, *arrays, **kwargs):
        return self._wrap(pyd.zip_with)(*arrays, **kwargs)
    def tap(self: "Chain[T]", interceptor: t.Callable[[T], t.Any]) -> "Chain[T]":
        return self._wrap(pyd.tap)(interceptor)
    def thru(self: "Chain[T]", interceptor: t.Callable[[T], T2]) -> "Chain[T2]":
        return self._wrap(pyd.thru)(interceptor)
    @t.overload
    def at(self: "Chain[t.Mapping[T, T2]]", *paths: T) -> "Chain[t.List[t.Union[T2, None]]]": ...
    @t.overload
    def at(
        self: "Chain[t.Mapping[T, t.Any]]", *paths: t.Union[T, t.Iterable[T]]
    ) -> "Chain[t.List[t.Any]]": ...
    @t.overload
    def at(self: "Chain[t.Iterable[T]]", *paths: int) -> "Chain[t.List[t.Union[T, None]]]": ...
    @t.overload
    def at(
        self: "Chain[t.Iterable[t.Any]]", *paths: t.Union[int, t.Iterable[int]]
    ) -> "Chain[t.List[t.Any]]": ...
    def at(self, *paths):
        return self._wrap(pyd.at)(*paths)
    @t.overload
    def count_by(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: None = None
    ) -> "Chain[t.Dict[T2, int]]": ...
    @t.overload
    def count_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T, t.Dict[T, T2]], T3]
    ) -> "Chain[t.Dict[T3, int]]": ...
    @t.overload
    def count_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], T3]
    ) -> "Chain[t.Dict[T3, int]]": ...
    @t.overload
    def count_by(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T2], T3]
    ) -> "Chain[t.Dict[T3, int]]": ...
    @t.overload
    def count_by(
        self: "Chain[t.Iterable[T]]", iteratee: None = None
    ) -> "Chain[t.Dict[T, int]]": ...
    @t.overload
    def count_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], T2]
    ) -> "Chain[t.Dict[T2, int]]": ...
    @t.overload
    def count_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], T2]
    ) -> "Chain[t.Dict[T2, int]]": ...
    @t.overload
    def count_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], T2]
    ) -> "Chain[t.Dict[T2, int]]": ...
    def count_by(self, iteratee=None):
        return self._wrap(pyd.count_by)(iteratee)
    def every(
        self: "Chain[t.Iterable[T]]",
        predicate: t.Union[t.Callable[[T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[bool]":
        return self._wrap(pyd.every)(predicate)
    @t.overload
    def filter_(
        self: "Chain[t.Mapping[T, T2]]",
        predicate: t.Union[t.Callable[[T2, T, t.Dict[T, T2]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def filter_(
        self: "Chain[t.Mapping[T, T2]]",
        predicate: t.Union[t.Callable[[T2, T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def filter_(
        self: "Chain[t.Mapping[t.Any, T2]]",
        predicate: t.Union[t.Callable[[T2], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def filter_(
        self: "Chain[t.Iterable[T]]",
        predicate: t.Union[t.Callable[[T, int, t.List[T]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def filter_(
        self: "Chain[t.Iterable[T]]",
        predicate: t.Union[t.Callable[[T, int], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def filter_(
        self: "Chain[t.Iterable[T]]",
        predicate: t.Union[t.Callable[[T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]": ...
    def filter_(self, predicate=None):
        return self._wrap(pyd.filter_)(predicate)
    filter = filter_

    @t.overload
    def find(
        self: "Chain[t.Dict[T, T2]]",
        predicate: t.Union[t.Callable[[T2, T, t.Dict[T, T2]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T2, None]]": ...
    @t.overload
    def find(
        self: "Chain[t.Dict[T, T2]]",
        predicate: t.Union[t.Callable[[T2, T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T2, None]]": ...
    @t.overload
    def find(
        self: "Chain[t.Dict[T, T2]]",
        predicate: t.Union[t.Callable[[T2], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T2, None]]": ...
    @t.overload
    def find(
        self: "Chain[t.List[T]]",
        predicate: t.Union[t.Callable[[T, int, t.List[T]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find(
        self: "Chain[t.List[T]]",
        predicate: t.Union[t.Callable[[T, int], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find(
        self: "Chain[t.List[T]]",
        predicate: t.Union[t.Callable[[T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T, None]]": ...
    def find(self, predicate=None):
        return self._wrap(pyd.find)(predicate)
    @t.overload
    def find_last(
        self: "Chain[t.Dict[T, T2]]",
        predicate: t.Union[t.Callable[[T2, T, t.Dict[T, T2]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T2, None]]": ...
    @t.overload
    def find_last(
        self: "Chain[t.Dict[T, T2]]",
        predicate: t.Union[t.Callable[[T2, T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T2, None]]": ...
    @t.overload
    def find_last(
        self: "Chain[t.Dict[t.Any, T2]]",
        predicate: t.Union[t.Callable[[T2], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T2, None]]": ...
    @t.overload
    def find_last(
        self: "Chain[t.List[T]]",
        predicate: t.Union[t.Callable[[T, int, t.List[T]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_last(
        self: "Chain[t.List[T]]",
        predicate: t.Union[t.Callable[[T, int], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_last(
        self: "Chain[t.List[T]]",
        predicate: t.Union[t.Callable[[T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Union[T, None]]": ...
    def find_last(self, predicate=None):
        return self._wrap(pyd.find_last)(predicate)
    @t.overload
    def flat_map(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Callable[[T2, T, t.Dict[T, T2]], t.Iterable[T3]],
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], t.Iterable[T3]]
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T2], t.Iterable[T3]]
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T, t.Dict[T, T2]], T3]
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], T3]
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T2], T3]
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Mapping[t.Any, t.Iterable[T2]]]", iteratee: None = None
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: None = None
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], t.Iterable[T2]]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], t.Iterable[T2]]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], t.Iterable[T2]]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], T2]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], T2]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], T2]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def flat_map(
        self: "Chain[t.Iterable[t.Iterable[T]]]", iteratee: None = None
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def flat_map(self: "Chain[t.Iterable[T]]", iteratee: None = None) -> "Chain[t.List[T]]": ...
    def flat_map(self, iteratee=None):
        return self._wrap(pyd.flat_map)(iteratee)
    @t.overload
    def flat_map_deep(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Union[t.Callable[[T2, T, t.Dict[T, T2]], t.Any], None] = None,
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_deep(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Union[t.Callable[[T2, T], t.Any], None] = None
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_deep(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Union[t.Callable[[T2], t.Any], None] = None
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_deep(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Union[t.Callable[[T, int, t.List[T]], t.Any], None] = None,
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_deep(
        self: "Chain[t.Iterable[T]]", iteratee: t.Union[t.Callable[[T, int], t.Any], None] = None
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_deep(
        self: "Chain[t.Iterable[T]]", iteratee: t.Union[t.Callable[[T], t.Any], None] = None
    ) -> "Chain[t.List]": ...
    def flat_map_deep(self: "Chain[t.Iterable]", iteratee=None):
        return self._wrap(pyd.flat_map_deep)(iteratee)
    @t.overload
    def flat_map_depth(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Union[t.Callable[[T2, T, t.Dict[T, T2]], t.Any], None] = None,
        depth: int = 1,
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_depth(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Union[t.Callable[[T2, T], t.Any], None] = None,
        depth: int = 1,
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_depth(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Union[t.Callable[[T2], t.Any], None] = None,
        depth: int = 1,
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_depth(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Union[t.Callable[[T, int, t.List[T]], t.Any], None] = None,
        depth: int = 1,
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_depth(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Union[t.Callable[[T, int], t.Any], None] = None,
        depth: int = 1,
    ) -> "Chain[t.List]": ...
    @t.overload
    def flat_map_depth(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Union[t.Callable[[T], t.Any], None] = None,
        depth: int = 1,
    ) -> "Chain[t.List]": ...
    def flat_map_depth(self, iteratee=None, depth=1):
        return self._wrap(pyd.flat_map_depth)(iteratee, depth)
    @t.overload
    def for_each(
        self: "Chain[t.Dict[T, T2]]",
        iteratee: t.Union[t.Callable[[T2, T, t.Dict[T, T2]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_each(
        self: "Chain[t.Dict[T, T2]]",
        iteratee: t.Union[t.Callable[[T2, T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_each(
        self: "Chain[t.Dict[T, T2]]",
        iteratee: t.Union[t.Callable[[T2], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_each(
        self: "Chain[t.List[T]]",
        iteratee: t.Union[t.Callable[[T, int, t.List[T]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_each(
        self: "Chain[t.List[T]]",
        iteratee: t.Union[t.Callable[[T, int], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_each(
        self: "Chain[t.List[T]]",
        iteratee: t.Union[t.Callable[[T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]": ...
    def for_each(self, iteratee=None):
        return self._wrap(pyd.for_each)(iteratee)
    @t.overload
    def for_each_right(
        self: "Chain[t.Dict[T, T2]]",
        iteratee: t.Union[t.Callable[[T2, T, t.Dict[T, T2]], t.Any], IterateeObjT],
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_each_right(
        self: "Chain[t.Dict[T, T2]]", iteratee: t.Union[t.Callable[[T2, T], t.Any], IterateeObjT]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_each_right(
        self: "Chain[t.Dict[T, T2]]", iteratee: t.Union[t.Callable[[T2], t.Any], IterateeObjT]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_each_right(
        self: "Chain[t.List[T]]",
        iteratee: t.Union[t.Callable[[T, int, t.List[T]], t.Any], IterateeObjT],
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_each_right(
        self: "Chain[t.List[T]]", iteratee: t.Union[t.Callable[[T, int], t.Any], IterateeObjT]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_each_right(
        self: "Chain[t.List[T]]", iteratee: t.Union[t.Callable[[T], t.Any], IterateeObjT]
    ) -> "Chain[t.List[T]]": ...
    def for_each_right(self, iteratee):
        return self._wrap(pyd.for_each_right)(iteratee)
    @t.overload
    def group_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], T2]
    ) -> "Chain[t.Dict[T2, t.List[T]]]": ...
    @t.overload
    def group_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Union[IterateeObjT, None] = None
    ) -> "Chain[t.Dict[t.Any, t.List[T]]]": ...
    def group_by(self, iteratee=None):
        return self._wrap(pyd.group_by)(iteratee)
    def includes(
        self: "Chain[t.Union[t.Sequence, t.Dict]]", target: t.Any, from_index: int = 0
    ) -> "Chain[bool]":
        return self._wrap(pyd.includes)(target, from_index)
    def invoke_map(
        self: "Chain[t.Iterable]", path: PathT, *args: t.Any, **kwargs: t.Any
    ) -> "Chain[t.List[t.Any]]":
        return self._wrap(pyd.invoke_map)(path, *args, **kwargs)
    @t.overload
    def key_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], T2]
    ) -> "Chain[t.Dict[T2, T]]": ...
    @t.overload
    def key_by(
        self: "Chain[t.Iterable]", iteratee: t.Union[IterateeObjT, None] = None
    ) -> "Chain[t.Dict]": ...
    def key_by(self, iteratee=None):
        return self._wrap(pyd.key_by)(iteratee)
    @t.overload
    def map_(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T2], T3]
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def map_(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], T3]
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def map_(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T, t.Dict[T, T2]], T3]
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def map_(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], T2]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def map_(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], T2]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def map_(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], T2]
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def map_(
        self: "Chain[t.Iterable]", iteratee: t.Union[IterateeObjT, None] = None
    ) -> "Chain[t.List]": ...
    def map_(self, iteratee=None):
        return self._wrap(pyd.map_)(iteratee)
    map = map_

    def nest(self: "Chain[t.Iterable]", *properties: t.Any) -> "Chain[t.Any]":
        return self._wrap(pyd.nest)(*properties)
    @t.overload
    def order_by(
        self: "Chain[t.Mapping[t.Any, T2]]",
        keys: t.Iterable[t.Union[str, int]],
        orders: t.Union[t.Iterable[bool], bool],
        reverse: bool = False,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def order_by(
        self: "Chain[t.Mapping[t.Any, T2]]",
        keys: t.Iterable[str],
        orders: None = None,
        reverse: bool = False,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def order_by(
        self: "Chain[t.Iterable[T]]",
        keys: t.Iterable[t.Union[str, int]],
        orders: t.Union[t.Iterable[bool], bool],
        reverse: bool = False,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def order_by(
        self: "Chain[t.Iterable[T]]",
        keys: t.Iterable[str],
        orders: None = None,
        reverse: bool = False,
    ) -> "Chain[t.List[T]]": ...
    def order_by(self, keys, orders=None, reverse=False):
        return self._wrap(pyd.order_by)(keys, orders, reverse)
    @t.overload
    def partition(
        self: "Chain[t.Mapping[T, T2]]", predicate: t.Callable[[T2, T, t.Dict[T, T2]], t.Any]
    ) -> "Chain[t.List[t.List[T2]]]": ...
    @t.overload
    def partition(
        self: "Chain[t.Mapping[T, T2]]", predicate: t.Callable[[T2, T], t.Any]
    ) -> "Chain[t.List[t.List[T2]]]": ...
    @t.overload
    def partition(
        self: "Chain[t.Mapping[t.Any, T2]]", predicate: t.Callable[[T2], t.Any]
    ) -> "Chain[t.List[t.List[T2]]]": ...
    @t.overload
    def partition(
        self: "Chain[t.Mapping[t.Any, T2]]", predicate: t.Union[IterateeObjT, None] = None
    ) -> "Chain[t.List[t.List[T2]]]": ...
    @t.overload
    def partition(
        self: "Chain[t.Iterable[T]]", predicate: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[t.List[t.List[T]]]": ...
    @t.overload
    def partition(
        self: "Chain[t.Iterable[T]]", predicate: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.List[t.List[T]]]": ...
    @t.overload
    def partition(
        self: "Chain[t.Iterable[T]]", predicate: t.Callable[[T], t.Any]
    ) -> "Chain[t.List[t.List[T]]]": ...
    @t.overload
    def partition(
        self: "Chain[t.Iterable[T]]", predicate: t.Union[IterateeObjT, None] = None
    ) -> "Chain[t.List[t.List[T]]]": ...
    def partition(self, predicate=None):
        return self._wrap(pyd.partition)(predicate)
    def pluck(self: "Chain[t.Iterable]", path: PathT) -> "Chain[t.List]":
        return self._wrap(pyd.pluck)(path)
    @t.overload
    def reduce_(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T3, T2, T], T3], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T3, T2], T3], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Mapping]", iteratee: t.Callable[[T3], T3], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Callable[[T2, T2, T], T2],
        accumulator: None = None,
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Callable[[T2, T2], T2],
        accumulator: None = None,
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Mapping]", iteratee: t.Callable[[T], T], accumulator: None = None
    ) -> "Chain[T]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T2, T, int], T2], accumulator: T2
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T2, T], T2], accumulator: T2
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Iterable]", iteratee: t.Callable[[T2], T2], accumulator: T2
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, T, int], T], accumulator: None = None
    ) -> "Chain[T]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, T], T], accumulator: None = None
    ) -> "Chain[T]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Iterable]", iteratee: t.Callable[[T], T], accumulator: None = None
    ) -> "Chain[T]": ...
    @t.overload
    def reduce_(
        self: "Chain[t.Iterable[T]]", iteratee: None = None, accumulator: t.Union[T, None] = None
    ) -> "Chain[T]": ...
    def reduce_(self, iteratee=None, accumulator=None):
        return self._wrap(pyd.reduce_)(iteratee, accumulator)
    reduce = reduce_

    @t.overload
    def reduce_right(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T3, T2, T], T3], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T3, T2], T3], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Mapping]", iteratee: t.Callable[[T3], T3], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Callable[[T2, T2, T], T2],
        accumulator: None = None,
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Callable[[T2, T2], T2],
        accumulator: None = None,
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Mapping]", iteratee: t.Callable[[T], T], accumulator: None = None
    ) -> "Chain[T]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T2, T, int], T2], accumulator: T2
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T2, T], T2], accumulator: T2
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Iterable]", iteratee: t.Callable[[T2], T2], accumulator: T2
    ) -> "Chain[T2]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, T, int], T], accumulator: None = None
    ) -> "Chain[T]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, T], T], accumulator: None = None
    ) -> "Chain[T]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Iterable]", iteratee: t.Callable[[T], T], accumulator: None = None
    ) -> "Chain[T]": ...
    @t.overload
    def reduce_right(
        self: "Chain[t.Iterable[T]]", iteratee: None = None, accumulator: t.Union[T, None] = None
    ) -> "Chain[T]": ...
    def reduce_right(self, iteratee=None, accumulator=None):
        return self._wrap(pyd.reduce_right)(iteratee, accumulator)
    @t.overload
    def reductions(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Callable[[T3, T2, T], T3],
        accumulator: T3,
        from_right: bool = False,
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Callable[[T3, T2], T3],
        accumulator: T3,
        from_right: bool = False,
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Mapping]",
        iteratee: t.Callable[[T3], T3],
        accumulator: T3,
        from_right: bool = False,
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Callable[[T2, T2, T], T2],
        accumulator: None = None,
        from_right: bool = False,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Callable[[T2, T2], T2],
        accumulator: None = None,
        from_right: bool = False,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Mapping]",
        iteratee: t.Callable[[T], T],
        accumulator: None = None,
        from_right: bool = False,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T2, T, int], T2],
        accumulator: T2,
        from_right: bool = False,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T2, T], T2],
        accumulator: T2,
        from_right: bool = False,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Iterable]",
        iteratee: t.Callable[[T2], T2],
        accumulator: T2,
        from_right: bool = False,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T, T, int], T],
        accumulator: None = None,
        from_right: bool = False,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T, T], T],
        accumulator: None = None,
        from_right: bool = False,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Iterable]",
        iteratee: t.Callable[[T], T],
        accumulator: None = None,
        from_right: bool = False,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reductions(
        self: "Chain[t.Iterable[T]]",
        iteratee: None = None,
        accumulator: t.Union[T, None] = None,
        from_right: bool = False,
    ) -> "Chain[t.List[T]]": ...
    def reductions(self, iteratee=None, accumulator=None, from_right=False):
        return self._wrap(pyd.reductions)(iteratee, accumulator, from_right)
    @t.overload
    def reductions_right(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T3, T2, T], T3], accumulator: T3
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T3, T2], T3], accumulator: T3
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Mapping]", iteratee: t.Callable[[T3], T3], accumulator: T3
    ) -> "Chain[t.List[T3]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Callable[[T2, T2, T], T2],
        accumulator: None = None,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Callable[[T2, T2], T2],
        accumulator: None = None,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Mapping]", iteratee: t.Callable[[T], T], accumulator: None = None
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T2, T, int], T2], accumulator: T2
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T2, T], T2], accumulator: T2
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Iterable]", iteratee: t.Callable[[T2], T2], accumulator: T2
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, T, int], T], accumulator: None = None
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, T], T], accumulator: None = None
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Iterable]", iteratee: t.Callable[[T], T], accumulator: None = None
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reductions_right(
        self: "Chain[t.Iterable[T]]", iteratee: None = None, accumulator: t.Union[T, None] = None
    ) -> "Chain[t.List[T]]": ...
    def reductions_right(self, iteratee=None, accumulator=None):
        return self._wrap(pyd.reductions_right)(iteratee, accumulator)
    @t.overload
    def reject(
        self: "Chain[t.Mapping[T, T2]]",
        predicate: t.Union[t.Callable[[T2, T, t.Dict[T, T2]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reject(
        self: "Chain[t.Mapping[T, T2]]",
        predicate: t.Union[t.Callable[[T2, T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reject(
        self: "Chain[t.Mapping[t.Any, T2]]",
        predicate: t.Union[t.Callable[[T2], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def reject(
        self: "Chain[t.Iterable[T]]",
        predicate: t.Union[t.Callable[[T, int, t.List[T]], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reject(
        self: "Chain[t.Iterable[T]]",
        predicate: t.Union[t.Callable[[T, int], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def reject(
        self: "Chain[t.Iterable[T]]",
        predicate: t.Union[t.Callable[[T], t.Any], IterateeObjT, None] = None,
    ) -> "Chain[t.List[T]]": ...
    def reject(self, predicate=None):
        return self._wrap(pyd.reject)(predicate)
    def sample(self: "Chain[t.Sequence[T]]") -> "Chain[T]":
        return self._wrap(pyd.sample)()
    def sample_size(
        self: "Chain[t.Sequence[T]]", n: t.Union[int, None] = None
    ) -> "Chain[t.List[T]]":
        return self._wrap(pyd.sample_size)(n)
    @t.overload
    def shuffle(self: "Chain[t.Mapping[t.Any, T]]") -> "Chain[t.List[T]]": ...
    @t.overload
    def shuffle(self: "Chain[t.Iterable[T]]") -> "Chain[t.List[T]]": ...
    def shuffle(self):
        return self._wrap(pyd.shuffle)()
    def size(self: "Chain[t.Sized]") -> "Chain[int]":
        return self._wrap(pyd.size)()
    def some(
        self: "Chain[t.Iterable[T]]", predicate: t.Union[t.Callable[[T], t.Any], None] = None
    ) -> "Chain[bool]":
        return self._wrap(pyd.some)(predicate)
    @t.overload
    def sort_by(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Union[t.Callable[[T2], t.Any], IterateeObjT, None] = None,
        reverse: bool = False,
    ) -> "Chain[t.List[T2]]": ...
    @t.overload
    def sort_by(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Union[t.Callable[[T], t.Any], IterateeObjT, None] = None,
        reverse: bool = False,
    ) -> "Chain[t.List[T]]": ...
    def sort_by(self, iteratee=None, reverse=False):
        return self._wrap(pyd.sort_by)(iteratee, reverse)
    def after(self: "Chain[t.Callable[P, T]]", n: t.SupportsInt) -> "Chain[After[P, T]]":
        return self._wrap(pyd.after)(n)
    def ary(self: "Chain[t.Callable[..., T]]", n: t.Union[t.SupportsInt, None]) -> "Chain[Ary[T]]":
        return self._wrap(pyd.ary)(n)
    def before(self: "Chain[t.Callable[P, T]]", n: t.SupportsInt) -> "Chain[Before[P, T]]":
        return self._wrap(pyd.before)(n)
    def conjoin(
        self: "Chain[t.Callable[[T], t.Any]]", *funcs: t.Callable[[T], t.Any]
    ) -> "Chain[t.Callable[[t.Iterable[T]], bool]]":
        return self._wrap(pyd.conjoin)(*funcs)
    @t.overload
    def curry(
        self: "Chain[t.Callable[[T1], T]]", arity: t.Union[int, None] = None
    ) -> "Chain[CurryOne[T1, T]]": ...
    @t.overload
    def curry(
        self: "Chain[t.Callable[[T1, T2], T]]", arity: t.Union[int, None] = None
    ) -> "Chain[CurryTwo[T1, T2, T]]": ...
    @t.overload
    def curry(
        self: "Chain[t.Callable[[T1, T2, T3], T]]", arity: t.Union[int, None] = None
    ) -> "Chain[CurryThree[T1, T2, T3, T]]": ...
    @t.overload
    def curry(
        self: "Chain[t.Callable[[T1, T2, T3, T4], T]]", arity: t.Union[int, None] = None
    ) -> "Chain[CurryFour[T1, T2, T3, T4, T]]": ...
    @t.overload
    def curry(
        self: "Chain[t.Callable[[T1, T2, T3, T4, T5], T]]", arity: t.Union[int, None] = None
    ) -> "Chain[CurryFive[T1, T2, T3, T4, T5, T]]": ...
    def curry(self, arity=None):
        return self._wrap(pyd.curry)(arity)
    @t.overload
    def curry_right(
        self: "Chain[t.Callable[[T1], T]]", arity: t.Union[int, None] = None
    ) -> "Chain[CurryRightOne[T1, T]]": ...
    @t.overload
    def curry_right(
        self: "Chain[t.Callable[[T1, T2], T]]", arity: t.Union[int, None] = None
    ) -> "Chain[CurryRightTwo[T2, T1, T]]": ...
    @t.overload
    def curry_right(
        self: "Chain[t.Callable[[T1, T2, T3], T]]", arity: t.Union[int, None] = None
    ) -> "Chain[CurryRightThree[T3, T2, T1, T]]": ...
    @t.overload
    def curry_right(
        self: "Chain[t.Callable[[T1, T2, T3, T4], T]]", arity: t.Union[int, None] = None
    ) -> "Chain[CurryRightFour[T4, T3, T2, T1, T]]": ...
    @t.overload
    def curry_right(
        self: "Chain[t.Callable[[T1, T2, T3, T4, T5], T]]",
    ) -> "Chain[CurryRightFive[T5, T4, T3, T2, T1, T]]": ...
    def curry_right(self, arity=None):
        return self._wrap(pyd.curry_right)(arity)
    def debounce(
        self: "Chain[t.Callable[P, T]]", wait: int, max_wait: t.Union[int, Literal[False]] = False
    ) -> "Chain[Debounce[P, T]]":
        return self._wrap(pyd.debounce)(wait, max_wait)
    def delay(
        self: "Chain[t.Callable[P, T]]", wait: int, *args: "P.args", **kwargs: "P.kwargs"
    ) -> "Chain[T]":
        return self._wrap(pyd.delay)(wait, *args, **kwargs)
    def disjoin(
        self: "Chain[t.Callable[[T], t.Any]]", *funcs: t.Callable[[T], t.Any]
    ) -> "Chain[Disjoin[T]]":
        return self._wrap(pyd.disjoin)(*funcs)
    @t.overload
    def flip(
        self: "Chain[t.Callable[[T1, T2, T3, T4, T5], T]]",
    ) -> "Chain[t.Callable[[T5, T4, T3, T2, T1], T]]": ...
    @t.overload
    def flip(
        self: "Chain[t.Callable[[T1, T2, T3, T4], T]]",
    ) -> "Chain[t.Callable[[T4, T3, T2, T1], T]]": ...
    @t.overload
    def flip(
        self: "Chain[t.Callable[[T1, T2, T3], T]]",
    ) -> "Chain[t.Callable[[T3, T2, T1], T]]": ...
    @t.overload
    def flip(self: "Chain[t.Callable[[T1, T2], T]]") -> "Chain[t.Callable[[T2, T1], T]]": ...
    @t.overload
    def flip(self: "Chain[t.Callable[[T1], T]]") -> "Chain[t.Callable[[T1], T]]": ...
    def flip(self: "Chain[t.Callable]") -> "Chain[t.Callable]":
        return self._wrap(pyd.flip)()
    @t.overload
    def flow(
        self: "Chain[t.Callable[P, T2]]",
        func2: t.Callable[[T2], T3],
        func3: t.Callable[[T3], T4],
        func4: t.Callable[[T4], T5],
        func5: t.Callable[[T5], T],
    ) -> "Chain[Flow[P, T]]": ...
    @t.overload
    def flow(
        self: "Chain[t.Callable[P, T2]]",
        func2: t.Callable[[T2], T3],
        func3: t.Callable[[T3], T4],
        func4: t.Callable[[T4], T],
    ) -> "Chain[Flow[P, T]]": ...
    @t.overload
    def flow(
        self: "Chain[t.Callable[P, T2]]", func2: t.Callable[[T2], T3], func3: t.Callable[[T3], T]
    ) -> "Chain[Flow[P, T]]": ...
    @t.overload
    def flow(
        self: "Chain[t.Callable[P, T2]]", func2: t.Callable[[T2], T]
    ) -> "Chain[Flow[P, T]]": ...
    @t.overload
    def flow(self: "Chain[t.Callable[P, T]]") -> "Chain[Flow[P, T]]": ...
    def flow(self, *funcs):
        return self._wrap(pyd.flow)(*funcs)
    @t.overload
    def flow_right(
        self: "Chain[t.Callable[[T4], T]]",
        func4: t.Callable[[T3], T4],
        func3: t.Callable[[T2], T3],
        func2: t.Callable[[T1], T2],
        func1: t.Callable[P, T1],
    ) -> "Chain[Flow[P, T]]": ...
    @t.overload
    def flow_right(
        self: "Chain[t.Callable[[T3], T]]",
        func3: t.Callable[[T2], T3],
        func2: t.Callable[[T1], T2],
        func1: t.Callable[P, T1],
    ) -> "Chain[Flow[P, T]]": ...
    @t.overload
    def flow_right(
        self: "Chain[t.Callable[[T2], T]]", func2: t.Callable[[T1], T2], func1: t.Callable[P, T1]
    ) -> "Chain[Flow[P, T]]": ...
    @t.overload
    def flow_right(
        self: "Chain[t.Callable[[T1], T]]", func1: t.Callable[P, T1]
    ) -> "Chain[Flow[P, T]]": ...
    @t.overload
    def flow_right(self: "Chain[t.Callable[P, T]]") -> "Chain[Flow[P, T]]": ...
    def flow_right(self, *funcs):
        return self._wrap(pyd.flow_right)(*funcs)
    def iterated(self: "Chain[t.Callable[[T], T]]") -> "Chain[Iterated[T]]":
        return self._wrap(pyd.iterated)()
    def juxtapose(
        self: "Chain[t.Callable[P, T]]", *funcs: t.Callable[P, T]
    ) -> "Chain[Juxtapose[P, T]]":
        return self._wrap(pyd.juxtapose)(*funcs)
    def negate(self: "Chain[t.Callable[P, t.Any]]") -> "Chain[Negate[P]]":
        return self._wrap(pyd.negate)()
    def once(self: "Chain[t.Callable[P, T]]") -> "Chain[Once[P, T]]":
        return self._wrap(pyd.once)()
    @t.overload
    def over_args(
        self: "Chain[t.Callable[[T1, T2, T3, T4, T5], T]]",
        transform_one: t.Callable[[T1], T1],
        transform_two: t.Callable[[T2], T2],
        transform_three: t.Callable[[T3], T3],
        transform_four: t.Callable[[T4], T4],
        transform_five: t.Callable[[T5], T5],
    ) -> "Chain[t.Callable[[T1, T2, T3, T4, T5], T]]": ...
    @t.overload
    def over_args(
        self: "Chain[t.Callable[[T1, T2, T3, T4], T]]",
        transform_one: t.Callable[[T1], T1],
        transform_two: t.Callable[[T2], T2],
        transform_three: t.Callable[[T3], T3],
        transform_four: t.Callable[[T4], T4],
    ) -> "Chain[t.Callable[[T1, T2, T3, T4], T]]": ...
    @t.overload
    def over_args(
        self: "Chain[t.Callable[[T1, T2, T3], T]]",
        transform_one: t.Callable[[T1], T1],
        transform_two: t.Callable[[T2], T2],
        transform_three: t.Callable[[T3], T3],
    ) -> "Chain[t.Callable[[T1, T2, T3], T]]": ...
    @t.overload
    def over_args(
        self: "Chain[t.Callable[[T1, T2], T]]",
        transform_one: t.Callable[[T1], T1],
        transform_two: t.Callable[[T2], T2],
    ) -> "Chain[t.Callable[[T1, T2], T]]": ...
    @t.overload
    def over_args(
        self: "Chain[t.Callable[[T1], T]]", transform_one: t.Callable[[T1], T1]
    ) -> "Chain[t.Callable[[T1], T]]": ...
    def over_args(self: "Chain[t.Callable]", *transforms: t.Callable) -> "Chain[t.Callable]":
        return self._wrap(pyd.over_args)(*transforms)
    def partial(
        self: "Chain[t.Callable[..., T]]", *args: t.Any, **kwargs: t.Any
    ) -> "Chain[Partial[T]]":
        return self._wrap(pyd.partial)(*args, **kwargs)
    def partial_right(
        self: "Chain[t.Callable[..., T]]", *args: t.Any, **kwargs: t.Any
    ) -> "Chain[Partial[T]]":
        return self._wrap(pyd.partial_right)(*args, **kwargs)
    def rearg(self: "Chain[t.Callable[P, T]]", *indexes: int) -> "Chain[Rearg[P, T]]":
        return self._wrap(pyd.rearg)(*indexes)
    def spread(self: "Chain[t.Callable[..., T]]") -> "Chain[Spread[T]]":
        return self._wrap(pyd.spread)()
    def throttle(self: "Chain[t.Callable[P, T]]", wait: int) -> "Chain[Throttle[P, T]]":
        return self._wrap(pyd.throttle)(wait)
    def unary(self: "Chain[t.Callable[..., T]]") -> "Chain[Ary[T]]":
        return self._wrap(pyd.unary)()
    def wrap(self: "Chain[T1]", func: t.Callable[Concatenate[T1, P], T]) -> "Chain[Partial[T]]":
        return self._wrap(pyd.wrap)(func)
    @t.overload
    def add(self: "Chain['SupportsAdd[T, T2]']", b: T) -> "Chain[T2]": ...
    @t.overload
    def add(self: "Chain[T]", b: "SupportsAdd[T, T2]") -> "Chain[T2]": ...
    def add(self, b):
        return self._wrap(pyd.add)(b)
    @t.overload
    def sum_(self: "Chain[t.Mapping[t.Any, 'SupportsAdd[int, T]']]") -> "Chain[T]": ...
    @t.overload
    def sum_(self: "Chain[t.Iterable['SupportsAdd[int, T]']]") -> "Chain[T]": ...
    def sum_(self):
        return self._wrap(pyd.sum_)()
    sum = sum_

    @t.overload
    def sum_by(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Callable[[T2, T, t.Dict[T, T2]], "SupportsAdd[int, T3]"],
    ) -> "Chain[T3]": ...
    @t.overload
    def sum_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], "SupportsAdd[int, T3]"]
    ) -> "Chain[T3]": ...
    @t.overload
    def sum_by(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T2], "SupportsAdd[int, T3]"]
    ) -> "Chain[T3]": ...
    @t.overload
    def sum_by(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T, int, t.List[T]], "SupportsAdd[int, T2]"],
    ) -> "Chain[T2]": ...
    @t.overload
    def sum_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], "SupportsAdd[int, T2]"]
    ) -> "Chain[T2]": ...
    @t.overload
    def sum_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], "SupportsAdd[int, T2]"]
    ) -> "Chain[T2]": ...
    @t.overload
    def sum_by(
        self: "Chain[t.Mapping[t.Any, 'SupportsAdd[int, T]']]", iteratee: None = None
    ) -> "Chain[T]": ...
    @t.overload
    def sum_by(
        self: "Chain[t.Iterable['SupportsAdd[int, T]']]", iteratee: None = None
    ) -> "Chain[T]": ...
    def sum_by(self, iteratee=None):
        return self._wrap(pyd.sum_by)(iteratee)
    @t.overload
    def mean(self: "Chain[t.Mapping[t.Any, 'SupportsAdd[int, t.Any]']]") -> "Chain[float]": ...
    @t.overload
    def mean(self: "Chain[t.Iterable['SupportsAdd[int, t.Any]']]") -> "Chain[float]": ...
    def mean(self):
        return self._wrap(pyd.mean)()
    @t.overload
    def mean_by(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Callable[[T2, T, t.Dict[T, T2]], "SupportsAdd[int, t.Any]"],
    ) -> "Chain[float]": ...
    @t.overload
    def mean_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], "SupportsAdd[int, t.Any]"]
    ) -> "Chain[float]": ...
    @t.overload
    def mean_by(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T2], "SupportsAdd[int, t.Any]"]
    ) -> "Chain[float]": ...
    @t.overload
    def mean_by(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T, int, t.List[T]], "SupportsAdd[int, t.Any]"],
    ) -> "Chain[float]": ...
    @t.overload
    def mean_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], "SupportsAdd[int, t.Any]"]
    ) -> "Chain[float]": ...
    @t.overload
    def mean_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], "SupportsAdd[int, t.Any]"]
    ) -> "Chain[float]": ...
    @t.overload
    def mean_by(
        self: "Chain[t.Mapping[t.Any, 'SupportsAdd[int, t.Any]']]", iteratee: None = None
    ) -> "Chain[float]": ...
    @t.overload
    def mean_by(
        self: "Chain[t.Iterable['SupportsAdd[int, t.Any]']]", iteratee: None = None
    ) -> "Chain[float]": ...
    def mean_by(self, iteratee=None):
        return self._wrap(pyd.mean_by)(iteratee)
    def ceil(self: "Chain[NumberT]", precision: int = 0) -> "Chain[float]":
        return self._wrap(pyd.ceil)(precision)
    def clamp(
        self: "Chain[NumT]", lower: NumT2, upper: t.Union[NumT3, None] = None
    ) -> "Chain[t.Union[NumT, NumT2, NumT3]]":
        return self._wrap(pyd.clamp)(lower, upper)
    def divide(
        self: "Chain[t.Union[NumberT, None]]", divisor: t.Union[NumberT, None]
    ) -> "Chain[float]":
        return self._wrap(pyd.divide)(divisor)
    def floor(self: "Chain[NumberT]", precision: int = 0) -> "Chain[float]":
        return self._wrap(pyd.floor)(precision)
    @t.overload
    def max_(
        self: "Chain[t.Mapping[t.Any, 'SupportsRichComparisonT']]", default: Unset = UNSET
    ) -> "Chain['SupportsRichComparisonT']": ...
    @t.overload
    def max_(
        self: "Chain[t.Mapping[t.Any, 'SupportsRichComparisonT']]", default: T
    ) -> "Chain[t.Union['SupportsRichComparisonT', T]]": ...
    @t.overload
    def max_(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]", default: Unset = UNSET
    ) -> "Chain['SupportsRichComparisonT']": ...
    @t.overload
    def max_(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]", default: T
    ) -> "Chain[t.Union['SupportsRichComparisonT', T]]": ...
    def max_(self, default=UNSET):
        return self._wrap(pyd.max_)(default)
    max = max_

    @t.overload
    def max_by(
        self: "Chain[t.Mapping[t.Any, 'SupportsRichComparisonT']]",
        iteratee: None = None,
        default: Unset = UNSET,
    ) -> "Chain['SupportsRichComparisonT']": ...
    @t.overload
    def max_by(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
        default: Unset = UNSET,
    ) -> "Chain[T2]": ...
    @t.overload
    def max_by(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
        *,
        default: T
    ) -> "Chain[t.Union[T2, T]]": ...
    @t.overload
    def max_by(
        self: "Chain[t.Mapping[t.Any, 'SupportsRichComparisonT']]",
        iteratee: None = None,
        *,
        default: T
    ) -> "Chain[t.Union['SupportsRichComparisonT', T]]": ...
    @t.overload
    def max_by(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]",
        iteratee: None = None,
        default: Unset = UNSET,
    ) -> "Chain['SupportsRichComparisonT']": ...
    @t.overload
    def max_by(
        self: "Chain[t.Iterable[T2]]",
        iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
        default: Unset = UNSET,
    ) -> "Chain[T2]": ...
    @t.overload
    def max_by(
        self: "Chain[t.Iterable[T2]]",
        iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
        *,
        default: T
    ) -> "Chain[t.Union[T2, T]]": ...
    @t.overload
    def max_by(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]", iteratee: None = None, *, default: T
    ) -> "Chain[t.Union['SupportsRichComparisonT', T]]": ...
    @t.overload
    def max_by(
        self: "Chain[t.Iterable[T]]", iteratee: IterateeObjT, default: Unset = UNSET
    ) -> "Chain[T]": ...
    @t.overload
    def max_by(
        self: "Chain[t.Iterable[T]]", iteratee: IterateeObjT, default: T2
    ) -> "Chain[t.Union[T, T2]]": ...
    def max_by(self, iteratee=None, default=UNSET):
        return self._wrap(pyd.max_by)(iteratee, default)
    @t.overload
    def median(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T, t.Dict[T, T2]], NumberT]
    ) -> "Chain[t.Union[float, int]]": ...
    @t.overload
    def median(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], NumberT]
    ) -> "Chain[t.Union[float, int]]": ...
    @t.overload
    def median(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T2], NumberT]
    ) -> "Chain[t.Union[float, int]]": ...
    @t.overload
    def median(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], NumberT]
    ) -> "Chain[t.Union[float, int]]": ...
    @t.overload
    def median(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], NumberT]
    ) -> "Chain[t.Union[float, int]]": ...
    @t.overload
    def median(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], NumberT]
    ) -> "Chain[t.Union[float, int]]": ...
    @t.overload
    def median(
        self: "Chain[t.Iterable[NumberT]]", iteratee: None = None
    ) -> "Chain[t.Union[float, int]]": ...
    def median(self, iteratee=None):
        return self._wrap(pyd.median)(iteratee)
    @t.overload
    def min_(
        self: "Chain[t.Mapping[t.Any, 'SupportsRichComparisonT']]", default: Unset = UNSET
    ) -> "Chain['SupportsRichComparisonT']": ...
    @t.overload
    def min_(
        self: "Chain[t.Mapping[t.Any, 'SupportsRichComparisonT']]", default: T
    ) -> "Chain[t.Union['SupportsRichComparisonT', T]]": ...
    @t.overload
    def min_(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]", default: Unset = UNSET
    ) -> "Chain['SupportsRichComparisonT']": ...
    @t.overload
    def min_(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]", default: T
    ) -> "Chain[t.Union['SupportsRichComparisonT', T]]": ...
    def min_(self, default=UNSET):
        return self._wrap(pyd.min_)(default)
    min = min_

    @t.overload
    def min_by(
        self: "Chain[t.Mapping[t.Any, 'SupportsRichComparisonT']]",
        iteratee: None = None,
        default: Unset = UNSET,
    ) -> "Chain['SupportsRichComparisonT']": ...
    @t.overload
    def min_by(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
        default: Unset = UNSET,
    ) -> "Chain[T2]": ...
    @t.overload
    def min_by(
        self: "Chain[t.Mapping[t.Any, T2]]",
        iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
        *,
        default: T
    ) -> "Chain[t.Union[T2, T]]": ...
    @t.overload
    def min_by(
        self: "Chain[t.Mapping[t.Any, 'SupportsRichComparisonT']]",
        iteratee: None = None,
        *,
        default: T
    ) -> "Chain[t.Union['SupportsRichComparisonT', T]]": ...
    @t.overload
    def min_by(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]",
        iteratee: None = None,
        default: Unset = UNSET,
    ) -> "Chain['SupportsRichComparisonT']": ...
    @t.overload
    def min_by(
        self: "Chain[t.Iterable[T2]]",
        iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
        default: Unset = UNSET,
    ) -> "Chain[T2]": ...
    @t.overload
    def min_by(
        self: "Chain[t.Iterable[T2]]",
        iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
        *,
        default: T
    ) -> "Chain[t.Union[T2, T]]": ...
    @t.overload
    def min_by(
        self: "Chain[t.Iterable['SupportsRichComparisonT']]", iteratee: None = None, *, default: T
    ) -> "Chain[t.Union['SupportsRichComparisonT', T]]": ...
    @t.overload
    def min_by(
        self: "Chain[t.Iterable[T]]", iteratee: IterateeObjT, default: Unset = UNSET
    ) -> "Chain[T]": ...
    @t.overload
    def min_by(
        self: "Chain[t.Iterable[T]]", iteratee: IterateeObjT, default: T2
    ) -> "Chain[t.Union[T, T2]]": ...
    def min_by(self, iteratee=None, default=UNSET):
        return self._wrap(pyd.min_by)(iteratee, default)
    def moving_mean(
        self: "Chain[t.Sequence['SupportsAdd[int, t.Any]']]", size: t.SupportsInt
    ) -> "Chain[t.List[float]]":
        return self._wrap(pyd.moving_mean)(size)
    @t.overload
    def multiply(self: "Chain[SupportsMul[int, T2]]", multiplicand: None) -> "Chain[T2]": ...
    @t.overload
    def multiply(self: "Chain[None]", multiplicand: SupportsMul[int, T2]) -> "Chain[T2]": ...
    @t.overload
    def multiply(self: "Chain[None]", multiplicand: None) -> "Chain[int]": ...
    @t.overload
    def multiply(self: "Chain[SupportsMul[T, T2]]", multiplicand: T) -> "Chain[T2]": ...
    @t.overload
    def multiply(self: "Chain[T]", multiplicand: SupportsMul[T, T2]) -> "Chain[T2]": ...
    def multiply(self, multiplicand):
        return self._wrap(pyd.multiply)(multiplicand)
    @t.overload
    def power(self: "Chain[int]", n: int) -> "Chain[t.Union[int, float]]": ...
    @t.overload
    def power(self: "Chain[float]", n: t.Union[int, float]) -> "Chain[float]": ...
    @t.overload
    def power(self: "Chain[t.List[int]]", n: int) -> "Chain[t.List[t.Union[int, float]]]": ...
    @t.overload
    def power(
        self: "Chain[t.List[float]]", n: t.List[t.Union[int, float]]
    ) -> "Chain[t.List[float]]": ...
    def power(self, n):
        return self._wrap(pyd.power)(n)
    @t.overload
    def round_(
        self: "Chain[t.List[SupportsRound[NumberT]]]", precision: int = 0
    ) -> "Chain[t.List[float]]": ...
    @t.overload
    def round_(self: "Chain[SupportsRound[NumberT]]", precision: int = 0) -> "Chain[float]": ...
    def round_(self, precision=0):
        return self._wrap(pyd.round_)(precision)
    round = round_

    @t.overload
    def scale(
        self: "Chain[t.Iterable['Decimal']]", maximum: "Decimal"
    ) -> "Chain[t.List['Decimal']]": ...
    @t.overload
    def scale(
        self: "Chain[t.Iterable[NumberNoDecimalT]]", maximum: NumberNoDecimalT
    ) -> "Chain[t.List[float]]": ...
    @t.overload
    def scale(self: "Chain[t.Iterable[NumberT]]", maximum: int = 1) -> "Chain[t.List[float]]": ...
    def scale(self, maximum: NumberT = 1):
        return self._wrap(pyd.scale)(maximum)
    @t.overload
    def slope(
        self: "Chain[t.Union[t.Tuple['Decimal', 'Decimal'], t.List['Decimal']]]",
        point2: t.Union[t.Tuple["Decimal", "Decimal"], t.List["Decimal"]],
    ) -> "Chain['Decimal']": ...
    @t.overload
    def slope(
        self: "Chain[t.Union[t.Tuple[NumberNoDecimalT, NumberNoDecimalT], t.List[NumberNoDecimalT]]]",
        point2: t.Union[t.Tuple[NumberNoDecimalT, NumberNoDecimalT], t.List[NumberNoDecimalT]],
    ) -> "Chain[float]": ...
    def slope(self, point2):
        return self._wrap(pyd.slope)(point2)
    def std_deviation(self: "Chain[t.List[NumberT]]") -> "Chain[float]":
        return self._wrap(pyd.std_deviation)()
    @t.overload
    def subtract(self: "Chain['SupportsSub[T, T2]']", subtrahend: T) -> "Chain[T2]": ...
    @t.overload
    def subtract(self: "Chain[T]", subtrahend: "SupportsSub[T, T2]") -> "Chain[T2]": ...
    def subtract(self, subtrahend):
        return self._wrap(pyd.subtract)(subtrahend)
    def transpose(self: "Chain[t.Iterable[t.Iterable[T]]]") -> "Chain[t.List[t.List[T]]]":
        return self._wrap(pyd.transpose)()
    @t.overload
    def variance(self: "Chain[t.Mapping[t.Any, 'SupportsAdd[int, t.Any]']]") -> "Chain[float]": ...
    @t.overload
    def variance(self: "Chain[t.Iterable['SupportsAdd[int, t.Any]']]") -> "Chain[float]": ...
    def variance(self):
        return self._wrap(pyd.variance)()
    @t.overload
    def zscore(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T, t.Dict[T, T2]], NumberT]
    ) -> "Chain[t.List[float]]": ...
    @t.overload
    def zscore(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], NumberT]
    ) -> "Chain[t.List[float]]": ...
    @t.overload
    def zscore(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T2], NumberT]
    ) -> "Chain[t.List[float]]": ...
    @t.overload
    def zscore(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], NumberT]
    ) -> "Chain[t.List[float]]": ...
    @t.overload
    def zscore(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], NumberT]
    ) -> "Chain[t.List[float]]": ...
    @t.overload
    def zscore(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], NumberT]
    ) -> "Chain[t.List[float]]": ...
    @t.overload
    def zscore(
        self: "Chain[t.Iterable[NumberT]]", iteratee: None = None
    ) -> "Chain[t.List[float]]": ...
    def zscore(self, iteratee=None):
        return self._wrap(pyd.zscore)(iteratee)
    @t.overload
    def assign(
        self: "Chain[t.Mapping[T, T2]]", *sources: t.Mapping[T3, T4]
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T4]]]": ...
    @t.overload
    def assign(
        self: "Chain[t.Union[t.Tuple[T, ...], t.List[T]]]", *sources: t.Mapping[int, T2]
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    def assign(self, *sources) -> "Chain[t.Union[t.List, t.Dict]]":
        return self._wrap(pyd.assign)(*sources)
    @t.overload
    def assign_with(
        self: "Chain[t.Mapping[T, T2]]",
        *sources: t.Mapping[T3, t.Any],
        customizer: t.Callable[[t.Union[T2, None]], T5]
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T5]]]": ...
    @t.overload
    def assign_with(
        self: "Chain[t.Mapping[T, T2]]",
        *sources: t.Mapping[T3, T4],
        customizer: t.Callable[[t.Union[T2, None], T4], T5]
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T5]]]": ...
    @t.overload
    def assign_with(
        self: "Chain[t.Mapping[T, T2]]",
        *sources: t.Mapping[T3, T4],
        customizer: t.Callable[[t.Union[T2, None], T4, T3], T5]
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T5]]]": ...
    @t.overload
    def assign_with(
        self: "Chain[t.Mapping[T, T2]]",
        *sources: t.Mapping[T3, T4],
        customizer: t.Callable[[t.Union[T2, None], T4, T3, t.Dict[T, T2]], T5]
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T5]]]": ...
    @t.overload
    def assign_with(
        self: "Chain[t.Mapping[T, T2]]",
        *sources: t.Mapping[T3, T4],
        customizer: t.Callable[[t.Union[T2, None], T4, T3, t.Dict[T, T2], t.Dict[T3, T4]], T5]
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T5]]]": ...
    @t.overload
    def assign_with(
        self: "Chain[t.Mapping[T, T2]]", *sources: t.Mapping[T3, T4], customizer: None = None
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T4]]]": ...
    def assign_with(self, *sources, customizer=None):
        return self._wrap(pyd.assign_with)(*sources, customizer=customizer)
    @t.overload
    def callables(
        self: "Chain[t.Mapping['SupportsRichComparisonT', t.Any]]",
    ) -> "Chain[t.List['SupportsRichComparisonT']]": ...
    @t.overload
    def callables(self: "Chain[t.Iterable[T]]") -> "Chain[t.List[T]]": ...
    def callables(self) -> "Chain[t.List]":
        return self._wrap(pyd.callables)()
    def clone(self: "Chain[T]") -> "Chain[T]":
        return self._wrap(pyd.clone)()
    @t.overload
    def clone_with(
        self: "Chain[t.Mapping[T, T2]]", customizer: t.Callable[[T2, T, t.Mapping[T, T2]], T3]
    ) -> "Chain[t.Dict[T, t.Union[T2, T3]]]": ...
    @t.overload
    def clone_with(
        self: "Chain[t.Mapping[T, T2]]", customizer: t.Callable[[T2, T], T3]
    ) -> "Chain[t.Dict[T, t.Union[T2, T3]]]": ...
    @t.overload
    def clone_with(
        self: "Chain[t.Mapping[T, T2]]", customizer: t.Callable[[T2], T3]
    ) -> "Chain[t.Dict[T, t.Union[T2, T3]]]": ...
    @t.overload
    def clone_with(
        self: "Chain[t.List[T]]", customizer: t.Callable[[T, int, t.List[T]], T2]
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    @t.overload
    def clone_with(
        self: "Chain[t.List[T]]", customizer: t.Callable[[T, int], T2]
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    @t.overload
    def clone_with(
        self: "Chain[t.List[T]]", customizer: t.Callable[[T], T2]
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    @t.overload
    def clone_with(self: "Chain[T]", customizer: None = None) -> "Chain[T]": ...
    @t.overload
    def clone_with(self: "Chain[t.Any]", customizer: t.Callable) -> "Chain[t.Any]": ...
    def clone_with(self, customizer=None):
        return self._wrap(pyd.clone_with)(customizer)
    def clone_deep(self: "Chain[T]") -> "Chain[T]":
        return self._wrap(pyd.clone_deep)()
    @t.overload
    def clone_deep_with(
        self: "Chain[t.Mapping[T, T2]]", customizer: t.Callable[[T2, T, t.Mapping[T, T2]], T3]
    ) -> "Chain[t.Dict[T, t.Union[T2, T3]]]": ...
    @t.overload
    def clone_deep_with(
        self: "Chain[t.Mapping[T, T2]]", customizer: t.Callable[[T2, T], T3]
    ) -> "Chain[t.Dict[T, t.Union[T2, T3]]]": ...
    @t.overload
    def clone_deep_with(
        self: "Chain[t.Mapping[T, T2]]", customizer: t.Callable[[T2], T3]
    ) -> "Chain[t.Dict[T, t.Union[T2, T3]]]": ...
    @t.overload
    def clone_deep_with(
        self: "Chain[t.List[T]]", customizer: t.Callable[[T, int, t.List[T]], T2]
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    @t.overload
    def clone_deep_with(
        self: "Chain[t.List[T]]", customizer: t.Callable[[T, int], T2]
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    @t.overload
    def clone_deep_with(
        self: "Chain[t.List[T]]", customizer: t.Callable[[T], T2]
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    @t.overload
    def clone_deep_with(self: "Chain[T]", customizer: None = None) -> "Chain[T]": ...
    @t.overload
    def clone_deep_with(self: "Chain[t.Any]", customizer: t.Callable) -> "Chain[t.Any]": ...
    def clone_deep_with(self, customizer=None):
        return self._wrap(pyd.clone_deep_with)(customizer)
    def defaults(
        self: "Chain[t.Dict[T, T2]]", *sources: t.Dict[T3, T4]
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T4]]]":
        return self._wrap(pyd.defaults)(*sources)
    def defaults_deep(
        self: "Chain[t.Dict[T, T2]]", *sources: t.Dict[T3, T4]
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T4]]]":
        return self._wrap(pyd.defaults_deep)(*sources)
    @t.overload
    def find_key(
        self: "Chain[t.Mapping[T, T2]]", predicate: t.Callable[[T2, T, t.Dict[T, T2]], t.Any]
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_key(
        self: "Chain[t.Mapping[T, T2]]", predicate: t.Callable[[T2, T], t.Any]
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_key(
        self: "Chain[t.Mapping[T, T2]]", predicate: t.Callable[[T2], t.Any]
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_key(
        self: "Chain[t.Mapping[T, t.Any]]", predicate: None = None
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_key(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[t.Union[int, None]]": ...
    @t.overload
    def find_key(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.Union[int, None]]": ...
    @t.overload
    def find_key(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], t.Any]
    ) -> "Chain[t.Union[int, None]]": ...
    @t.overload
    def find_key(
        self: "Chain[t.Iterable[t.Any]]", iteratee: None = None
    ) -> "Chain[t.Union[int, None]]": ...
    def find_key(self, predicate=None):
        return self._wrap(pyd.find_key)(predicate)
    @t.overload
    def find_last_key(
        self: "Chain[t.Mapping[T, T2]]", predicate: t.Callable[[T2, T, t.Dict[T, T2]], t.Any]
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_last_key(
        self: "Chain[t.Mapping[T, T2]]", predicate: t.Callable[[T2, T], t.Any]
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_last_key(
        self: "Chain[t.Mapping[T, T2]]", predicate: t.Callable[[T2], t.Any]
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_last_key(
        self: "Chain[t.Mapping[T, t.Any]]", predicate: None = None
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def find_last_key(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[t.Union[int, None]]": ...
    @t.overload
    def find_last_key(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.Union[int, None]]": ...
    @t.overload
    def find_last_key(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], t.Any]
    ) -> "Chain[t.Union[int, None]]": ...
    @t.overload
    def find_last_key(
        self: "Chain[t.Iterable[t.Any]]", iteratee: None = None
    ) -> "Chain[t.Union[int, None]]": ...
    def find_last_key(self, predicate=None):
        return self._wrap(pyd.find_last_key)(predicate)
    @t.overload
    def for_in(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T, t.Dict[T, T2]], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_in(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_in(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_in(
        self: "Chain[t.Mapping[T, T2]]", iteratee: None = None
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_in(
        self: "Chain[t.Sequence[T]]", iteratee: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_in(
        self: "Chain[t.Sequence[T]]", iteratee: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_in(
        self: "Chain[t.Sequence[T]]", iteratee: t.Callable[[T], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_in(self: "Chain[t.Sequence[T]]", iteratee: None = None) -> "Chain[t.List[T]]": ...
    def for_in(self, iteratee=None):
        return self._wrap(pyd.for_in)(iteratee)
    @t.overload
    def for_in_right(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T, t.Dict[T, T2]], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_in_right(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_in_right(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_in_right(
        self: "Chain[t.Mapping[T, T2]]", iteratee: None = None
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def for_in_right(
        self: "Chain[t.Sequence[T]]", iteratee: t.Callable[[T, int, t.List[T]], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_in_right(
        self: "Chain[t.Sequence[T]]", iteratee: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_in_right(
        self: "Chain[t.Sequence[T]]", iteratee: t.Callable[[T], t.Any]
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def for_in_right(self: "Chain[t.Sequence[T]]", iteratee: None = None) -> "Chain[t.List[T]]": ...
    def for_in_right(self, iteratee=None):
        return self._wrap(pyd.for_in_right)(iteratee)
    @t.overload
    def get(self: "Chain[t.List[T]]", path: int, default: T2) -> "Chain[t.Union[T, T2]]": ...
    @t.overload
    def get(
        self: "Chain[t.List[T]]", path: int, default: None = None
    ) -> "Chain[t.Union[T, None]]": ...
    @t.overload
    def get(self: "Chain[t.Any]", path: PathT, default: t.Any = None) -> "Chain[t.Any]": ...
    def get(self: "Chain[t.Any]", path: PathT, default: t.Any = None) -> "Chain[t.Any]":
        return self._wrap(pyd.get)(path, default)
    def has(self: "Chain[t.Any]", path: PathT) -> "Chain[bool]":
        return self._wrap(pyd.has)(path)
    @t.overload
    def invert(self: "Chain[t.Mapping[T, T2]]") -> "Chain[t.Dict[T2, T]]": ...
    @t.overload
    def invert(self: "Chain[t.Iterable[T]]") -> "Chain[t.Dict[T, int]]": ...
    def invert(self) -> "Chain[t.Dict]":
        return self._wrap(pyd.invert)()
    @t.overload
    def invert_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2], T3]
    ) -> "Chain[t.Dict[T3, t.List[T]]]": ...
    @t.overload
    def invert_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: None = None
    ) -> "Chain[t.Dict[T2, t.List[T]]]": ...
    @t.overload
    def invert_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], T2]
    ) -> "Chain[t.Dict[T2, t.List[int]]]": ...
    @t.overload
    def invert_by(
        self: "Chain[t.Iterable[T]]", iteratee: None = None
    ) -> "Chain[t.Dict[T, t.List[int]]]": ...
    def invert_by(self, iteratee=None):
        return self._wrap(pyd.invert_by)(iteratee)
    def invoke(self: "Chain[t.Any]", path: PathT, *args: t.Any, **kwargs: t.Any) -> "Chain[t.Any]":
        return self._wrap(pyd.invoke)(path, *args, **kwargs)
    @t.overload
    def keys(self: "Chain[t.Iterable[T]]") -> "Chain[t.List[T]]": ...
    @t.overload
    def keys(self: "Chain[t.Any]") -> "Chain[t.List]": ...
    def keys(self):
        return self._wrap(pyd.keys)()
    @t.overload
    def map_keys(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T, t.Dict[T, T2]], T3]
    ) -> "Chain[t.Dict[T3, T2]]": ...
    @t.overload
    def map_keys(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], T3]
    ) -> "Chain[t.Dict[T3, T2]]": ...
    @t.overload
    def map_keys(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T2], T3]
    ) -> "Chain[t.Dict[T3, T2]]": ...
    @t.overload
    def map_keys(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], T2]
    ) -> "Chain[t.Dict[T2, T]]": ...
    @t.overload
    def map_keys(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], T2]
    ) -> "Chain[t.Dict[T2, T]]": ...
    @t.overload
    def map_keys(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], T2]
    ) -> "Chain[t.Dict[T2, T]]": ...
    @t.overload
    def map_keys(
        self: "Chain[t.Iterable]", iteratee: t.Union[IterateeObjT, None] = None
    ) -> "Chain[t.Dict]": ...
    def map_keys(self, iteratee=None):
        return self._wrap(pyd.map_keys)(iteratee)
    @t.overload
    def map_values(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T, t.Dict[T, T2]], T3]
    ) -> "Chain[t.Dict[T, T3]]": ...
    @t.overload
    def map_values(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], T3]
    ) -> "Chain[t.Dict[T, T3]]": ...
    @t.overload
    def map_values(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2], T3]
    ) -> "Chain[t.Dict[T, T3]]": ...
    @t.overload
    def map_values(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int, t.List[T]], T2]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def map_values(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], T2]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def map_values(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], T2]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def map_values(
        self: "Chain[t.Iterable]", iteratee: t.Union[IterateeObjT, None] = None
    ) -> "Chain[t.Dict]": ...
    def map_values(self, iteratee=None):
        return self._wrap(pyd.map_values)(iteratee)
    def map_values_deep(
        self: "Chain[t.Iterable]",
        iteratee: t.Union[t.Callable, None] = None,
        property_path: t.Any = UNSET,
    ) -> "Chain[t.Any]":
        return self._wrap(pyd.map_values_deep)(iteratee, property_path)
    @t.overload
    def merge(
        self: "Chain[t.Mapping[T, T2]]", *sources: t.Mapping[T3, T4]
    ) -> "Chain[t.Dict[t.Union[T, T3], t.Union[T2, T4]]]": ...
    @t.overload
    def merge(
        self: "Chain[t.Sequence[T]]", *sources: t.Sequence[T2]
    ) -> "Chain[t.List[t.Union[T, T2]]]": ...
    def merge(self, *sources):
        return self._wrap(pyd.merge)(*sources)
    def merge_with(self: "Chain[t.Any]", *sources: t.Any, **kwargs: t.Any) -> "Chain[t.Any]":
        return self._wrap(pyd.merge_with)(*sources, **kwargs)
    @t.overload
    def omit(self: "Chain[t.Mapping[T, T2]]", *properties: PathT) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def omit(self: "Chain[t.Iterable[T]]", *properties: PathT) -> "Chain[t.Dict[int, T]]": ...
    @t.overload
    def omit(self: "Chain[t.Any]", *properties: PathT) -> "Chain[t.Dict]": ...
    def omit(self, *properties):
        return self._wrap(pyd.omit)(*properties)
    @t.overload
    def omit_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def omit_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def omit_by(self: "Chain[t.Dict[T, T2]]", iteratee: None = None) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def omit_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.Dict[int, T]]": ...
    @t.overload
    def omit_by(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T], t.Any]
    ) -> "Chain[t.Dict[int, T]]": ...
    @t.overload
    def omit_by(self: "Chain[t.List[T]]", iteratee: None = None) -> "Chain[t.Dict[int, T]]": ...
    @t.overload
    def omit_by(
        self: "Chain[t.Any]", iteratee: t.Union[t.Callable, None] = None
    ) -> "Chain[t.Dict]": ...
    def omit_by(self, iteratee=None):
        return self._wrap(pyd.omit_by)(iteratee)
    def parse_int(
        self: "Chain[t.Any]", radix: t.Union[int, None] = None
    ) -> "Chain[t.Union[int, None]]":
        return self._wrap(pyd.parse_int)(radix)
    @t.overload
    def pick(self: "Chain[t.Mapping[T, T2]]", *properties: PathT) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def pick(
        self: "Chain[t.Union[t.Tuple[T, ...], t.List[T]]]", *properties: PathT
    ) -> "Chain[t.Dict[int, T]]": ...
    @t.overload
    def pick(self: "Chain[t.Any]", *properties: PathT) -> "Chain[t.Dict]": ...
    def pick(self, *properties):
        return self._wrap(pyd.pick)(*properties)
    @t.overload
    def pick_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def pick_by(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T2, T], t.Any]
    ) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def pick_by(self: "Chain[t.Dict[T, T2]]", iteratee: None = None) -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def pick_by(
        self: "Chain[t.Union[t.Tuple[T, ...], t.List[T]]]", iteratee: t.Callable[[T, int], t.Any]
    ) -> "Chain[t.Dict[int, T]]": ...
    @t.overload
    def pick_by(
        self: "Chain[t.Union[t.Tuple[T, ...], t.List[T]]]", iteratee: t.Callable[[T], t.Any]
    ) -> "Chain[t.Dict[int, T]]": ...
    @t.overload
    def pick_by(
        self: "Chain[t.Union[t.Tuple[T, ...], t.List[T]]]", iteratee: None = None
    ) -> "Chain[t.Dict[int, T]]": ...
    @t.overload
    def pick_by(
        self: "Chain[t.Any]", iteratee: t.Union[t.Callable, None] = None
    ) -> "Chain[t.Dict]": ...
    def pick_by(self, iteratee=None):
        return self._wrap(pyd.pick_by)(iteratee)
    def rename_keys(
        self: "Chain[t.Dict[T, T2]]", key_map: t.Dict[t.Any, T3]
    ) -> "Chain[t.Dict[t.Union[T, T3], T2]]":
        return self._wrap(pyd.rename_keys)(key_map)
    def set_(self: "Chain[T]", path: PathT, value: t.Any) -> "Chain[T]":
        return self._wrap(pyd.set_)(path, value)
    set = set_

    def set_with(
        self: "Chain[T]", path: PathT, value: t.Any, customizer: t.Union[t.Callable, None] = None
    ) -> "Chain[T]":
        return self._wrap(pyd.set_with)(path, value, customizer)
    def to_boolean(
        self: "Chain[t.Any]",
        true_values: t.Tuple[str, ...] = ("true", "1"),
        false_values: t.Tuple[str, ...] = ("false", "0"),
    ) -> "Chain[t.Union[bool, None]]":
        return self._wrap(pyd.to_boolean)(true_values, false_values)
    @t.overload
    def to_dict(self: "Chain[t.Mapping[T, T2]]") -> "Chain[t.Dict[T, T2]]": ...
    @t.overload
    def to_dict(self: "Chain[t.Iterable[T]]") -> "Chain[t.Dict[int, T]]": ...
    @t.overload
    def to_dict(self: "Chain[t.Any]") -> "Chain[t.Dict]": ...
    def to_dict(self):
        return self._wrap(pyd.to_dict)()
    def to_integer(self: "Chain[t.Any]") -> "Chain[int]":
        return self._wrap(pyd.to_integer)()
    @t.overload
    def to_list(
        self: "Chain[t.Dict[t.Any, T]]", split_strings: bool = True
    ) -> "Chain[t.List[T]]": ...
    @t.overload
    def to_list(self: "Chain[t.Iterable[T]]", split_strings: bool = True) -> "Chain[t.List[T]]": ...
    @t.overload
    def to_list(self: "Chain[T]", split_strings: bool = True) -> "Chain[t.List[T]]": ...
    def to_list(self, split_strings=True):
        return self._wrap(pyd.to_list)(split_strings)
    def to_number(self: "Chain[t.Any]", precision: int = 0) -> "Chain[t.Union[float, None]]":
        return self._wrap(pyd.to_number)(precision)
    @t.overload
    def to_pairs(self: "Chain[t.Mapping[T, T2]]") -> "Chain[t.List[t.List[t.Union[T, T2]]]]": ...
    @t.overload
    def to_pairs(self: "Chain[t.Iterable[T]]") -> "Chain[t.List[t.List[t.Union[int, T]]]]": ...
    @t.overload
    def to_pairs(self: "Chain[t.Any]") -> "Chain[t.List]": ...
    def to_pairs(self):
        return self._wrap(pyd.to_pairs)()
    @t.overload
    def transform(
        self: "Chain[t.Mapping[T, T2]]",
        iteratee: t.Callable[[T3, T2, T, t.Dict[T, T2]], t.Any],
        accumulator: T3,
    ) -> "Chain[T3]": ...
    @t.overload
    def transform(
        self: "Chain[t.Mapping[T, T2]]", iteratee: t.Callable[[T3, T2, T], t.Any], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def transform(
        self: "Chain[t.Mapping[t.Any, T2]]", iteratee: t.Callable[[T3, T2], t.Any], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def transform(
        self: "Chain[t.Mapping[t.Any, t.Any]]", iteratee: t.Callable[[T3], t.Any], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def transform(
        self: "Chain[t.Iterable[T]]",
        iteratee: t.Callable[[T3, T, int, t.List[T]], t.Any],
        accumulator: T3,
    ) -> "Chain[T3]": ...
    @t.overload
    def transform(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T3, T, int], t.Any], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def transform(
        self: "Chain[t.Iterable[T]]", iteratee: t.Callable[[T3, T], t.Any], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def transform(
        self: "Chain[t.Iterable[t.Any]]", iteratee: t.Callable[[T3], t.Any], accumulator: T3
    ) -> "Chain[T3]": ...
    @t.overload
    def transform(
        self: "Chain[t.Any]", iteratee: t.Any = None, accumulator: t.Any = None
    ) -> "Chain[t.Any]": ...
    def transform(self, iteratee=None, accumulator=None):
        return self._wrap(pyd.transform)(iteratee, accumulator)
    @t.overload
    def update(
        self: "Chain[t.Dict[t.Any, T2]]", path: PathT, updater: t.Callable[[T2], t.Any]
    ) -> "Chain[t.Dict]": ...
    @t.overload
    def update(
        self: "Chain[t.List[T]]", path: PathT, updater: t.Callable[[T], t.Any]
    ) -> "Chain[t.List]": ...
    @t.overload
    def update(self: "Chain[T]", path: PathT, updater: t.Callable) -> "Chain[T]": ...
    def update(self, path, updater):
        return self._wrap(pyd.update)(path, updater)
    @t.overload
    def update_with(
        self: "Chain[t.Dict[t.Any, T2]]",
        path: PathT,
        updater: t.Callable[[T2], t.Any],
        customizer: t.Union[t.Callable, None],
    ) -> "Chain[t.Dict]": ...
    @t.overload
    def update_with(
        self: "Chain[t.List[T]]",
        path: PathT,
        updater: t.Callable[[T], t.Any],
        customizer: t.Union[t.Callable, None] = None,
    ) -> "Chain[t.List]": ...
    @t.overload
    def update_with(
        self: "Chain[T]",
        path: PathT,
        updater: t.Callable,
        customizer: t.Union[t.Callable, None] = None,
    ) -> "Chain[T]": ...
    def update_with(self, path, updater, customizer=None):
        return self._wrap(pyd.update_with)(path, updater, customizer)
    def unset(self: "Chain[t.Union[t.List, t.Dict]]", path: PathT) -> "Chain[bool]":
        return self._wrap(pyd.unset)(path)
    @t.overload
    def values(self: "Chain[t.Mapping[t.Any, T2]]") -> "Chain[t.List[T2]]": ...
    @t.overload
    def values(self: "Chain[t.Iterable[T]]") -> "Chain[t.List[T]]": ...
    @t.overload
    def values(self: "Chain[t.Any]") -> "Chain[t.List]": ...
    def values(self):
        return self._wrap(pyd.values)()
    def eq(self: "Chain[t.Any]", other: t.Any) -> "Chain[bool]":
        return self._wrap(pyd.eq)(other)
    def gt(self: "Chain['SupportsDunderGT[T]']", other: T) -> "Chain[bool]":
        return self._wrap(pyd.gt)(other)
    def gte(self: "Chain['SupportsDunderGE[T]']", other: T) -> "Chain[bool]":
        return self._wrap(pyd.gte)(other)
    def lt(self: "Chain['SupportsDunderLT[T]']", other: T) -> "Chain[bool]":
        return self._wrap(pyd.lt)(other)
    def lte(self: "Chain['SupportsDunderLE[T]']", other: T) -> "Chain[bool]":
        return self._wrap(pyd.lte)(other)
    def in_range(self: "Chain[t.Any]", start: t.Any = 0, end: t.Any = None) -> "Chain[bool]":
        return self._wrap(pyd.in_range)(start, end)
    def is_associative(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_associative)()
    def is_blank(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_blank)()
    def is_boolean(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_boolean)()
    def is_builtin(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_builtin)()
    def is_date(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_date)()
    def is_decreasing(
        self: "Chain[t.Union['SupportsRichComparison', t.List['SupportsRichComparison']]]",
    ) -> "Chain[bool]":
        return self._wrap(pyd.is_decreasing)()
    def is_dict(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_dict)()
    def is_empty(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_empty)()
    def is_equal(self: "Chain[t.Any]", other: t.Any) -> "Chain[bool]":
        return self._wrap(pyd.is_equal)(other)
    @t.overload
    def is_equal_with(
        self: "Chain[T]", other: T2, customizer: t.Callable[[T, T2], T3]
    ) -> "Chain[T3]": ...
    @t.overload
    def is_equal_with(
        self: "Chain[t.Any]", other: t.Any, customizer: t.Callable
    ) -> "Chain[bool]": ...
    @t.overload
    def is_equal_with(self: "Chain[t.Any]", other: t.Any, customizer: None) -> "Chain[bool]": ...
    def is_equal_with(self, other, customizer):
        return self._wrap(pyd.is_equal_with)(other, customizer)
    def is_error(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_error)()
    def is_even(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_even)()
    def is_float(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_float)()
    def is_function(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_function)()
    def is_increasing(
        self: "Chain[t.Union['SupportsRichComparison', t.List['SupportsRichComparison']]]",
    ) -> "Chain[bool]":
        return self._wrap(pyd.is_increasing)()
    def is_indexed(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_indexed)()
    def is_instance_of(
        self: "Chain[t.Any]", types: t.Union[type, t.Tuple[type, ...]]
    ) -> "Chain[bool]":
        return self._wrap(pyd.is_instance_of)(types)
    def is_integer(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_integer)()
    def is_iterable(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_iterable)()
    def is_json(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_json)()
    def is_list(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_list)()
    def is_match(self: "Chain[t.Any]", source: t.Any) -> "Chain[bool]":
        return self._wrap(pyd.is_match)(source)
    def is_match_with(
        self: "Chain[t.Any]",
        source: t.Any,
        customizer: t.Any = None,
        _key: t.Any = UNSET,
        _obj: t.Any = UNSET,
        _source: t.Any = UNSET,
    ) -> "Chain[bool]":
        return self._wrap(pyd.is_match_with)(source, customizer, _key, _obj, _source)
    def is_monotone(
        self: "Chain[t.Union[T, t.List[T]]]", op: t.Callable[[T, T], t.Any]
    ) -> "Chain[bool]":
        return self._wrap(pyd.is_monotone)(op)
    def is_nan(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_nan)()
    def is_negative(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_negative)()
    def is_none(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_none)()
    def is_number(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_number)()
    def is_object(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_object)()
    def is_odd(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_odd)()
    def is_positive(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_positive)()
    def is_reg_exp(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_reg_exp)()
    def is_set(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_set)()
    def is_strictly_decreasing(
        self: "Chain[t.Union['SupportsRichComparison', t.List['SupportsRichComparison']]]",
    ) -> "Chain[bool]":
        return self._wrap(pyd.is_strictly_decreasing)()
    def is_strictly_increasing(
        self: "Chain[t.Union['SupportsRichComparison', t.List['SupportsRichComparison']]]",
    ) -> "Chain[bool]":
        return self._wrap(pyd.is_strictly_increasing)()
    def is_string(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_string)()
    def is_tuple(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_tuple)()
    def is_zero(self: "Chain[t.Any]") -> "Chain[bool]":
        return self._wrap(pyd.is_zero)()
    def camel_case(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.camel_case)()
    def capitalize(self: "Chain[t.Any]", strict: bool = True) -> "Chain[str]":
        return self._wrap(pyd.capitalize)(strict)
    def chars(self: "Chain[t.Any]") -> "Chain[t.List[str]]":
        return self._wrap(pyd.chars)()
    def chop(self: "Chain[t.Any]", step: int) -> "Chain[t.List[str]]":
        return self._wrap(pyd.chop)(step)
    def chop_right(self: "Chain[t.Any]", step: int) -> "Chain[t.List[str]]":
        return self._wrap(pyd.chop_right)(step)
    def clean(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.clean)()
    def count_substr(self: "Chain[t.Any]", subtext: t.Any) -> "Chain[int]":
        return self._wrap(pyd.count_substr)(subtext)
    def deburr(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.deburr)()
    def decapitalize(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.decapitalize)()
    def ends_with(
        self: "Chain[t.Any]", target: t.Any, position: t.Union[int, None] = None
    ) -> "Chain[bool]":
        return self._wrap(pyd.ends_with)(target, position)
    def ensure_ends_with(self: "Chain[t.Any]", suffix: t.Any) -> "Chain[str]":
        return self._wrap(pyd.ensure_ends_with)(suffix)
    def ensure_starts_with(self: "Chain[t.Any]", prefix: t.Any) -> "Chain[str]":
        return self._wrap(pyd.ensure_starts_with)(prefix)
    def escape(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.escape)()
    def escape_reg_exp(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.escape_reg_exp)()
    def has_substr(self: "Chain[t.Any]", subtext: t.Any) -> "Chain[bool]":
        return self._wrap(pyd.has_substr)(subtext)
    def human_case(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.human_case)()
    def insert_substr(self: "Chain[t.Any]", index: int, subtext: t.Any) -> "Chain[str]":
        return self._wrap(pyd.insert_substr)(index, subtext)
    def join(self: "Chain[t.Iterable[t.Any]]", separator: t.Any = "") -> "Chain[str]":
        return self._wrap(pyd.join)(separator)
    def kebab_case(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.kebab_case)()
    def lines(self: "Chain[t.Any]") -> "Chain[t.List[str]]":
        return self._wrap(pyd.lines)()
    def lower_case(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.lower_case)()
    def lower_first(self: "Chain[str]") -> "Chain[str]":
        return self._wrap(pyd.lower_first)()
    def number_format(
        self: "Chain[NumberT]",
        scale: int = 0,
        decimal_separator: str = ".",
        order_separator: str = ",",
    ) -> "Chain[str]":
        return self._wrap(pyd.number_format)(scale, decimal_separator, order_separator)
    def pad(self: "Chain[t.Any]", length: int, chars: t.Any = " ") -> "Chain[str]":
        return self._wrap(pyd.pad)(length, chars)
    def pad_end(self: "Chain[t.Any]", length: int, chars: t.Any = " ") -> "Chain[str]":
        return self._wrap(pyd.pad_end)(length, chars)
    def pad_start(self: "Chain[t.Any]", length: int, chars: t.Any = " ") -> "Chain[str]":
        return self._wrap(pyd.pad_start)(length, chars)
    def pascal_case(self: "Chain[t.Any]", strict: bool = True) -> "Chain[str]":
        return self._wrap(pyd.pascal_case)(strict)
    def predecessor(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.predecessor)()
    def prune(self: "Chain[t.Any]", length: int = 0, omission: str = "...") -> "Chain[str]":
        return self._wrap(pyd.prune)(length, omission)
    def quote(self: "Chain[t.Any]", quote_char: t.Any = '"') -> "Chain[str]":
        return self._wrap(pyd.quote)(quote_char)
    def reg_exp_js_match(self: "Chain[t.Any]", reg_exp: str) -> "Chain[t.List[str]]":
        return self._wrap(pyd.reg_exp_js_match)(reg_exp)
    def reg_exp_js_replace(
        self: "Chain[t.Any]", reg_exp: str, repl: t.Union[str, t.Callable[[re.Match], str]]
    ) -> "Chain[str]":
        return self._wrap(pyd.reg_exp_js_replace)(reg_exp, repl)
    def reg_exp_replace(
        self: "Chain[t.Any]",
        pattern: t.Any,
        repl: t.Union[str, t.Callable[[re.Match], str]],
        ignore_case: bool = False,
        count: int = 0,
    ) -> "Chain[str]":
        return self._wrap(pyd.reg_exp_replace)(pattern, repl, ignore_case, count)
    def repeat(self: "Chain[t.Any]", n: t.SupportsInt = 0) -> "Chain[str]":
        return self._wrap(pyd.repeat)(n)
    def replace(
        self: "Chain[t.Any]",
        pattern: t.Any,
        repl: t.Union[str, t.Callable[[re.Match], str]],
        ignore_case: bool = False,
        count: int = 0,
        escape: bool = True,
        from_start: bool = False,
        from_end: bool = False,
    ) -> "Chain[str]":
        return self._wrap(pyd.replace)(
            pattern, repl, ignore_case, count, escape, from_start, from_end
        )
    def replace_end(
        self: "Chain[t.Any]",
        pattern: t.Any,
        repl: t.Union[str, t.Callable[[re.Match], str]],
        ignore_case: bool = False,
        escape: bool = True,
    ) -> "Chain[str]":
        return self._wrap(pyd.replace_end)(pattern, repl, ignore_case, escape)
    def replace_start(
        self: "Chain[t.Any]",
        pattern: t.Any,
        repl: t.Union[str, t.Callable[[re.Match], str]],
        ignore_case: bool = False,
        escape: bool = True,
    ) -> "Chain[str]":
        return self._wrap(pyd.replace_start)(pattern, repl, ignore_case, escape)
    def separator_case(self: "Chain[t.Any]", separator: str) -> "Chain[str]":
        return self._wrap(pyd.separator_case)(separator)
    def series_phrase(
        self: "Chain[t.List[t.Any]]",
        separator: t.Any = ", ",
        last_separator: t.Any = " and ",
        serial: bool = False,
    ) -> "Chain[str]":
        return self._wrap(pyd.series_phrase)(separator, last_separator, serial)
    def series_phrase_serial(
        self: "Chain[t.List[t.Any]]", separator: t.Any = ", ", last_separator: t.Any = " and "
    ) -> "Chain[str]":
        return self._wrap(pyd.series_phrase_serial)(separator, last_separator)
    def slugify(self: "Chain[t.Any]", separator: str = "-") -> "Chain[str]":
        return self._wrap(pyd.slugify)(separator)
    def snake_case(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.snake_case)()
    def split(
        self: "Chain[t.Any]", separator: t.Union[str, Unset, None] = UNSET
    ) -> "Chain[t.List[str]]":
        return self._wrap(pyd.split)(separator)
    def start_case(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.start_case)()
    def starts_with(self: "Chain[t.Any]", target: t.Any, position: int = 0) -> "Chain[bool]":
        return self._wrap(pyd.starts_with)(target, position)
    def strip_tags(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.strip_tags)()
    def substr_left(self: "Chain[t.Any]", subtext: str) -> "Chain[str]":
        return self._wrap(pyd.substr_left)(subtext)
    def substr_left_end(self: "Chain[t.Any]", subtext: str) -> "Chain[str]":
        return self._wrap(pyd.substr_left_end)(subtext)
    def substr_right(self: "Chain[t.Any]", subtext: str) -> "Chain[str]":
        return self._wrap(pyd.substr_right)(subtext)
    def substr_right_end(self: "Chain[t.Any]", subtext: str) -> "Chain[str]":
        return self._wrap(pyd.substr_right_end)(subtext)
    def successor(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.successor)()
    def surround(self: "Chain[t.Any]", wrapper: t.Any) -> "Chain[str]":
        return self._wrap(pyd.surround)(wrapper)
    def swap_case(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.swap_case)()
    def title_case(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.title_case)()
    def to_lower(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.to_lower)()
    def to_upper(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.to_upper)()
    def trim(self: "Chain[t.Any]", chars: t.Union[str, None] = None) -> "Chain[str]":
        return self._wrap(pyd.trim)(chars)
    def trim_end(self: "Chain[t.Any]", chars: t.Union[str, None] = None) -> "Chain[str]":
        return self._wrap(pyd.trim_end)(chars)
    def trim_start(self: "Chain[t.Any]", chars: t.Union[str, None] = None) -> "Chain[str]":
        return self._wrap(pyd.trim_start)(chars)
    def truncate(
        self: "Chain[t.Any]",
        length: int = 30,
        omission: str = "...",
        separator: t.Union[str, re.Pattern, None] = None,
    ) -> "Chain[str]":
        return self._wrap(pyd.truncate)(length, omission, separator)
    def unescape(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.unescape)()
    def upper_case(self: "Chain[t.Any]") -> "Chain[str]":
        return self._wrap(pyd.upper_case)()
    def upper_first(self: "Chain[str]") -> "Chain[str]":
        return self._wrap(pyd.upper_first)()
    def unquote(self: "Chain[t.Any]", quote_char: t.Any = '"') -> "Chain[str]":
        return self._wrap(pyd.unquote)(quote_char)
    def url(self: "Chain[t.Any]", *paths: t.Any, **params: t.Any) -> "Chain[str]":
        return self._wrap(pyd.url)(*paths, **params)
    def words(self: "Chain[t.Any]", pattern: t.Union[str, None] = None) -> "Chain[t.List[str]]":
        return self._wrap(pyd.words)(pattern)
    def attempt(
        self: "Chain[t.Callable[P, T]]", *args: "P.args", **kwargs: "P.kwargs"
    ) -> "Chain[t.Union[T, Exception]]":
        return self._wrap(pyd.attempt)(*args, **kwargs)
    @t.overload
    def cond(
        self: "Chain[t.List[t.Tuple[t.Callable[P, t.Any], t.Callable[P, T]]]]",
        *extra_pairs: t.Tuple[t.Callable[P, t.Any], t.Callable[P, T]]
    ) -> "Chain[t.Callable[P, T]]": ...
    @t.overload
    def cond(
        self: "Chain[t.List[t.List[t.Callable[P, t.Any]]]]",
        *extra_pairs: t.List[t.Callable[P, t.Any]]
    ) -> "Chain[t.Callable[P, t.Any]]": ...
    def cond(self, *extra_pairs):
        return self._wrap(pyd.cond)(*extra_pairs)
    @t.overload
    def conforms(
        self: "Chain[t.Dict[T, t.Callable[[T2], t.Any]]]",
    ) -> "Chain[t.Callable[[t.Dict[T, T2]], bool]]": ...
    @t.overload
    def conforms(
        self: "Chain[t.List[t.Callable[[T], t.Any]]]",
    ) -> "Chain[t.Callable[[t.List[T]], bool]]": ...
    def conforms(self: "Chain[t.Union[t.List, t.Dict]]") -> "Chain[t.Callable]":
        return self._wrap(pyd.conforms)()
    @t.overload
    def conforms_to(
        self: "Chain[t.Dict[T, T2]]", source: t.Dict[T, t.Callable[[T2], t.Any]]
    ) -> "Chain[bool]": ...
    @t.overload
    def conforms_to(
        self: "Chain[t.List[T]]", source: t.List[t.Callable[[T], t.Any]]
    ) -> "Chain[bool]": ...
    def conforms_to(self, source):
        return self._wrap(pyd.conforms_to)(source)
    def constant(self: "Chain[T]") -> "Chain[t.Callable[..., T]]":
        return self._wrap(pyd.constant)()
    def default_to(self: "Chain[t.Union[T, None]]", default_value: T2) -> "Chain[t.Union[T, T2]]":
        return self._wrap(pyd.default_to)(default_value)
    @t.overload
    def default_to_any(self: "Chain[None]", *default_values: None) -> "Chain[None]": ...
    @t.overload
    def default_to_any(
        self: "Chain[t.Union[T, None]]", default_value1: None, default_value2: T2
    ) -> "Chain[t.Union[T, T2]]": ...
    @t.overload
    def default_to_any(
        self: "Chain[t.Union[T, None]]",
        default_value1: None,
        default_value2: None,
        default_value3: T2,
    ) -> "Chain[t.Union[T, T2]]": ...
    @t.overload
    def default_to_any(
        self: "Chain[t.Union[T, None]]",
        default_value1: None,
        default_value2: None,
        default_value3: None,
        default_value4: T2,
    ) -> "Chain[t.Union[T, T2]]": ...
    @t.overload
    def default_to_any(
        self: "Chain[t.Union[T, None]]",
        default_value1: None,
        default_value2: None,
        default_value3: None,
        default_value4: None,
        default_value5: T2,
    ) -> "Chain[t.Union[T, T2]]": ...
    @t.overload
    def default_to_any(
        self: "Chain[t.Union[T, None]]", *default_values: T2
    ) -> "Chain[t.Union[T, T2]]": ...
    def default_to_any(self, *default_values):
        return self._wrap(pyd.default_to_any)(*default_values)
    @t.overload
    def identity(self: "Chain[T]", *args: t.Any) -> "Chain[T]": ...
    @t.overload
    def iteratee(self: "Chain[t.Callable[P, T]]") -> "Chain[t.Callable[P, T]]": ...
    @t.overload
    def iteratee(self: "Chain[t.Any]") -> "Chain[t.Callable]": ...
    def iteratee(self):
        return self._wrap(pyd.iteratee)()
    def matches(self: "Chain[t.Any]") -> "Chain[t.Callable[[t.Any], bool]]":
        return self._wrap(pyd.matches)()
    def matches_property(self: "Chain[t.Any]", value: t.Any) -> "Chain[t.Callable[[t.Any], bool]]":
        return self._wrap(pyd.matches_property)(value)
    @t.overload
    def memoize(
        self: "Chain[t.Callable[P, T]]", resolver: None = None
    ) -> "Chain[MemoizedFunc[P, T, str]]": ...
    @t.overload
    def memoize(
        self: "Chain[t.Callable[P, T]]", resolver: t.Union[t.Callable[P, T2], None] = None
    ) -> "Chain[MemoizedFunc[P, T, T2]]": ...
    def memoize(self, resolver=None):
        return self._wrap(pyd.memoize)(resolver)
    def method(
        self: "Chain[PathT]", *args: t.Any, **kwargs: t.Any
    ) -> "Chain[t.Callable[..., t.Any]]":
        return self._wrap(pyd.method)(*args, **kwargs)
    def method_of(
        self: "Chain[t.Any]", *args: t.Any, **kwargs: t.Any
    ) -> "Chain[t.Callable[..., t.Any]]":
        return self._wrap(pyd.method_of)(*args, **kwargs)
    def noop(self: "Chain[t.Any]", *args: t.Any, **kwargs: t.Any) -> "Chain[None]":
        return self._wrap(pyd.noop)(*args, **kwargs)
    def over(self: "Chain[t.Iterable[t.Callable[P, T]]]") -> "Chain[t.Callable[P, t.List[T]]]":
        return self._wrap(pyd.over)()
    def over_every(self: "Chain[t.Iterable[t.Callable[P, t.Any]]]") -> "Chain[t.Callable[P, bool]]":
        return self._wrap(pyd.over_every)()
    def over_some(self: "Chain[t.Iterable[t.Callable[P, t.Any]]]") -> "Chain[t.Callable[P, bool]]":
        return self._wrap(pyd.over_some)()
    def property_(self: "Chain[PathT]") -> "Chain[t.Callable[[t.Any], t.Any]]":
        return self._wrap(pyd.property_)()
    property = property_

    def properties(self: "Chain[t.Any]", *paths: t.Any) -> "Chain[t.Callable[[t.Any], t.Any]]":
        return self._wrap(pyd.properties)(*paths)
    def property_of(self: "Chain[t.Any]") -> "Chain[t.Callable[[PathT], t.Any]]":
        return self._wrap(pyd.property_of)()
    @t.overload
    def random(
        self: "Chain[int]", stop: int = 1, *, floating: Literal[False] = False
    ) -> "Chain[int]": ...
    @t.overload
    def random(self: "Chain[float]", stop: int = 1, floating: bool = False) -> "Chain[float]": ...
    @t.overload
    def random(self: "Chain[float]", stop: float, floating: bool = False) -> "Chain[float]": ...
    @t.overload
    def random(
        self: "Chain[t.Union[float, int]]",
        stop: t.Union[float, int] = 1,
        *,
        floating: Literal[True]
    ) -> "Chain[float]": ...
    def random(
        self: "Chain[t.Union[float, int]]", stop: t.Union[float, int] = 1, floating: bool = False
    ):
        return self._wrap(pyd.random)(stop, floating)
    @t.overload
    def range_(self: "Chain[int]") -> "Chain[t.Generator[int, None, None]]": ...
    @t.overload
    def range_(
        self: "Chain[int]", stop: int, step: int = 1
    ) -> "Chain[t.Generator[int, None, None]]": ...
    def range_(self, *args):
        return self._wrap(pyd.range_)(*args)
    range = range_

    @t.overload
    def range_right(self: "Chain[int]") -> "Chain[t.Generator[int, None, None]]": ...
    @t.overload
    def range_right(
        self: "Chain[int]", stop: int, step: int = 1
    ) -> "Chain[t.Generator[int, None, None]]": ...
    def range_right(self, *args):
        return self._wrap(pyd.range_right)(*args)
    @t.overload
    def result(self: "Chain[None]", key: t.Any, default: None = None) -> "Chain[None]": ...
    @t.overload
    def result(self: "Chain[None]", key: t.Any, default: T) -> "Chain[T]": ...
    @t.overload
    def result(self: "Chain[t.Any]", key: t.Any, default: t.Any = None) -> "Chain[t.Any]": ...
    def result(self, key, default=None):
        return self._wrap(pyd.result)(key, default)
    def retry(
        self: "Chain[int]",
        delay: t.Union[int, float] = 0.5,
        max_delay: t.Union[int, float] = 150.0,
        scale: t.Union[int, float] = 2.0,
        jitter: t.Union[int, float, t.Tuple[t.Union[int, float], t.Union[int, float]]] = 0,
        exceptions: t.Iterable[Type[Exception]] = (Exception,),
        on_exception: t.Union[t.Callable[[Exception, int], t.Any], None] = None,
    ) -> "Chain[t.Callable[[CallableT], CallableT]]":
        return self._wrap(pyd.retry)(delay, max_delay, scale, jitter, exceptions, on_exception)
    @t.overload
    def times(self: "Chain[int]", iteratee: t.Callable[..., T]) -> "Chain[t.List[T]]": ...
    @t.overload
    def times(self: "Chain[int]", iteratee: None = None) -> "Chain[t.List[int]]": ...
    def times(self: "Chain[int]", iteratee=None):
        return self._wrap(pyd.times)(iteratee)
    def to_path(self: "Chain[PathT]") -> "Chain[t.List[t.Hashable]]":
        return self._wrap(pyd.to_path)()
