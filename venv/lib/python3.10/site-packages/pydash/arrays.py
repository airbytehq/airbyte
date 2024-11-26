"""
Functions that operate on lists.

.. versionadded:: 1.0.0
"""

from bisect import bisect_left, bisect_right
from functools import cmp_to_key
from math import ceil
import typing as t

import pydash as pyd

from .helpers import base_get, iteriteratee, parse_iteratee
from .types import IterateeObjT


if t.TYPE_CHECKING:
    from _typeshed import SupportsRichComparisonT  # pragma: no cover


__all__ = (
    "chunk",
    "compact",
    "concat",
    "difference",
    "difference_by",
    "difference_with",
    "drop",
    "drop_right",
    "drop_right_while",
    "drop_while",
    "duplicates",
    "fill",
    "find_index",
    "find_last_index",
    "flatten",
    "flatten_deep",
    "flatten_depth",
    "from_pairs",
    "head",
    "index_of",
    "initial",
    "intercalate",
    "interleave",
    "intersection",
    "intersection_by",
    "intersection_with",
    "intersperse",
    "last",
    "last_index_of",
    "mapcat",
    "nth",
    "pull",
    "pull_all",
    "pull_all_by",
    "pull_all_with",
    "pull_at",
    "push",
    "remove",
    "reverse",
    "shift",
    "slice_",
    "sort",
    "sorted_index",
    "sorted_index_by",
    "sorted_index_of",
    "sorted_last_index",
    "sorted_last_index_by",
    "sorted_last_index_of",
    "sorted_uniq",
    "sorted_uniq_by",
    "splice",
    "split_at",
    "tail",
    "take",
    "take_right",
    "take_right_while",
    "take_while",
    "union",
    "union_by",
    "union_with",
    "uniq",
    "uniq_by",
    "uniq_with",
    "unshift",
    "unzip",
    "unzip_with",
    "without",
    "xor",
    "xor_by",
    "xor_with",
    "zip_",
    "zip_object",
    "zip_object_deep",
    "zip_with",
)

T = t.TypeVar("T")
T2 = t.TypeVar("T2")
SequenceT = t.TypeVar("SequenceT", bound=t.Sequence)
MutableSequenceT = t.TypeVar("MutableSequenceT", bound=t.MutableSequence)


def chunk(array: t.Sequence[T], size: int = 1) -> t.List[t.Sequence[T]]:
    """
    Creates a list of elements split into groups the length of `size`. If `array` can't be split
    evenly, the final chunk will be the remaining elements.

    Args:
        array: List to chunk.
        size: Chunk size. Defaults to ``1``.

    Returns:
        New list containing chunks of `array`.

    Example:

        >>> chunk([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]

    .. versionadded:: 1.1.0
    """
    chunks = int(ceil(len(array) / float(size)))
    return [array[i * size : (i + 1) * size] for i in range(chunks)]


def compact(array: t.Iterable[t.Union[T, None]]) -> t.List[T]:
    """
    Creates a list with all falsey values of array removed.

    Args:
        array: List to compact.

    Returns:
        Compacted list.

    Example:

        >>> compact(['', 1, 0, True, False, None])
        [1, True]

    .. versionadded:: 1.0.0
    """
    return [item for item in array if item]


def concat(*arrays: t.Iterable[T]) -> t.List[T]:
    """
    Concatenates zero or more lists into one.

    Args:
        arrays: Lists to concatenate.

    Returns:
        Concatenated list.

    Example:

        >>> concat([1, 2], [3, 4], [[5], [6]])
        [1, 2, 3, 4, [5], [6]]

    .. versionadded:: 2.0.0

    .. versionchanged:: 4.0.0
        Renamed from ``cat`` to ``concat``.
    """
    return flatten(arrays)


def difference(array: t.Iterable[T], *others: t.Iterable[T]) -> t.List[T]:
    """
    Creates a list of list elements not present in others.

    Args:
        array: List to process.
        others: Lists to check.

    Returns:
        Difference between `others`.

    Example:

        >>> difference([1, 2, 3], [1], [2])
        [3]

    .. versionadded:: 1.0.0
    """
    return difference_with(array, *others)


@t.overload
def difference_by(
    array: t.Iterable[T],
    *others: t.Iterable[T],
    iteratee: t.Union[IterateeObjT, t.Callable[[T], t.Any], None],
) -> t.List[T]:
    ...


@t.overload
def difference_by(
    array: t.Iterable[T], *others: t.Union[IterateeObjT, t.Iterable[T], t.Callable[[T], t.Any]]
) -> t.List[T]:
    ...


def difference_by(array, *others, **kwargs):
    """
    This method is like :func:`difference` except that it accepts an iteratee which is invoked for
    each element of each array to generate the criterion by which they're compared. The order and
    references of result values are determined by `array`. The iteratee is invoked with one
    argument: ``(value)``.

    Args:
        array: The array to find the difference of.
        others: Lists to check for difference with `array`.

    Keyword Args:
        iteratee: Function to transform the elements of the arrays. Defaults to
            :func:`.identity`.

    Returns:
        Difference between `others`.

    Example:

        >>> difference_by([1.2, 1.5, 1.7, 2.8], [0.9, 3.2], round)
        [1.5, 1.7]

    .. versionadded:: 4.0.0
    """
    array = array[:]

    if not others:
        return array

    # Check if last other is a potential iteratee.
    iteratee, others = parse_iteratee("iteratee", *others, **kwargs)

    for other in others:
        if not other:
            continue
        array = list(iterdifference(array, other, iteratee=iteratee))

    return array


@t.overload
def difference_with(
    array: t.Iterable[T],
    *others: t.Iterable[T2],
    comparator: t.Union[t.Callable[[T, T2], t.Any], None],
) -> t.List[T]:
    ...


@t.overload
def difference_with(
    array: t.Iterable[T], *others: t.Union[t.Iterable[T2], t.Callable[[T, T2], t.Any]]
) -> t.List[T]:
    ...


def difference_with(array, *others, **kwargs):
    """
    This method is like :func:`difference` except that it accepts a comparator which is invoked to
    compare the elements of all arrays. The order and references of result values are determined by
    the first array. The comparator is invoked with two arguments: ``(arr_val, oth_val)``.

    Args:
        array: The array to find the difference of.
        others: Lists to check for difference with `array`.

    Keyword Args:
        comparator: Function to compare the elements of the arrays. Defaults to
            :func:`.is_equal`.

    Returns:
        Difference between `others`.

    Example:

        >>> array = ['apple', 'banana', 'pear']
        >>> others = (['avocado', 'pumpkin'], ['peach'])
        >>> comparator = lambda a, b: a[0] == b[0]
        >>> difference_with(array, *others, comparator=comparator)
        ['banana']

    .. versionadded:: 4.0.0
    """
    array = array[:]

    if not others:
        return array

    comparator = kwargs.get("comparator")
    last_other = others[-1]

    # Check if last other is a comparator.
    if comparator is None and (callable(last_other) or last_other is None):
        comparator = last_other
        others = others[:-1]

    for other in others:
        if not other:
            continue
        array = list(iterdifference(array, other, comparator=comparator))

    return array


def drop(array: t.Sequence[T], n: int = 1) -> t.List[T]:
    """
    Creates a slice of `array` with `n` elements dropped from the beginning.

    Args:
        array: List to process.
        n: Number of elements to drop. Defaults to ``1``.

    Returns:
        Dropped list.

    Example:

        >>> drop([1, 2, 3, 4], 2)
        [3, 4]

    .. versionadded:: 1.0.0

    .. versionchanged:: 1.1.0
        Added ``n`` argument and removed as alias of :func:`rest`.

    .. versionchanged:: 3.0.0
        Made ``n`` default to ``1``.
    """
    return drop_while(array, lambda _, index: index < n)


def drop_right(array: t.Sequence[T], n: int = 1) -> t.List[T]:
    """
    Creates a slice of `array` with `n` elements dropped from the end.

    Args:
        array: List to process.
        n: Number of elements to drop. Defaults to ``1``.

    Returns:
        Dropped list.

    Example:

        >>> drop_right([1, 2, 3, 4], 2)
        [1, 2]

    .. versionadded:: 1.1.0

    .. versionchanged:: 3.0.0
        Made ``n`` default to ``1``.
    """
    length = len(array)
    return drop_right_while(array, lambda _, index: (length - index) <= n)


@t.overload
def drop_right_while(
    array: t.Sequence[T], predicate: t.Callable[[T, int, t.List[T]], t.Any]
) -> t.List[T]:
    ...


@t.overload
def drop_right_while(array: t.Sequence[T], predicate: t.Callable[[T, int], t.Any]) -> t.List[T]:
    ...


@t.overload
def drop_right_while(array: t.Sequence[T], predicate: t.Callable[[T], t.Any]) -> t.List[T]:
    ...


@t.overload
def drop_right_while(array: t.Sequence[T], predicate: None = None) -> t.List[T]:
    ...


def drop_right_while(array, predicate=None):
    """
    Creates a slice of `array` excluding elements dropped from the end. Elements are dropped until
    the `predicate` returns falsey. The `predicate` is invoked with three arguments: ``(value,
    index, array)``.

    Args:
        array: List to process.
        predicate: Predicate called per iteration

    Returns:
        Dropped list.

    Example:

        >>> drop_right_while([1, 2, 3, 4], lambda x: x >= 3)
        [1, 2]

    .. versionadded:: 1.1.0
    """
    n = len(array)
    for is_true, _, _, _ in iteriteratee(array, predicate, reverse=True):
        if is_true:
            n -= 1
        else:
            break

    return array[:n]


@t.overload
def drop_while(
    array: t.Sequence[T], predicate: t.Callable[[T, int, t.List[T]], t.Any]
) -> t.List[T]:
    ...


@t.overload
def drop_while(array: t.Sequence[T], predicate: t.Callable[[T, int], t.Any]) -> t.List[T]:
    ...


@t.overload
def drop_while(array: t.Sequence[T], predicate: t.Callable[[T], t.Any]) -> t.List[T]:
    ...


@t.overload
def drop_while(array: t.Sequence[T], predicate: None = None) -> t.List[T]:
    ...


def drop_while(array, predicate=None):
    """
    Creates a slice of `array` excluding elements dropped from the beginning. Elements are dropped
    until the `predicate` returns falsey. The `predicate` is invoked with three arguments: ``(value,
    index, array)``.

    Args:
        array: List to process.
        predicate: Predicate called per iteration

    Returns:
        Dropped list.

    Example:

        >>> drop_while([1, 2, 3, 4], lambda x: x < 3)
        [3, 4]

    .. versionadded:: 1.1.0
    """
    n = 0
    for is_true, _, _, _ in iteriteratee(array, predicate):
        if is_true:
            n += 1
        else:
            break

    return array[n:]


def duplicates(
    array: t.Sequence[T], iteratee: t.Union[t.Callable[[T], t.Any], IterateeObjT, None] = None
) -> t.List[T]:
    """
    Creates a unique list of duplicate values from `array`. If iteratee is passed, each element of
    array is passed through an iteratee before duplicates are computed. The iteratee is invoked with
    three arguments: ``(value, index, array)``. If an object path is passed for iteratee, the
    created iteratee will return the path value of the given element. If an object is passed for
    iteratee, the created filter style iteratee will return ``True`` for elements that have the
    properties of the given object, else ``False``.

    Args:
        array: List to process.
        iteratee: Iteratee applied per iteration.

    Returns:
        List of duplicates.

    Example:

        >>> duplicates([0, 1, 3, 2, 3, 1])
        [3, 1]

    .. versionadded:: 3.0.0
    """
    if iteratee:
        cbk = pyd.iteratee(iteratee)
        computed = [cbk(item) for item in array]
    else:
        computed = array  # type: ignore

    # NOTE: Using array[i] instead of item since iteratee could have modified
    # returned item values.
    lst = uniq(array[i] for i, _ in iterduplicates(computed))

    return lst


def fill(
    array: t.Sequence[T], value: T2, start: int = 0, end: t.Union[int, None] = None
) -> t.List[t.Union[T, T2]]:
    """
    Fills elements of array with value from `start` up to, but not including, `end`.

    Args:
        array: List to fill.
        value: Value to fill with.
        start: Index to start filling. Defaults to ``0``.
        end: Index to end filling. Defaults to ``len(array)``.

    Returns:
        Filled `array`.

    Example:

        >>> fill([1, 2, 3, 4, 5], 0)
        [0, 0, 0, 0, 0]
        >>> fill([1, 2, 3, 4, 5], 0, 1, 3)
        [1, 0, 0, 4, 5]
        >>> fill([1, 2, 3, 4, 5], 0, 0, 100)
        [0, 0, 0, 0, 0]

    Warning:
        `array` is modified in place.

    .. versionadded:: 3.1.0
    """
    if end is None:
        end = len(array)
    else:
        end = min(end, len(array))

    # Use this style of assignment so that `array` is mutated.
    array[:] = array[:start] + [value] * len(array[start:end]) + array[end:]  # type: ignore
    return array  # type: ignore


@t.overload
def find_index(array: t.Iterable[T], predicate: t.Callable[[T, int, t.List[T]], t.Any]) -> int:
    ...


@t.overload
def find_index(array: t.Iterable[T], predicate: t.Callable[[T, int], t.Any]) -> int:
    ...


@t.overload
def find_index(array: t.Iterable[T], predicate: t.Callable[[T], t.Any]) -> int:
    ...


@t.overload
def find_index(array: t.Iterable[t.Any], predicate: IterateeObjT) -> int:
    ...


@t.overload
def find_index(array: t.Iterable[t.Any], predicate: None = None) -> int:
    ...


def find_index(array, predicate=None):
    """
    This method is similar to :func:`pydash.collections.find`, except that it returns the index of
    the element that passes the predicate check, instead of the element itself.

    Args:
        array: List to process.
        predicate: Predicate applied per iteration.

    Returns:
        Index of found item or ``-1`` if not found.

    Example:

        >>> find_index([1, 2, 3, 4], lambda x: x >= 3)
        2
        >>> find_index([1, 2, 3, 4], lambda x: x > 4)
        -1

    .. versionadded:: 1.0.0
    """
    search = (i for is_true, _, i, _ in iteriteratee(array, predicate) if is_true)
    return next(search, -1)


@t.overload
def find_last_index(array: t.Iterable[T], predicate: t.Callable[[T, int, t.List[T]], t.Any]) -> int:
    ...


@t.overload
def find_last_index(array: t.Iterable[T], predicate: t.Callable[[T, int], t.Any]) -> int:
    ...


@t.overload
def find_last_index(array: t.Iterable[T], predicate: t.Callable[[T], t.Any]) -> int:
    ...


@t.overload
def find_last_index(array: t.Iterable[t.Any], predicate: IterateeObjT) -> int:
    ...


@t.overload
def find_last_index(array: t.Iterable[t.Any], predicate: None = None) -> int:
    ...


def find_last_index(array, predicate=None):
    """
    This method is similar to :func:`find_index`, except that it iterates over elements from right
    to left.

    Args:
        array: List to process.
        predicate: Predicate applied per iteration.

    Returns:
        Index of found item or ``-1`` if not found.

    Example:

        >>> find_last_index([1, 2, 3, 4], lambda x: x >= 3)
        3
        >>> find_last_index([1, 2, 3, 4], lambda x: x > 4)
        -1

    .. versionadded:: 1.0.0
    """
    search = (i for is_true, _, i, _ in iteriteratee(array, predicate, reverse=True) if is_true)
    return next(search, -1)


@t.overload
def flatten(array: t.Iterable[t.Iterable[T]]) -> t.List[T]:
    ...


@t.overload
def flatten(array: t.Iterable[T]) -> t.List[T]:
    ...


def flatten(array):
    """
    Flattens array a single level deep.

    Args:
        array: List to flatten.

    Returns:
        Flattened list.

    Example:

        >>> flatten([[1], [2, [3]], [[4]]])
        [1, 2, [3], [4]]


    .. versionadded:: 1.0.0

    .. versionchanged:: 2.0.0
        Removed `callback` option. Added ``is_deep`` option. Made it shallow
        by default.

    .. versionchanged:: 4.0.0
        Removed ``is_deep`` option. Use :func:`flatten_deep` instead.
    """
    return flatten_depth(array, depth=1)


def flatten_deep(array: t.Iterable) -> t.List:
    """
    Flattens an array recursively.

    Args:
        array: List to flatten.

    Returns:
        Flattened list.

    Example:

        >>> flatten_deep([[1], [2, [3]], [[4]]])
        [1, 2, 3, 4]

    .. versionadded:: 2.0.0
    """
    return flatten_depth(array, depth=-1)


def flatten_depth(array: t.Iterable, depth: int = 1) -> t.List:
    """
    Recursively flatten `array` up to `depth` times.

    Args:
        array: List to flatten.
        depth: Depth to flatten to. Defaults to ``1``.

    Returns:
        Flattened list.

    Example:

        >>> flatten_depth([[[1], [2, [3]], [[4]]]], 1)
        [[1], [2, [3]], [[4]]]
        >>> flatten_depth([[[1], [2, [3]], [[4]]]], 2)
        [1, 2, [3], [4]]
        >>> flatten_depth([[[1], [2, [3]], [[4]]]], 3)
        [1, 2, 3, 4]
        >>> flatten_depth([[[1], [2, [3]], [[4]]]], 4)
        [1, 2, 3, 4]

    .. versionadded:: 4.0.0
    """
    return list(iterflatten(array, depth=depth))


@t.overload
def from_pairs(pairs: t.Iterable[t.Tuple[T, T2]]) -> t.Dict[T, T2]:
    ...


@t.overload
def from_pairs(pairs: t.Iterable[t.List[t.Union[T, T2]]]) -> t.Dict[t.Union[T, T2], t.Union[T, T2]]:
    ...


def from_pairs(pairs):
    """
    Returns a dict from the given list of pairs.

    Args:
        pairs: List of key-value pairs.

    Returns:
        dict

    Example:

        >>> from_pairs([['a', 1], ['b', 2]]) == {'a': 1, 'b': 2}
        True

    .. versionadded:: 4.0.0
    """
    return dict(pairs)


def head(array: t.Sequence[T]) -> t.Union[T, None]:
    """
    Return the first element of `array`.

    Args:
        array: List to process.

    Returns:
        First element of list.

    Example:

        >>> head([1, 2, 3, 4])
        1

    .. versionadded:: 1.0.0

    .. versionchanged::
        Renamed from ``first`` to ``head``.
    """
    return base_get(array, 0, default=None)


def index_of(array: t.Sequence[T], value: T, from_index: int = 0) -> int:
    """
    Gets the index at which the first occurrence of value is found.

    Args:
        array: List to search.
        value: Value to search for.
        from_index: Index to search from.

    Returns:
        Index of found item or ``-1`` if not found.

    Example:

        >>> index_of([1, 2, 3, 4], 2)
        1
        >>> index_of([2, 1, 2, 3], 2, from_index=1)
        2

    .. versionadded:: 1.0.0
    """
    try:
        return array.index(value, from_index)
    except ValueError:
        return -1


def initial(array: t.Sequence[T]) -> t.Sequence[T]:
    """
    Return all but the last element of `array`.

    Args:
        array: List to process.

    Returns:
        Initial part of `array`.

    Example:

        >>> initial([1, 2, 3, 4])
        [1, 2, 3]

    .. versionadded:: 1.0.0
    """
    return array[:-1]


@t.overload
def intercalate(array: t.Iterable[t.Iterable[T]], separator: T2) -> t.List[t.Union[T, T2]]:
    ...


@t.overload
def intercalate(array: t.Iterable[T], separator: T2) -> t.List[t.Union[T, T2]]:
    ...


def intercalate(array, separator):
    """
    Like :func:`intersperse` for lists of lists but shallowly flattening the result.

    Args:
        array: List to intercalate.
        separator: Element to insert.

    Returns:
        Intercalated list.

    Example:

        >>> intercalate([1, [2], [3], 4], 'x')
        [1, 'x', 2, 'x', 3, 'x', 4]


    .. versionadded:: 2.0.0
    """
    return flatten(intersperse(array, separator))


def interleave(*arrays: t.Iterable[T]) -> t.List[T]:
    """
    Merge multiple lists into a single list by inserting the next element of each list by sequential
    round-robin into the new list.

    Args:
        arrays: Lists to interleave.

    Returns:
        Interleaved list.

    Example:

        >>> interleave([1, 2, 3], [4, 5, 6], [7, 8, 9])
        [1, 4, 7, 2, 5, 8, 3, 6, 9]

    .. versionadded:: 2.0.0
    """
    return list(iterinterleave(*arrays))


def intersection(array: t.Sequence[T], *others: t.Iterable[t.Any]) -> t.List[T]:
    """
    Computes the intersection of all the passed-in arrays.

    Args:
        array: The array to find the intersection of.
        others: Lists to check for intersection with `array`.

    Returns:
        Intersection of provided lists.

    Example:

        >>> intersection([1, 2, 3], [1, 2, 3, 4, 5], [2, 3])
        [2, 3]

        >>> intersection([1, 2, 3])
        [1, 2, 3]

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Support finding intersection of unhashable types.
    """
    return intersection_with(array, *others)


@t.overload
def intersection_by(
    array: t.Sequence[T],
    *others: t.Iterable[t.Any],
    iteratee: t.Union[t.Callable[[T], t.Any], IterateeObjT],
) -> t.List[T]:
    ...


@t.overload
def intersection_by(
    array: t.Sequence[T], *others: t.Union[t.Iterable[t.Any], t.Callable[[T], t.Any], IterateeObjT]
) -> t.List[T]:
    ...


def intersection_by(array, *others, **kwargs):
    """
    This method is like :func:`intersection` except that it accepts an iteratee which is invoked for
    each element of each array to generate the criterion by which they're compared. The order and
    references of result values are determined by `array`. The iteratee is invoked with one
    argument: ``(value)``.

    Args:
        array: The array to find the intersection of.
        others: Lists to check for intersection with `array`.

    Keyword Args:
        iteratee: Function to transform the elements of the arrays. Defaults to
            :func:`.identity`.

    Returns:
        Intersection of provided lists.

    Example:

        >>> intersection_by([1.2, 1.5, 1.7, 2.8], [0.9, 3.2], round)
        [1.2, 2.8]

    .. versionadded:: 4.0.0
    """
    array = array[:]

    if not others:
        return array

    iteratee, others = parse_iteratee("iteratee", *others, **kwargs)

    # Sort by smallest list length to make intersection faster.
    others = sorted(others, key=lambda other: len(other))

    for other in others:
        array = list(iterintersection(array, other, iteratee=iteratee))
        if not array:
            break

    return array


@t.overload
def intersection_with(
    array: t.Sequence[T], *others: t.Iterable[T2], comparator: t.Callable[[T, T2], t.Any]
) -> t.List[T]:
    ...


@t.overload
def intersection_with(
    array: t.Sequence[T], *others: t.Union[t.Iterable[T2], t.Callable[[T, T2], t.Any]]
) -> t.List[T]:
    ...


def intersection_with(array, *others, **kwargs):
    """
    This method is like :func:`intersection` except that it accepts a comparator which is invoked to
    compare the elements of all arrays. The order and references of result values are determined by
    the first array. The comparator is invoked with two arguments: ``(arr_val, oth_val)``.

    Args:
        array: The array to find the intersection of.
        others: Lists to check for intersection with `array`.

    Keyword Args:
        comparator: Function to compare the elements of the arrays. Defaults to
            :func:`.is_equal`.

    Returns:
        Intersection of provided lists.

    Example:

        >>> array = ['apple', 'banana', 'pear']
        >>> others = (['avocado', 'pumpkin'], ['peach'])
        >>> comparator = lambda a, b: a[0] == b[0]
        >>> intersection_with(array, *others, comparator=comparator)
        ['pear']

    .. versionadded:: 4.0.0
    """
    array = array[:]

    if not others:
        return array

    comparator, others = parse_iteratee("comparator", *others, **kwargs)

    # Sort by smallest list length to reduce to intersection faster.
    others = sorted(others, key=lambda other: len(other))

    for other in others:
        array = list(iterintersection(array, other, comparator=comparator))
        if not array:
            break

    return array


def intersperse(array: t.Iterable[T], separator: T2) -> t.List[t.Union[T, T2]]:
    """
    Insert a separating element between the elements of `array`.

    Args:
        array: List to intersperse.
        separator: Element to insert.

    Returns:
        Interspersed list.

    Example:

        >>> intersperse([1, [2], [3], 4], 'x')
        [1, 'x', [2], 'x', [3], 'x', 4]

    .. versionadded:: 2.0.0
    """
    return list(iterintersperse(array, separator))


def last(array: t.Sequence[T]) -> t.Union[T, None]:
    """
    Return the last element of `array`.

    Args:
        array: List to process.

    Returns:
        Last part of `array`.

    Example:

        >>> last([1, 2, 3, 4])
        4

    .. versionadded:: 1.0.0
    """
    return base_get(array, -1, default=None)


def last_index_of(
    array: t.Sequence[t.Any], value: t.Any, from_index: t.Union[int, None] = None
) -> int:
    """
    Gets the index at which the last occurrence of value is found.

    Args:
        array: List to search.
        value: Value to search for.
        from_index: Index to search from.

    Returns:
        Index of found item or ``-1`` if not found.

    Example:

        >>> last_index_of([1, 2, 2, 4], 2)
        2
        >>> last_index_of([1, 2, 2, 4], 2, from_index=1)
        1

    .. versionadded:: 1.0.0
    """
    index = array_len = len(array)

    try:
        # safe as we are catching any type errors
        from_index = int(from_index)  # type: ignore
    except (TypeError, ValueError):
        pass
    else:
        # Set starting index base on from_index offset.
        index = max(0, index + from_index) if from_index < 0 else min(from_index, index - 1)

    while index:
        if index < array_len and array[index] == value:
            return index
        index -= 1
    return -1


@t.overload
def mapcat(
    array: t.Iterable[T],
    iteratee: t.Callable[[T, int, t.List[T]], t.Union[t.List[T2], t.List[t.List[T2]]]],
) -> t.List[T2]:
    ...


@t.overload
def mapcat(array: t.Iterable[T], iteratee: t.Callable[[T, int, t.List[T]], T2]) -> t.List[T2]:
    ...


@t.overload
def mapcat(
    array: t.Iterable[T], iteratee: t.Callable[[T, int], t.Union[t.List[T2], t.List[t.List[T2]]]]
) -> t.List[T2]:
    ...


@t.overload
def mapcat(array: t.Iterable[T], iteratee: t.Callable[[T, int], T2]) -> t.List[T2]:
    ...


@t.overload
def mapcat(
    array: t.Iterable[T], iteratee: t.Callable[[T], t.Union[t.List[T2], t.List[t.List[T2]]]]
) -> t.List[T2]:
    ...


@t.overload
def mapcat(array: t.Iterable[T], iteratee: t.Callable[[T], T2]) -> t.List[T2]:
    ...


@t.overload
def mapcat(
    array: t.Iterable[t.Union[t.List[T], t.List[t.List[T]]]], iteratee: None = None
) -> t.List[t.Union[T, t.List[T]]]:
    ...


def mapcat(array, iteratee=None):
    """
    Map an iteratee to each element of a list and concatenate the results into a single list using
    :func:`concat`.

    Args:
        array: List to map and concatenate.
        iteratee: Iteratee to apply to each element.

    Returns:
        Mapped and concatenated list.

    Example:

        >>> mapcat(range(4), lambda x: list(range(x)))
        [0, 0, 1, 0, 1, 2]

    .. versionadded:: 2.0.0
    """
    return concat(*pyd.map_(array, iteratee))


def nth(array: t.Iterable[T], pos: int = 0) -> t.Union[T, None]:
    """
    Gets the element at index n of array.

    Args:
        array: List passed in by the user.
        pos: Index of element to return.

    Returns:
        Returns the element at :attr:`pos`.

    Example:

        >>> nth([1, 2, 3], 0)
        1
        >>> nth([3, 4, 5, 6], 2)
        5
        >>> nth([11, 22, 33], -1)
        33
        >>> nth([11, 22, 33])
        11

    .. versionadded:: 4.0.0
    """
    return pyd.get(array, pos)


def pop(array: t.List[T], index: int = -1) -> T:
    """
    Remove element of array at `index` and return element.

    Args:
        array: List to pop from.
        index: Index to remove element from. Defaults to ``-1``.

    Returns:
        Value at `index`.

    Warning:
        `array` is modified in place.

    Example:

        >>> array = [1, 2, 3, 4]
        >>> item = pop(array)
        >>> item
        4
        >>> array
        [1, 2, 3]
        >>> item = pop(array, index=0)
        >>> item
        1
        >>> array
        [2, 3]

    .. versionadded:: 2.2.0
    """
    return array.pop(index)


def pull(array: t.List[T], *values: T) -> t.List[T]:
    """
    Removes all provided values from the given array.

    Args:
        array: List to pull from.
        values: Values to remove.

    Returns:
        Modified `array`.

    Warning:
        `array` is modified in place.

    Example:

        >>> pull([1, 2, 2, 3, 3, 4], 2, 3)
        [1, 4]

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        :func:`pull` method now calls :func:`pull_all` method for the desired
        functionality.
    """
    return pull_all(array, values)


def pull_all(array: t.List[T], values: t.Iterable[T]) -> t.List[T]:
    """
    Removes all provided values from the given array.

    Args:
        array: Array to modify.
        values: Values to remove.

    Returns:
        Modified `array`.

    Example:

        >>> pull_all([1, 2, 2, 3, 3, 4], [2, 3])
        [1, 4]

    .. versionadded:: 4.0.0
    """
    # Use this style of assignment so that `array` is mutated.
    array[:] = without(array, *values)
    return array


def pull_all_by(
    array: t.List[T],
    values: t.Iterable[T],
    iteratee: t.Union[IterateeObjT, t.Callable[[T], t.Any], None] = None,
) -> t.List[T]:
    """
    This method is like :func:`pull_all` except that it accepts iteratee which is invoked for each
    element of array and values to generate the criterion by which they're compared. The iteratee is
    invoked with one argument: ``(value)``.

    Args:
        array: Array to modify.
        values: Values to remove.
        iteratee: Function to transform the elements of the arrays. Defaults to
            :func:`.identity`.

    Returns:
        Modified `array`.

    Example:

        >>> array = [{'x': 1}, {'x': 2}, {'x': 3}, {'x': 1}]
        >>> pull_all_by(array, [{'x': 1}, {'x': 3}], 'x')
        [{'x': 2}]

    .. versionadded:: 4.0.0
    """
    values = difference(array, difference_by(array, values, iteratee=iteratee))
    return pull_all(array, values)


def pull_all_with(
    array: t.List[T],
    values: t.Iterable[T],
    comparator: t.Union[t.Callable[[T, T], t.Any], None] = None,
) -> t.List[T]:
    """
    This method is like :func:`pull_all` except that it accepts comparator which is invoked to
    compare elements of array to values. The comparator is invoked with two arguments: ``(arr_val,
    oth_val)``.

    Args:
        array: Array to modify.
        values: Values to remove.
        comparator: Function to compare the elements of the arrays. Defaults to
            :func:`.is_equal`.

    Returns:
        Modified `array`.

    Example:

        >>> array = [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}, {'x': 5, 'y': 6}]
        >>> res = pull_all_with(array, [{'x': 3, 'y': 4}], lambda a, b: a == b)
        >>> res == [{'x': 1, 'y': 2}, {'x': 5, 'y': 6}]
        True
        >>> array = [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}, {'x': 5, 'y': 6}]
        >>> res = pull_all_with(array, [{'x': 3, 'y': 4}], lambda a, b: a != b)
        >>> res == [{'x': 3, 'y': 4}]
        True

    .. versionadded:: 4.0.0
    """
    values = difference(array, difference_with(array, values, comparator=comparator))
    return pull_all(array, values)


def pull_at(array: t.List[T], *indexes: int) -> t.List[T]:
    """
    Removes elements from `array` corresponding to the specified indexes and returns a list of the
    removed elements. Indexes may be specified as a list of indexes or as individual arguments.

    Args:
        array: List to pull from.
        indexes: Indexes to pull.

    Returns:
        Modified `array`.

    Warning:
        `array` is modified in place.

    Example:

        >>> pull_at([1, 2, 3, 4], 0, 2)
        [2, 4]

    .. versionadded:: 1.1.0
    """
    flat_indexes = flatten(indexes)
    for index in sorted(flat_indexes, reverse=True):
        del array[index]

    return array


def push(array: t.List[T], *items: T2) -> t.List[t.Union[T, T2]]:
    """
    Push items onto the end of `array` and return modified `array`.

    Args:
        array: List to push to.
        items: Items to append.

    Returns:
        Modified `array`.

    Warning:
        `array` is modified in place.

    Example:

        >>> array = [1, 2, 3]
        >>> push(array, 4, 5, [6])
        [1, 2, 3, 4, 5, [6]]

    .. versionadded:: 2.2.0

    .. versionchanged:: 4.0.0
        Removed alias ``append``.
    """
    for item in items:
        array.append(item)  # type: ignore
    return array  # type: ignore


def remove(
    array: t.List[T],
    predicate: t.Union[
        t.Callable[[T, int, t.List[T]], t.Any],
        t.Callable[[T, int], t.Any],
        t.Callable[[T], t.Any],
        None,
    ] = None,
) -> t.List[T]:
    """
    Removes all elements from a list that the predicate returns truthy for and returns an array of
    removed elements.

    Args:
        array: List to remove elements from.
        predicate: Predicate applied per iteration.

    Returns:
        Removed elements of `array`.

    Warning:
        `array` is modified in place.

    Example:

        >>> array = [1, 2, 3, 4]
        >>> items = remove(array, lambda x: x >= 3)
        >>> items
        [3, 4]
        >>> array
        [1, 2]

    .. versionadded:: 1.0.0
    """
    removed = []
    kept = []

    for is_true, _, i, _ in iteriteratee(array, predicate):
        if is_true:
            removed.append(array[i])
        else:
            kept.append(array[i])

    # Modify array in place.
    array[:] = kept

    return removed


def reverse(array: SequenceT) -> SequenceT:
    """
    Return `array` in reverse order.

    Args:
        array: Object to process.

    Returns:
        Reverse of object.

    Example:

        >>> reverse([1, 2, 3, 4])
        [4, 3, 2, 1]

    .. versionadded:: 2.2.0
    """
    # NOTE: Using this method to reverse object since it works for both lists and strings.
    return array[::-1]  # type: ignore


def shift(array: t.List[T]) -> T:
    """
    Remove the first element of `array` and return it.

    Args:
        array: List to shift.

    Returns:
        First element of `array`.

    Warning:
        `array` is modified in place.

    Example:

        >>> array = [1, 2, 3, 4]
        >>> item = shift(array)
        >>> item
        1
        >>> array
        [2, 3, 4]

    .. versionadded:: 2.2.0
    """
    return pop(array, 0)


def slice_(array: SequenceT, start: int = 0, end: t.Union[int, None] = None) -> SequenceT:
    """
    Slices `array` from the `start` index up to, but not including, the `end` index.

    Args:
        array: Array to slice.
        start: Start index. Defaults to ``0``.
        end: End index. Defaults to selecting the value at ``start`` index.

    Returns:
        Sliced list.

    Example:

        >>> slice_([1, 2, 3, 4])
        [1]
        >>> slice_([1, 2, 3, 4], 1)
        [2]
        >>> slice_([1, 2, 3, 4], 1, 3)
        [2, 3]

    .. versionadded:: 1.1.0
    """
    if end is None:
        end = (start + 1) if start >= 0 else (len(array) + start + 1)

    return array[start:end]  # type: ignore


@t.overload
def sort(
    array: t.List["SupportsRichComparisonT"],
    comparator: None = None,
    key: None = None,
    reverse: bool = False,
) -> t.List["SupportsRichComparisonT"]:
    ...


@t.overload
def sort(
    array: t.List[T], comparator: t.Callable[[T, T], int], *, reverse: bool = False
) -> t.List[T]:
    ...


@t.overload
def sort(
    array: t.List[T], *, key: t.Callable[[T], "SupportsRichComparisonT"], reverse: bool = False
) -> t.List[T]:
    ...


def sort(array, comparator=None, key=None, reverse=False):
    """
    Sort `array` using optional `comparator`, `key`, and `reverse` options and return sorted
    `array`.

    Note:
        Python 3 removed the option to pass a custom comparator function and instead only allows a
        key function. Therefore, if a comparator function is passed in, it will be converted to a
        key function automatically using ``functools.cmp_to_key``.

    Args:
        array: List to sort.
        comparator: A custom comparator function used to sort the list.
            Function should accept two arguments and return a negative, zero, or position number
            depending on whether the first argument is considered smaller than, equal to, or larger
            than the second argument. Defaults to ``None``. This argument is mutually exclusive with
            `key`.
        key: A function of one argument used to extract a comparator key from each list element.
            Defaults to ``None``. This argument is mutually exclusive with `comparator`.
        reverse: Whether to reverse the sort. Defaults to ``False``.

    Returns:
        Sorted list.

    Warning:
        `array` is modified in place.

    Example:

        >>> sort([2, 1, 4, 3])
        [1, 2, 3, 4]
        >>> sort([2, 1, 4, 3], reverse=True)
        [4, 3, 2, 1]
        >>> results = sort([{'a': 2, 'b': 1},\
                            {'a': 3, 'b': 2},\
                            {'a': 0, 'b': 3}],\
                           key=lambda item: item['a'])
        >>> assert results == [{'a': 0, 'b': 3},\
                               {'a': 2, 'b': 1},\
                               {'a': 3, 'b': 2}]

    .. versionadded:: 2.2.0
    """
    if comparator and key:
        raise ValueError('The "comparator" and "key" arguments are mutually exclusive')

    if comparator:
        key = cmp_to_key(comparator)

    array.sort(key=key, reverse=reverse)
    return array


def sorted_index(
    array: t.Sequence["SupportsRichComparisonT"], value: "SupportsRichComparisonT"
) -> int:
    """
    Uses a binary search to determine the lowest index at which `value` should be inserted into
    `array` in order to maintain its sort order.

    Args:
        array: List to inspect.
        value: Value to evaluate.

    Returns:
        Returns the index at which `value` should be inserted into `array`.

    Example:

        >>> sorted_index([1, 2, 2, 3, 4], 2)
        1

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Move iteratee support to :func:`sorted_index_by`.
    """
    return sorted_index_by(array, value)


@t.overload
def sorted_index_by(
    array: t.Sequence[T],
    value: T,
    iteratee: t.Union[IterateeObjT, t.Callable[[T], "SupportsRichComparisonT"]],
) -> int:
    ...


@t.overload
def sorted_index_by(
    array: t.Sequence["SupportsRichComparisonT"],
    value: "SupportsRichComparisonT",
    iteratee: None = None,
) -> int:
    ...


def sorted_index_by(array, value, iteratee=None):
    """
    This method is like :func:`sorted_index` except that it accepts iteratee which is invoked for
    `value` and each element of `array` to compute their sort ranking. The iteratee is invoked with
    one argument: ``(value)``.

    Args:
        array: List to inspect.
        value: Value to evaluate.
        iteratee: The iteratee invoked per element. Defaults to :func:`.identity`.

    Returns:
        Returns the index at which `value` should be inserted into `array`.

    Example:

        >>> array = [{'x': 4}, {'x': 5}]
        >>> sorted_index_by(array, {'x': 4}, lambda o: o['x'])
        0
        >>> sorted_index_by(array, {'x': 4}, 'x')
        0

    .. versionadded:: 4.0.0
    """
    if iteratee:
        # Generate array of sorted keys computed using iteratee.
        iteratee = pyd.iteratee(iteratee)
        array = sorted(iteratee(item) for item in array)
        value = iteratee(value)

    return bisect_left(array, value)


def sorted_index_of(
    array: t.Sequence["SupportsRichComparisonT"], value: "SupportsRichComparisonT"
) -> int:
    """
    Returns the index of the matched `value` from the sorted `array`, else ``-1``.

    Args:
        array: Array to inspect.
        value: Value to search for.

    Returns:
        Returns the index of the first matched value, else ``-1``.

    Example:

        >>> sorted_index_of([3, 5, 7, 10], 3)
        0
        >>> sorted_index_of([10, 10, 5, 7, 3], 10)
        -1

    .. versionadded:: 4.0.0
    """
    index = sorted_index(array, value)

    if index < len(array) and array[index] == value:
        return index
    else:
        return -1


def sorted_last_index(
    array: t.Sequence["SupportsRichComparisonT"], value: "SupportsRichComparisonT"
) -> int:
    """
    This method is like :func:`sorted_index` except that it returns the highest index at which
    `value` should be inserted into `array` in order to maintain its sort order.

    Args:
        array: List to inspect.
        value: Value to evaluate.

    Returns:
        Returns the index at which `value` should be inserted into `array`.

    Example:

        >>> sorted_last_index([1, 2, 2, 3, 4], 2)
        3

    .. versionadded:: 1.1.0

    .. versionchanged:: 4.0.0
        Move iteratee support to :func:`sorted_last_index_by`.
    """
    return sorted_last_index_by(array, value)


@t.overload
def sorted_last_index_by(
    array: t.Sequence[T],
    value: T,
    iteratee: t.Union[IterateeObjT, t.Callable[[T], "SupportsRichComparisonT"]],
) -> int:
    ...


@t.overload
def sorted_last_index_by(
    array: t.Sequence["SupportsRichComparisonT"],
    value: "SupportsRichComparisonT",
    iteratee: None = None,
) -> int:
    ...


def sorted_last_index_by(array, value, iteratee=None):
    """
    This method is like :func:`sorted_last_index` except that it accepts iteratee which is invoked
    for `value` and each element of `array` to compute their sort ranking. The iteratee is invoked
    with one argument: ``(value)``.

    Args:
        array: List to inspect.
        value: Value to evaluate.
        iteratee: The iteratee invoked per element. Defaults to :func:`.identity`.

    Returns:
        Returns the index at which `value` should be inserted into `array`.

    Example:

        >>> array = [{'x': 4}, {'x': 5}]
        >>> sorted_last_index_by(array, {'x': 4}, lambda o: o['x'])
        1
        >>> sorted_last_index_by(array, {'x': 4}, 'x')
        1
    """
    if iteratee:
        # Generate array of sorted keys computed using iteratee.
        iteratee = pyd.iteratee(iteratee)
        array = sorted(iteratee(item) for item in array)
        value = iteratee(value)

    return bisect_right(array, value)


def sorted_last_index_of(
    array: t.Sequence["SupportsRichComparisonT"], value: "SupportsRichComparisonT"
) -> int:
    """
    This method is like :func:`last_index_of` except that it performs a binary search on a sorted
    `array`.

    Args:
        array: Array to inspect.
        value: Value to search for.

    Returns:
        Returns the index of the matched value, else ``-1``.

    Example:

        >>> sorted_last_index_of([4, 5, 5, 5, 6], 5)
        3
        >>> sorted_last_index_of([6, 5, 5, 5, 4], 6)
        -1

    .. versionadded:: 4.0.0
    """
    index = sorted_last_index(array, value) - 1

    if index < len(array) and array[index] == value:
        return index
    else:
        return -1


def sorted_uniq(array: t.Iterable["SupportsRichComparisonT"]) -> t.List["SupportsRichComparisonT"]:
    """
    Return sorted array with unique elements.

    Args:
        array: List of values to be sorted.

    Returns:
        List of unique elements in a sorted fashion.

    Example:

        >>> sorted_uniq([4, 2, 2, 5])
        [2, 4, 5]
        >>> sorted_uniq([-2, -2, 4, 1])
        [-2, 1, 4]

    .. versionadded:: 4.0.0
    """
    return sorted(uniq(array))


def sorted_uniq_by(
    array: t.Iterable["SupportsRichComparisonT"],
    iteratee: t.Union[
        t.Callable[["SupportsRichComparisonT"], "SupportsRichComparisonT"], None
    ] = None,
) -> t.List["SupportsRichComparisonT"]:
    """
    This method is like :func:`sorted_uniq` except that it accepts iteratee which is invoked for
    each element in array to generate the criterion by which uniqueness is computed. The order of
    result values is determined by the order they occur in the array. The iteratee is invoked with
    one argument: ``(value)``.

    Args:
        array: List of values to be sorted.
        iteratee: Function to transform the elements of the arrays. Defaults to
            :func:`.identity`.

    Returns:
        Unique list.

    Example:

        >>> sorted_uniq_by([3, 2, 1, 3, 2, 1], lambda val: val % 2)
        [2, 3]

    .. versionadded:: 4.0.0
    """
    return sorted(uniq_by(array, iteratee=iteratee))


def splice(
    array: MutableSequenceT, start: int, count: t.Union[int, None] = None, *items: t.Any
) -> MutableSequenceT:
    """
    Modify the contents of `array` by inserting elements starting at index `start` and removing
    `count` number of elements after.

    Args:
        array: List to splice.
        start: Start to splice at.
        count: Number of items to remove starting at `start`. If ``None`` then all
            items after `start` are removed. Defaults to ``None``.
        items: Elements to insert starting at `start`. Each item is inserted in the order
            given.

    Returns:
        The removed elements of `array` or the spliced string.

    Warning:
        `array` is modified in place if ``list``.

    Example:

        >>> array = [1, 2, 3, 4]
        >>> splice(array, 1)
        [2, 3, 4]
        >>> array
        [1]
        >>> array = [1, 2, 3, 4]
        >>> splice(array, 1, 2)
        [2, 3]
        >>> array
        [1, 4]
        >>> array = [1, 2, 3, 4]
        >>> splice(array, 1, 2, 0, 0)
        [2, 3]
        >>> array
        [1, 0, 0, 4]

    .. versionadded:: 2.2.0

    .. versionchanged:: 3.0.0
        Support string splicing.
    """
    if count is None:
        count = len(array) - start

    is_string = pyd.is_string(array)

    if is_string:
        # allow reassignment with different type
        array = list(array)  # type: ignore

    removed = array[start : start + count]
    del array[start : start + count]

    for item in reverse(items):
        array.insert(start, item)

    if is_string:
        return "".join(array)  # type: ignore
    else:
        return removed  # type: ignore


def split_at(array: t.Sequence[T], index: int) -> t.List[t.Sequence[T]]:
    """
    Returns a list of two lists composed of the split of `array` at `index`.

    Args:
        array: List to split.
        index: Index to split at.

    Returns:
        Split list.

    Example:

        >>> split_at([1, 2, 3, 4], 2)
        [[1, 2], [3, 4]]

    .. versionadded:: 2.0.0
    """
    return [array[:index], array[index:]]


def tail(array: t.Sequence[T]) -> t.Sequence[T]:
    """
    Return all but the first element of `array`.

    Args:
        array: List to process.

    Returns:
        Rest of the list.

    Example:

        >>> tail([1, 2, 3, 4])
        [2, 3, 4]

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Renamed from ``rest`` to ``tail``.
    """
    return array[1:]


def take(array: t.Sequence[T], n: int = 1) -> t.Sequence[T]:
    """
    Creates a slice of `array` with `n` elements taken from the beginning.

    Args:
        array: List to process.
        n: Number of elements to take. Defaults to ``1``.

    Returns:
        Taken list.

    Example:

        >>> take([1, 2, 3, 4], 2)
        [1, 2]

    .. versionadded:: 1.0.0

    .. versionchanged:: 1.1.0
        Added ``n`` argument and removed as alias of :func:`first`.

    .. versionchanged:: 3.0.0
        Made ``n`` default to ``1``.
    """
    return take_while(array, lambda _, index: index < n)


def take_right(array: t.Sequence[T], n: int = 1) -> t.Sequence[T]:
    """
    Creates a slice of `array` with `n` elements taken from the end.

    Args:
        array: List to process.
        n: Number of elements to take. Defaults to ``1``.

    Returns:
        Taken list.

    Example:

        >>> take_right([1, 2, 3, 4], 2)
        [3, 4]

    .. versionadded:: 1.1.0

    .. versionchanged:: 3.0.0
        Made ``n`` default to ``1``.
    """
    length = len(array)
    return take_right_while(array, lambda _, index: (length - index) <= n)


@t.overload
def take_right_while(
    array: t.Sequence[T], predicate: t.Callable[[T, int, t.List[T]], t.Any]
) -> t.Sequence[T]:
    ...


@t.overload
def take_right_while(array: t.Sequence[T], predicate: t.Callable[[T, int], t.Any]) -> t.Sequence[T]:
    ...


@t.overload
def take_right_while(array: t.Sequence[T], predicate: t.Callable[[T], t.Any]) -> t.Sequence[T]:
    ...


@t.overload
def take_right_while(array: t.Sequence[T], predicate: None = None) -> t.Sequence[T]:
    ...


def take_right_while(array, predicate=None):
    """
    Creates a slice of `array` with elements taken from the end. Elements are taken until the
    `predicate` returns falsey. The `predicate` is invoked with three arguments: ``(value, index,
    array)``.

    Args:
        array: List to process.
        predicate: Predicate called per iteration

    Returns:
        Dropped list.

    Example:

        >>> take_right_while([1, 2, 3, 4], lambda x: x >= 3)
        [3, 4]

    .. versionadded:: 1.1.0
    """
    n = len(array)
    for is_true, _, _, _ in iteriteratee(array, predicate, reverse=True):
        if is_true:
            n -= 1
        else:
            break

    return array[n:]


@t.overload
def take_while(
    array: t.Sequence[T], predicate: t.Callable[[T, int, t.List[T]], t.Any]
) -> t.List[T]:
    ...


@t.overload
def take_while(array: t.Sequence[T], predicate: t.Callable[[T, int], t.Any]) -> t.List[T]:
    ...


@t.overload
def take_while(array: t.Sequence[T], predicate: t.Callable[[T], t.Any]) -> t.List[T]:
    ...


@t.overload
def take_while(array: t.Sequence[T], predicate: None = None) -> t.List[T]:
    ...


def take_while(array, predicate=None):
    """
    Creates a slice of `array` with elements taken from the beginning. Elements are taken until the
    `predicate` returns falsey. The `predicate` is invoked with three arguments: ``(value, index,
    array)``.

    Args:
        array: List to process.
        predicate: Predicate called per iteration

    Returns:
        Taken list.

    Example:

        >>> take_while([1, 2, 3, 4], lambda x: x < 3)
        [1, 2]

    .. versionadded:: 1.1.0
    """
    n = 0
    for is_true, _, _, _ in iteriteratee(array, predicate):
        if is_true:
            n += 1
        else:
            break

    return array[:n]


@t.overload
def union(array: t.Sequence[T]) -> t.List[T]:
    ...


@t.overload
def union(array: t.Sequence[T], *others: t.Sequence[T2]) -> t.List[t.Union[T, T2]]:
    ...


def union(array, *others):
    """
    Computes the union of the passed-in arrays.

    Args:
        array: List to union with.
        others: Lists to unionize with `array`.

    Returns:
        Unionized list.

    Example:

        >>> union([1, 2, 3], [2, 3, 4], [3, 4, 5])
        [1, 2, 3, 4, 5]

    .. versionadded:: 1.0.0
    """
    if not others:
        return array[:]

    return uniq(flatten([array] + list(others)))


@t.overload
def union_by(
    array: t.Sequence[T], *others: t.Iterable[T], iteratee: t.Callable[[T], t.Any]
) -> t.List[T]:
    ...


@t.overload
def union_by(
    array: t.Sequence[T], *others: t.Union[t.Iterable[T], t.Callable[[T], t.Any]]
) -> t.List[T]:
    ...


def union_by(array, *others, **kwargs):
    """
    This method is similar to :func:`union` except that it accepts iteratee which is invoked for
    each element of each array to generate the criterion by which uniqueness is computed.

    Args:
        array: List to unionize with.
        others: Lists to unionize with `array`.

    Keyword Args:
        iteratee: Function to invoke on each element.

    Returns:
        Unionized list.

    Example:

        >>> union_by([1, 2, 3], [2, 3, 4], iteratee=lambda x: x % 2)
        [1, 2]
        >>> union_by([1, 2, 3], [2, 3, 4], iteratee=lambda x: x % 9)
        [1, 2, 3, 4]

    .. versionadded:: 4.0.0
    """
    if not others:
        return array[:]

    iteratee, others = parse_iteratee("iteratee", *others, **kwargs)

    return uniq_by(flatten([array] + list(others)), iteratee=iteratee)


@t.overload
def union_with(
    array: t.Sequence[T], *others: t.Iterable[T2], comparator: t.Callable[[T, T2], t.Any]
) -> t.List[T]:
    ...


@t.overload
def union_with(
    array: t.Sequence[T], *others: t.Union[t.Iterable[T2], t.Callable[[T, T2], t.Any]]
) -> t.List[T]:
    ...


def union_with(array, *others, **kwargs):
    """
    This method is like :func:`union` except that it accepts comparator which is invoked to compare
    elements of arrays. Result values are chosen from the first array in which the value occurs.

    Args:
        array: List to unionize with.
        others: Lists to unionize with `array`.

    Keyword Args:
        comparator: Function to compare the elements of the arrays. Defaults to
            :func:`.is_equal`.

    Returns:
        Unionized list.

    Example:

        >>> comparator = lambda a, b: (a % 2) == (b % 2)
        >>> union_with([1, 2, 3], [2, 3, 4], comparator=comparator)
        [1, 2]
        >>> union_with([1, 2, 3], [2, 3, 4])
        [1, 2, 3, 4]

    .. versionadded:: 4.0.0
    """
    if not others:
        return array[:]

    comparator, others = parse_iteratee("comparator", *others, **kwargs)

    return uniq_with(flatten([array] + list(others)), comparator=comparator)


def uniq(array: t.Iterable[T]) -> t.List[T]:
    """
    Creates a duplicate-value-free version of the array. If iteratee is passed, each element of
    array is passed through an iteratee before uniqueness is computed. The iteratee is invoked with
    three arguments: ``(value, index, array)``. If an object path is passed for iteratee, the
    created iteratee will return the path value of the given element. If an object is passed for
    iteratee, the created filter style iteratee will return ``True`` for elements that have the
    properties of the given object, else ``False``.

    Args:
        array: List to process.

    Returns:
        Unique list.

    Example:

        >>> uniq([1, 2, 3, 1, 2, 3])
        [1, 2, 3]

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0

        - Moved `iteratee` argument to :func:`uniq_by`.
        - Removed alias ``unique``.
    """
    return uniq_by(array)


def uniq_by(
    array: t.Iterable[T], iteratee: t.Union[t.Callable[[T], t.Any], None] = None
) -> t.List[T]:
    """
    This method is like :func:`uniq` except that it accepts iteratee which is invoked for each
    element in array to generate the criterion by which uniqueness is computed. The order of result
    values is determined by the order they occur in the array. The iteratee is invoked with one
    argument: ``(value)``.

    Args:
        array: List to process.
        iteratee: Function to transform the elements of the arrays. Defaults to
            :func:`.identity`.

    Returns:
        Unique list.

    Example:

        >>> uniq_by([1, 2, 3, 1, 2, 3], lambda val: val % 2)
        [1, 2]

    .. versionadded:: 4.0.0
    """
    return list(iterunique(array, iteratee=iteratee))


def uniq_with(
    array: t.Sequence[T], comparator: t.Union[t.Callable[[T, T], t.Any], None] = None
) -> t.List[T]:
    """
    This method is like :func:`uniq` except that it accepts comparator which is invoked to compare
    elements of array. The order of result values is determined by the order they occur in the
    array.The comparator is invoked with two arguments: ``(value, other)``.

    Args:
        array: List to process.
        comparator: Function to compare the elements of the arrays. Defaults to
            :func:`.is_equal`.

    Returns:
        Unique list.

    Example:

        >>> uniq_with([1, 2, 3, 4, 5], lambda a, b: (a % 2) == (b % 2))
        [1, 2]

    .. versionadded:: 4.0.0
    """
    return list(iterunique(array, comparator=comparator))


def unshift(array: t.List[T], *items: T2) -> t.List[t.Union[T, T2]]:
    """
    Insert the given elements at the beginning of `array` and return the modified list.

    Args:
        array: List to modify.
        items: Items to insert.

    Returns:
        Modified list.

    Warning:
        `array` is modified in place.

    Example:

        >>> array = [1, 2, 3, 4]
        >>> unshift(array, -1, -2)
        [-1, -2, 1, 2, 3, 4]
        >>> array
        [-1, -2, 1, 2, 3, 4]

    .. versionadded:: 2.2.0
    """
    for item in reverse(items):
        array.insert(0, item)  # type: ignore

    return array  # type: ignore


def unzip(array: t.Iterable[t.Iterable[T]]) -> t.List[t.List[T]]:
    """
    The inverse of :func:`zip_`, this method splits groups of elements into lists composed of
    elements from each group at their corresponding indexes.

    Args:
        array: List to process.

    Returns:
        Unzipped list.

    Example:

        >>> unzip([[1, 4, 7], [2, 5, 8], [3, 6, 9]])
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    .. versionadded:: 1.0.0
    """
    return zip_(*array)


@t.overload
def unzip_with(
    array: t.Iterable[t.Iterable[T]],
    iteratee: t.Union[
        t.Callable[[T, T, int, t.List[T]], T2],
        t.Callable[[T, T, int], T2],
        t.Callable[[T, T], T2],
        t.Callable[[T], T2],
    ],
) -> t.List[T2]:
    ...


@t.overload
def unzip_with(
    array: t.Iterable[t.Iterable[T]],
    iteratee: None = None,
) -> t.List[t.List[T]]:
    ...


def unzip_with(array, iteratee=None):
    """
    This method is like :func:`unzip` except that it accepts an iteratee to specify how regrouped
    values should be combined. The iteratee is invoked with four arguments: ``(accumulator, value,
    index, group)``.

    Args:
        array: List to process.
        iteratee: Function to combine regrouped values.

    Returns:
        Unzipped list.

    Example:

        >>> from pydash import add
        >>> unzip_with([[1, 10, 100], [2, 20, 200]], add)
        [3, 30, 300]

    .. versionadded:: 3.3.0
    """
    if not array:
        return []

    result = unzip(array)

    if iteratee is None:
        return result

    def cbk(group):
        return pyd.reduce_(group, iteratee)

    return pyd.map_(result, cbk)


def without(array: t.Iterable[T], *values: T) -> t.List[T]:
    """
    Creates an array with all occurrences of the passed values removed.

    Args:
        array: List to filter.
        values: Values to remove.

    Returns:
        Filtered list.

    Example:

        >>> without([1, 2, 3, 2, 4, 4], 2, 4)
        [1, 3]

    .. versionadded:: 1.0.0
    """
    return [item for item in array if item not in values]


def xor(array: t.Iterable[T], *lists: t.Iterable[T]) -> t.List[T]:
    """
    Creates a list that is the symmetric difference of the provided lists.

    Args:
        array: List to process.
        *lists: Lists to xor with.

    Returns:
        XOR'd list.

    Example:

        >>> xor([1, 3, 4], [1, 2, 4], [2])
        [3]

    .. versionadded:: 1.0.0
    """
    return xor_by(array, *lists)


@t.overload
def xor_by(
    array: t.Iterable[T],
    *lists: t.Iterable[T],
    iteratee: t.Union[t.Callable[[T], t.Any], IterateeObjT],
) -> t.List[T]:
    ...


@t.overload
def xor_by(
    array: t.Iterable[T], *lists: t.Union[t.Iterable[T], t.Callable[[T], t.Any]]
) -> t.List[T]:
    ...


def xor_by(array, *lists, **kwargs):
    """
    This method is like :func:`xor` except that it accepts iteratee which is invoked for each
    element of each arras to generate the criterion by which they're compared. The order of result
    values is determined by the order they occur in the arrays. The iteratee is invoked with one
    argument: ``(value)``.

    Args:
        array: List to process.
        *lists: Lists to xor with.

    Keyword Args:
        iteratee: Function to transform the elements of the arrays. Defaults to
            :func:`.identity`.

    Returns:
        XOR'd list.

    Example:

        >>> xor_by([2.1, 1.2], [2.3, 3.4], round)
        [1.2, 3.4]
        >>> xor_by([{'x': 1}], [{'x': 2}, {'x': 1}], 'x')
        [{'x': 2}]

    .. versionadded:: 4.0.0
    """
    if not lists:
        return array[:]

    iteratee, lists = parse_iteratee("iteratee", *lists, **kwargs)

    return xor(
        uniq(
            difference_by(
                array + lists[0],
                intersection_by(array, lists[0], iteratee=iteratee),
                iteratee=iteratee,
            )
        ),
        *lists[1:],
    )


@t.overload
def xor_with(
    array: t.Sequence[T], *lists: t.Iterable[T2], comparator: t.Callable[[T, T2], t.Any]
) -> t.List[T]:
    ...


@t.overload
def xor_with(
    array: t.Sequence[T], *lists: t.Union[t.Iterable[T2], t.Callable[[T, T2], t.Any]]
) -> t.List[T]:
    ...


def xor_with(array, *lists, **kwargs):
    """
    This method is like :func:`xor` except that it accepts comparator which is invoked to compare
    elements of arrays. The order of result values is determined by the order they occur in the
    arrays. The comparator is invoked with two arguments: ``(arr_val, oth_val)``.

    Args:
        array: List to process.
        *lists: Lists to xor with.

    Keyword Args:
        comparator: Function to compare the elements of the arrays. Defaults to
            :func:`.is_equal`.

    Returns:
        XOR'd list.

    Example:

        >>> objects = [{'x': 1, 'y': 2}, {'x': 2, 'y': 1}]
        >>> others = [{'x': 1, 'y': 1}, {'x': 1, 'y': 2}]
        >>> expected = [{'y': 1, 'x': 2}, {'y': 1, 'x': 1}]
        >>> xor_with(objects, others, lambda a, b: a == b) == expected
        True

    .. versionadded:: 4.0.0
    """
    if not lists:
        return array[:]

    comp, lists = parse_iteratee("comparator", *lists, **kwargs)

    return xor_with(
        uniq(
            difference_with(
                array + lists[0],
                intersection_with(array, lists[0], comparator=comp),
                comparator=comp,
            )
        ),
        *lists[1:],
    )


def zip_(*arrays: t.Iterable[T]) -> t.List[t.List[T]]:
    """
    Groups the elements of each array at their corresponding indexes. Useful for separate data
    sources that are coordinated through matching array indexes.

    Args:
        arrays: Lists to process.

    Returns:
        Zipped list.

    Example:

        >>> zip_([1, 2, 3], [4, 5, 6], [7, 8, 9])
        [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

    .. versionadded:: 1.0.0
    """
    # zip returns as a list of tuples so convert to list of lists
    return [list(item) for item in zip(*arrays)]


@t.overload
def zip_object(keys: t.Iterable[t.Tuple[T, T2]], values: None = None) -> t.Dict[T, T2]:
    ...


@t.overload
def zip_object(
    keys: t.Iterable[t.List[t.Union[T, T2]]], values: None = None
) -> t.Dict[t.Union[T, T2], t.Union[T, T2]]:
    ...


@t.overload
def zip_object(keys: t.Iterable[T], values: t.List[T2]) -> t.Dict[T, T2]:
    ...


def zip_object(keys, values=None):
    """
    Creates a dict composed of lists of keys and values. Pass either a single two-dimensional list,
    i.e. ``[[key1, value1], [key2, value2]]``, or two lists, one of keys and one of corresponding
    values.

    Args:
        keys: Either a list of keys or a list of ``[key, value]`` pairs.
        values: List of values to zip.

    Returns:
        Zipped dict.

    Example:

        >>> zip_object([1, 2, 3], [4, 5, 6])
        {1: 4, 2: 5, 3: 6}

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Removed alias ``object_``.
    """

    if values is None:
        keys, values = unzip(keys)

    return dict(zip(keys, values))


def zip_object_deep(keys: t.Iterable[t.Any], values: t.Union[t.List[t.Any], None] = None) -> t.Dict:
    """
    This method is like :func:`zip_object` except that it supports property paths.

    Args:
        keys: Either a list of keys or a list of ``[key, value]`` pairs.
        values: List of values to zip.

    Returns:
        Zipped dict.

    Example:

        >>> expected = {'a': {'b': {'c': 1, 'd': 2}}}
        >>> zip_object_deep(['a.b.c', 'a.b.d'], [1, 2]) == expected
        True

    .. versionadded:: 4.0.0
    """
    if values is None:  # pragma: no cover
        keys, values = unzip(keys)

    obj: t.Dict = {}
    for idx, key in enumerate(keys):
        obj = pyd.set_(obj, key, pyd.get(values, idx))

    return obj


@t.overload
def zip_with(
    *arrays: t.Iterable[T],
    iteratee: t.Union[
        t.Callable[[T, T, int, t.List[T]], T2],
        t.Callable[[T, T, int], T2],
        t.Callable[[T, T], T2],
        t.Callable[[T], T2],
    ],
) -> t.List[T2]:
    ...


@t.overload
def zip_with(*arrays: t.Iterable[T]) -> t.List[t.List[T]]:
    ...


@t.overload
def zip_with(
    *arrays: t.Union[
        t.Iterable[T],
        t.Callable[[T, T, int, t.List[T]], T2],
        t.Callable[[T, T, int], T2],
        t.Callable[[T, T], T2],
        t.Callable[[T], T2],
    ],
) -> t.List[t.Union[t.List[T], T2]]:
    ...


def zip_with(*arrays, **kwargs):
    """
    This method is like :func:`zip` except that it accepts an iteratee to specify how grouped values
    should be combined. The iteratee is invoked with four arguments: ``(accumulator, value, index,
    group)``.

    Args:
        *arrays: Lists to process.

    Keyword Args:
        iteratee (callable): Function to combine grouped values.

    Returns:
        Zipped list of grouped elements.

    Example:

        >>> from pydash import add
        >>> zip_with([1, 2], [10, 20], [100, 200], add)
        [111, 222]
        >>> zip_with([1, 2], [10, 20], [100, 200], iteratee=add)
        [111, 222]

    .. versionadded:: 3.3.0
    """
    if "iteratee" in kwargs:
        iteratee = kwargs["iteratee"]
    elif len(arrays) > 1:
        iteratee = arrays[-1]
        arrays = arrays[:-1]
    else:
        iteratee = None

    return unzip_with(arrays, iteratee)


#
# Utility methods not a part of the main API
#


def iterflatten(array, depth=-1):
    """Iteratively flatten a list shallowly or deeply."""
    for item in array:
        if isinstance(item, (list, tuple)) and depth != 0:
            for subitem in iterflatten(item, depth - 1):
                yield subitem
        else:
            yield item


def iterinterleave(*arrays):
    """Interleave multiple lists."""
    iters = [iter(arr) for arr in arrays]

    while iters:
        nextiters = []
        for itr in iters:
            try:
                yield next(itr)
                nextiters.append(itr)
            except StopIteration:
                pass

        iters = nextiters


def iterintersperse(iterable, separator):
    """Iteratively intersperse iterable."""
    iterable = iter(iterable)
    yield next(iterable)
    for item in iterable:
        yield separator
        yield item


def iterunique(array, comparator=None, iteratee=None):  # noqa: C901
    """Yield each unique item in array."""
    if not array:  # pragma: no cover
        return

    if iteratee is not None:
        iteratee = pyd.iteratee(iteratee)

    seen_hashable = set()
    seen_unhashable = []

    for item in array:
        if iteratee is None:
            cmp_item = item
        else:
            cmp_item = iteratee(item)

        if comparator is None:
            try:
                if cmp_item not in seen_hashable:
                    yield item
                    seen_hashable.add(cmp_item)
            except TypeError:
                if cmp_item not in seen_unhashable:
                    yield item
                    seen_unhashable.append(cmp_item)
        else:
            unseen = True
            for seen_item in seen_unhashable:
                if comparator(cmp_item, seen_item):
                    unseen = False
                    break
            if unseen:
                yield item
                seen_unhashable.append(cmp_item)


def iterduplicates(array):
    """Yield duplictes found in `array`."""
    seen = []
    for i, item in enumerate(array):
        if item in seen:
            yield i, item
        else:
            seen.append(item)


def iterintersection(array, other, comparator=None, iteratee=None):
    """Yield intersecting values between `array` and `other` using `comparator` to determine if they
    intersect."""
    if not array or not other:  # pragma: no cover
        return

    if comparator is None:
        comparator = pyd.is_equal

    iteratee = pyd.iteratee(iteratee)

    # NOTE: Maintain ordering of yielded values based on `array` ordering.
    seen = []
    for item in array:
        cmp_item = iteratee(item)

        if cmp_item in seen:
            continue

        seen.append(cmp_item)
        seen_others = []

        for value in other:
            cmp_value = iteratee(value)

            if cmp_value in seen_others:
                continue

            seen_others.append(cmp_value)

            if comparator(cmp_item, cmp_value):
                yield item
                break


def iterdifference(array, other, comparator=None, iteratee=None):
    """Yield different values in `array` as compared to `other` using `comparator` to determine if
    they are different."""
    if not array or not other:  # pragma: no cover
        return

    if comparator is None:
        comparator = pyd.is_equal

    iteratee = pyd.iteratee(iteratee)

    def is_different(item, seen):
        is_diff = True

        if item not in seen:
            for value in other:
                if comparator(iteratee(item), iteratee(value)):
                    is_diff = False
                    break

            if is_diff:
                seen.append(item)
        return is_diff

    seen = []
    not_seen = []

    for item in array:
        if item in not_seen or is_different(item, seen):
            yield item
