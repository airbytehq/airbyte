"""
Functions that operate on lists, dicts, and other objects.

.. versionadded:: 1.0.0
"""

import copy
from functools import partial
import math
import re
import typing as t

import pydash as pyd

from .helpers import UNSET, base_get, base_set, callit, getargcount, iterator, iteriteratee
from .types import IterateeObjT, PathT
from .utilities import PathToken, to_path, to_path_tokens


if t.TYPE_CHECKING:
    from _typeshed import SupportsRichComparisonT  # pragma: no cover

__all__ = (
    "assign",
    "assign_with",
    "callables",
    "clone",
    "clone_deep",
    "clone_deep_with",
    "clone_with",
    "defaults",
    "defaults_deep",
    "find_key",
    "find_last_key",
    "for_in",
    "for_in_right",
    "get",
    "has",
    "invert",
    "invert_by",
    "invoke",
    "keys",
    "map_keys",
    "map_values",
    "map_values_deep",
    "merge",
    "merge_with",
    "omit",
    "omit_by",
    "parse_int",
    "pick",
    "pick_by",
    "rename_keys",
    "set_",
    "set_with",
    "to_boolean",
    "to_dict",
    "to_integer",
    "to_list",
    "to_number",
    "to_pairs",
    "to_string",
    "transform",
    "unset",
    "update",
    "update_with",
    "values",
)

T = t.TypeVar("T")
T2 = t.TypeVar("T2")
T3 = t.TypeVar("T3")
T4 = t.TypeVar("T4")
T5 = t.TypeVar("T5")


@t.overload
def assign(
    obj: t.Mapping[T, T2], *sources: t.Mapping[T3, T4]
) -> t.Dict[t.Union[T, T3], t.Union[T2, T4]]:
    ...


@t.overload
def assign(
    obj: t.Union[t.Tuple[T, ...], t.List[T]], *sources: t.Mapping[int, T2]
) -> t.List[t.Union[T, T2]]:
    ...


def assign(obj, *sources) -> t.Union[t.List, t.Dict]:
    """
    Assigns properties of source object(s) to the destination object.

    Args:
        obj: Destination object whose properties will be modified.
        sources: Source objects to assign to `obj`.

    Returns:
        Modified `obj`.

    Warning:
        `obj` is modified in place.

    Example:

        >>> obj = {}
        >>> obj2 = assign(obj, {'a': 1}, {'b': 2}, {'c': 3})
        >>> obj == {'a': 1, 'b': 2, 'c': 3}
        True
        >>> obj is obj2
        True

    .. versionadded:: 1.0.0

    .. versionchanged:: 2.3.2
        Apply :func:`clone_deep` to each `source` before assigning to `obj`.

    .. versionchanged:: 3.0.0
        Allow iteratees to accept partial arguments.

    .. versionchanged:: 3.4.4
        Shallow copy each `source` instead of deep copying.

    .. versionchanged:: 4.0.0

        - Moved `iteratee` argument to :func:`assign_with`.
        - Removed alias ``extend``.
    """
    return assign_with(obj, *sources)  # type: ignore


@t.overload
def assign_with(
    obj: t.Mapping[T, T2],
    *sources: t.Mapping[T3, t.Any],
    customizer: t.Callable[[t.Union[T2, None]], T5],
) -> t.Dict[t.Union[T, T3], t.Union[T2, T5]]:
    ...


@t.overload
def assign_with(
    obj: t.Mapping[T, T2],
    *sources: t.Mapping[T3, T4],
    customizer: t.Callable[[t.Union[T2, None], T4], T5],
) -> t.Dict[t.Union[T, T3], t.Union[T2, T5]]:
    ...


@t.overload
def assign_with(
    obj: t.Mapping[T, T2],
    *sources: t.Mapping[T3, T4],
    customizer: t.Callable[[t.Union[T2, None], T4, T3], T5],
) -> t.Dict[t.Union[T, T3], t.Union[T2, T5]]:
    ...


@t.overload
def assign_with(
    obj: t.Mapping[T, T2],
    *sources: t.Mapping[T3, T4],
    customizer: t.Callable[[t.Union[T2, None], T4, T3, t.Dict[T, T2]], T5],
) -> t.Dict[t.Union[T, T3], t.Union[T2, T5]]:
    ...


@t.overload
def assign_with(
    obj: t.Mapping[T, T2],
    *sources: t.Mapping[T3, T4],
    customizer: t.Callable[[t.Union[T2, None], T4, T3, t.Dict[T, T2], t.Dict[T3, T4]], T5],
) -> t.Dict[t.Union[T, T3], t.Union[T2, T5]]:
    ...


@t.overload
def assign_with(
    obj: t.Mapping[T, T2], *sources: t.Mapping[T3, T4], customizer: None = None
) -> t.Dict[t.Union[T, T3], t.Union[T2, T4]]:
    ...


def assign_with(obj, *sources, customizer=None):
    """
    This method is like :func:`assign` except that it accepts customizer which is invoked to produce
    the assigned values. If customizer returns ``None``, assignment is handled by the method
    instead. The customizer is invoked with five arguments: ``(obj_value, src_value, key, obj,
    source)``.

    Args:
        obj: Destination object whose properties will be modified.
        sources: Source objects to assign to `obj`.

    Keyword Args:
        customizer: Customizer applied per iteration.

    Returns:
        Modified `obj`.

    Warning:
        `obj` is modified in place.

    Example:

        >>> customizer = lambda o, s: s if o is None else o
        >>> results = assign_with({'a': 1}, {'b': 2}, {'a': 3}, customizer)
        >>> results == {'a': 1, 'b': 2}
        True

    .. versionadded:: 4.0.0
    """
    sources = list(sources)

    if customizer is None and callable(sources[-1]):
        customizer = sources.pop()

    if customizer is not None:
        argcount = getargcount(customizer, maxargs=5)
    else:
        argcount = None

    for source in sources:
        source = source.copy()

        for key, value in source.items():
            if customizer:
                val = callit(customizer, obj.get(key), value, key, obj, source, argcount=argcount)
                if val is not None:
                    value = val

            obj[key] = value

    return obj


@t.overload
def callables(
    obj: t.Mapping["SupportsRichComparisonT", t.Any]
) -> t.List["SupportsRichComparisonT"]:
    ...


@t.overload
def callables(obj: t.Iterable[T]) -> t.List[T]:
    ...


def callables(obj) -> t.List:
    """
    Creates a sorted list of keys of an object that are callable.

    Args:
        obj: Object to inspect.

    Returns:
        All keys whose values are callable.

    Example:

        >>> callables({'a': 1, 'b': lambda: 2, 'c': lambda: 3})
        ['b', 'c']

    .. versionadded:: 1.0.0

    .. versionchanged:: 2.0.0
        Renamed ``functions`` to ``callables``.

    .. versionchanged:: 4.0.0
        Removed alias ``methods``.
    """
    return sorted(key for key, value in iterator(obj) if callable(value))


def clone(value: T) -> T:
    """
    Creates a clone of `value`.

    Args:
        value: Object to clone.

    Example:

        >>> x = {'a': 1, 'b': 2, 'c': {'d': 3}}
        >>> y = clone(x)
        >>> y == y
        True
        >>> x is y
        False
        >>> x['c'] is y['c']
        True

    Returns:
        Cloned object.

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Moved 'iteratee' parameter to :func:`clone_with`.
    """
    return base_clone(value)


@t.overload
def clone_with(
    value: t.Mapping[T, T2], customizer: t.Callable[[T2, T, t.Mapping[T, T2]], T3]
) -> t.Dict[T, t.Union[T2, T3]]:
    ...


@t.overload
def clone_with(
    value: t.Mapping[T, T2], customizer: t.Callable[[T2, T], T3]
) -> t.Dict[T, t.Union[T2, T3]]:
    ...


@t.overload
def clone_with(
    value: t.Mapping[T, T2], customizer: t.Callable[[T2], T3]
) -> t.Dict[T, t.Union[T2, T3]]:
    ...


@t.overload
def clone_with(
    value: t.List[T], customizer: t.Callable[[T, int, t.List[T]], T2]
) -> t.List[t.Union[T, T2]]:
    ...


@t.overload
def clone_with(value: t.List[T], customizer: t.Callable[[T, int], T2]) -> t.List[t.Union[T, T2]]:
    ...


@t.overload
def clone_with(value: t.List[T], customizer: t.Callable[[T], T2]) -> t.List[t.Union[T, T2]]:
    ...


@t.overload
def clone_with(value: T, customizer: None = None) -> T:
    ...


@t.overload
def clone_with(value: t.Any, customizer: t.Callable) -> t.Any:
    ...


def clone_with(value, customizer=None):
    """
    This method is like :func:`clone` except that it accepts customizer which is invoked to produce
    the cloned value. If customizer returns ``None``, cloning is handled by the method instead. The
    customizer is invoked with up to three arguments: ``(value, index|key, object)``.

    Args:
        value: Object to clone.
        customizer: Function to customize cloning.

    Returns:
        Cloned object.

    Example:

        >>> x = {'a': 1, 'b': 2, 'c': {'d': 3}}
        >>> cbk = lambda v, k: v + 2 if isinstance(v, int) and k else None
        >>> y = clone_with(x, cbk)
        >>> y == {'a': 3, 'b': 4, 'c': {'d': 3}}
        True
    """
    return base_clone(value, customizer=customizer)


def clone_deep(value: T) -> T:
    """
    Creates a deep clone of `value`. If an iteratee is provided it will be executed to produce the
    cloned values.

    Args:
        value: Object to clone.

    Returns:
        Cloned object.

    Example:

        >>> x = {'a': 1, 'b': 2, 'c': {'d': 3}}
        >>> y = clone_deep(x)
        >>> y == y
        True
        >>> x is y
        False
        >>> x['c'] is y['c']
        False

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Moved 'iteratee' parameter to :func:`clone_deep_with`.
    """
    return base_clone(value, is_deep=True)


@t.overload
def clone_deep_with(
    value: t.Mapping[T, T2], customizer: t.Callable[[T2, T, t.Mapping[T, T2]], T3]
) -> t.Dict[T, t.Union[T2, T3]]:
    ...


@t.overload
def clone_deep_with(
    value: t.Mapping[T, T2], customizer: t.Callable[[T2, T], T3]
) -> t.Dict[T, t.Union[T2, T3]]:
    ...


@t.overload
def clone_deep_with(
    value: t.Mapping[T, T2], customizer: t.Callable[[T2], T3]
) -> t.Dict[T, t.Union[T2, T3]]:
    ...


@t.overload
def clone_deep_with(
    value: t.List[T], customizer: t.Callable[[T, int, t.List[T]], T2]
) -> t.List[t.Union[T, T2]]:
    ...


@t.overload
def clone_deep_with(
    value: t.List[T], customizer: t.Callable[[T, int], T2]
) -> t.List[t.Union[T, T2]]:
    ...


@t.overload
def clone_deep_with(value: t.List[T], customizer: t.Callable[[T], T2]) -> t.List[t.Union[T, T2]]:
    ...


@t.overload
def clone_deep_with(value: T, customizer: None = None) -> T:
    ...


@t.overload
def clone_deep_with(value: t.Any, customizer: t.Callable) -> t.Any:
    ...


def clone_deep_with(value, customizer=None):
    """
    This method is like :func:`clone_with` except that it recursively clones `value`.

    Args:
        value: Object to clone.
        customizer: Function to customize cloning.

    Returns:
        Cloned object.
    """
    return base_clone(value, is_deep=True, customizer=customizer)


def defaults(
    obj: t.Dict[T, T2], *sources: t.Dict[T3, T4]
) -> t.Dict[t.Union[T, T3], t.Union[T2, T4]]:
    """
    Assigns properties of source object(s) to the destination object for all destination properties
    that resolve to undefined.

    Args:
        obj: Destination object whose properties will be modified.
        sources: Source objects to assign to `obj`.

    Returns:
        Modified `obj`.

    Warning:
        `obj` is modified in place.

    Example:

        >>> obj = {'a': 1}
        >>> obj2 = defaults(obj, {'b': 2}, {'c': 3}, {'a': 4})
        >>> obj is obj2
        True
        >>> obj == {'a': 1, 'b': 2, 'c': 3}
        True

    .. versionadded:: 1.0.0
    """
    for source in sources:
        for key, value in source.items():
            obj.setdefault(key, value)  # type: ignore

    return obj  # type: ignore


def defaults_deep(
    obj: t.Dict[T, T2], *sources: t.Dict[T3, T4]
) -> t.Dict[t.Union[T, T3], t.Union[T2, T4]]:
    """
    This method is like :func:`defaults` except that it recursively assigns default properties.

    Args:
        obj: Destination object whose properties will be modified.
        sources: Source objects to assign to `obj`.

    Returns:
        Modified `obj`.

    Warning:
        `obj` is modified in place.

    Example:

        >>> obj = {'a': {'b': 1}}
        >>> obj2 = defaults_deep(obj, {'a': {'b': 2, 'c': 3}})
        >>> obj is obj2
        True
        >>> obj == {'a': {'b': 1, 'c': 3}}
        True

    .. versionadded:: 3.3.0
    """

    def setter(obj, key, value):
        if hasattr(obj, "setdefault"):
            obj.setdefault(key, value)

    return merge_with(obj, *sources, _setter=setter)


@t.overload
def find_key(
    obj: t.Mapping[T, T2], predicate: t.Callable[[T2, T, t.Dict[T, T2]], t.Any]
) -> t.Union[T, None]:
    ...


@t.overload
def find_key(obj: t.Mapping[T, T2], predicate: t.Callable[[T2, T], t.Any]) -> t.Union[T, None]:
    ...


@t.overload
def find_key(obj: t.Mapping[T, T2], predicate: t.Callable[[T2], t.Any]) -> t.Union[T, None]:
    ...


@t.overload
def find_key(obj: t.Mapping[T, t.Any], predicate: None = None) -> t.Union[T, None]:
    ...


@t.overload
def find_key(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int, t.List[T]], t.Any]
) -> t.Union[int, None]:
    ...


@t.overload
def find_key(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int], t.Any]
) -> t.Union[int, None]:
    ...


@t.overload
def find_key(collection: t.Iterable[T], iteratee: t.Callable[[T], t.Any]) -> t.Union[int, None]:
    ...


@t.overload
def find_key(collection: t.Iterable[t.Any], iteratee: None = None) -> t.Union[int, None]:
    ...


def find_key(obj, predicate=None):
    """
    This method is like :func:`pydash.arrays.find_index` except that it returns the key of the first
    element that passes the predicate check, instead of the element itself.

    Args:
        obj: Object to search.
        predicate: Predicate applied per iteration.

    Returns:
        Found key or ``None``.

    Example:

        >>> find_key({'a': 1, 'b': 2, 'c': 3}, lambda x: x == 1)
        'a'
        >>> find_key([1, 2, 3, 4], lambda x: x == 1)
        0

    .. versionadded:: 1.0.0
    """
    for result, _, key, _ in iteriteratee(obj, predicate):
        if result:
            return key


@t.overload
def find_last_key(
    obj: t.Mapping[T, T2], predicate: t.Callable[[T2, T, t.Dict[T, T2]], t.Any]
) -> t.Union[T, None]:
    ...


@t.overload
def find_last_key(obj: t.Mapping[T, T2], predicate: t.Callable[[T2, T], t.Any]) -> t.Union[T, None]:
    ...


@t.overload
def find_last_key(obj: t.Mapping[T, T2], predicate: t.Callable[[T2], t.Any]) -> t.Union[T, None]:
    ...


@t.overload
def find_last_key(obj: t.Mapping[T, t.Any], predicate: None = None) -> t.Union[T, None]:
    ...


@t.overload
def find_last_key(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int, t.List[T]], t.Any]
) -> t.Union[int, None]:
    ...


@t.overload
def find_last_key(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int], t.Any]
) -> t.Union[int, None]:
    ...


@t.overload
def find_last_key(
    collection: t.Iterable[T], iteratee: t.Callable[[T], t.Any]
) -> t.Union[int, None]:
    ...


@t.overload
def find_last_key(collection: t.Iterable[t.Any], iteratee: None = None) -> t.Union[int, None]:
    ...


def find_last_key(obj, predicate=None):
    """
    This method is like :func:`find_key` except that it iterates over elements of a collection in
    the opposite order.

    Args:
        obj: Object to search.
        predicate: Predicate applied per iteration.

    Returns:
        Found key or ``None``.

    Example:

        >>> find_last_key({'a': 1, 'b': 2, 'c': 3}, lambda x: x == 1)
        'a'
        >>> find_last_key([1, 2, 3, 1], lambda x: x == 1)
        3

    .. versionchanged:: 4.0.0
        Made into its own function (instead of an alias of ``find_key``) with
        proper reverse find implementation.
    """
    reversed_obj = reversed(list(iteriteratee(obj, predicate)))
    for result, _, key, _ in reversed_obj:
        if result:
            return key


@t.overload
def for_in(
    obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T, t.Dict[T, T2]], t.Any]
) -> t.Dict[T, T2]:
    ...


@t.overload
def for_in(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], t.Any]) -> t.Dict[T, T2]:
    ...


@t.overload
def for_in(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2], t.Any]) -> t.Dict[T, T2]:
    ...


@t.overload
def for_in(obj: t.Mapping[T, T2], iteratee: None = None) -> t.Dict[T, T2]:
    ...


@t.overload
def for_in(obj: t.Sequence[T], iteratee: t.Callable[[T, int, t.List[T]], t.Any]) -> t.List[T]:
    ...


@t.overload
def for_in(obj: t.Sequence[T], iteratee: t.Callable[[T, int], t.Any]) -> t.List[T]:
    ...


@t.overload
def for_in(obj: t.Sequence[T], iteratee: t.Callable[[T], t.Any]) -> t.List[T]:
    ...


@t.overload
def for_in(obj: t.Sequence[T], iteratee: None = None) -> t.List[T]:
    ...


def for_in(obj, iteratee=None):
    """
    Iterates over own and inherited enumerable properties of `obj`, executing `iteratee` for each
    property.

    Args:
        obj: Object to process.
        iteratee: Iteratee applied per iteration.

    Returns:
        `obj`.

    Example:

        >>> obj = {}
        >>> def cb(v, k): obj[k] = v
        >>> results = for_in({'a': 1, 'b': 2, 'c': 3}, cb)
        >>> results == {'a': 1, 'b': 2, 'c': 3}
        True
        >>> obj == {'a': 1, 'b': 2, 'c': 3}
        True

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Removed alias ``for_own``.
    """
    walk = (None for ret, _, _, _ in iteriteratee(obj, iteratee) if ret is False)
    next(walk, None)
    return obj


@t.overload
def for_in_right(
    obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T, t.Dict[T, T2]], t.Any]
) -> t.Dict[T, T2]:
    ...


@t.overload
def for_in_right(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], t.Any]) -> t.Dict[T, T2]:
    ...


@t.overload
def for_in_right(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2], t.Any]) -> t.Dict[T, T2]:
    ...


@t.overload
def for_in_right(obj: t.Mapping[T, T2], iteratee: None = None) -> t.Dict[T, T2]:
    ...


@t.overload
def for_in_right(obj: t.Sequence[T], iteratee: t.Callable[[T, int, t.List[T]], t.Any]) -> t.List[T]:
    ...


@t.overload
def for_in_right(obj: t.Sequence[T], iteratee: t.Callable[[T, int], t.Any]) -> t.List[T]:
    ...


@t.overload
def for_in_right(obj: t.Sequence[T], iteratee: t.Callable[[T], t.Any]) -> t.List[T]:
    ...


@t.overload
def for_in_right(obj: t.Sequence[T], iteratee: None = None) -> t.List[T]:
    ...


def for_in_right(obj, iteratee=None):
    """
    This function is like :func:`for_in` except it iterates over the properties in reverse order.

    Args:
        obj: Object to process.
        iteratee: Iteratee applied per iteration.

    Returns:
        `obj`.

    Example:

        >>> data = {'product': 1}
        >>> def cb(v): data['product'] *= v
        >>> for_in_right([1, 2, 3, 4], cb)
        [1, 2, 3, 4]
        >>> data['product'] == 24
        True

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Removed alias ``for_own_right``.
    """
    walk = (None for ret, _, _, _ in iteriteratee(obj, iteratee, reverse=True) if ret is False)
    next(walk, None)
    return obj


@t.overload
def get(obj: t.List[T], path: int, default: T2) -> t.Union[T, T2]:
    ...


@t.overload
def get(obj: t.List[T], path: int, default: None = None) -> t.Union[T, None]:
    ...


@t.overload
def get(obj: t.Any, path: PathT, default: t.Any = None) -> t.Any:
    ...


def get(obj: t.Any, path: PathT, default: t.Any = None) -> t.Any:
    """
    Get the value at any depth of a nested object based on the path described by `path`. If path
    doesn't exist, `default` is returned.

    Args:
        obj: Object to process.
        path: List or ``.`` delimited string of path describing path.
        default: Default value to return if path doesn't exist. Defaults to ``None``.

    Returns:
        Value of `obj` at path.

    Example:

        >>> get({}, 'a.b.c') is None
        True
        >>> get({'a': {'b': {'c': [1, 2, 3, 4]}}}, 'a.b.c[1]')
        2
        >>> get({'a': {'b': {'c': [1, 2, 3, 4]}}}, 'a.b.c.1')
        2
        >>> get({'a': {'b': [0, {'c': [1, 2]}]}}, 'a.b.1.c.1')
        2
        >>> get({'a': {'b': [0, {'c': [1, 2]}]}}, ['a', 'b', 1, 'c', 1])
        2
        >>> get({'a': {'b': [0, {'c': [1, 2]}]}}, 'a.b.1.c.2') is None
        True

    .. versionadded:: 2.0.0

    .. versionchanged:: 2.2.0
        Support escaping "." delimiter in single string path key.

    .. versionchanged:: 3.3.0

        - Added :func:`get` as main definition and :func:`get_path` as alias.
        - Made :func:`deep_get` an alias.

    .. versionchanged:: 3.4.7
        Fixed bug where an iterable default was iterated over instead of being returned when an
        object path wasn't found.

    .. versionchanged:: 4.0.0

        - Support attribute access on `obj` if item access fails.
        - Removed aliases ``get_path`` and ``deep_get``.

    .. versionchanged:: 4.7.6
        Fixed bug where getattr is used on Mappings and Sequence in Python 3.5+
    """
    if default is UNSET:
        # When NoValue given for default, then this method will raise if path is not present in obj.
        sentinel = default
    else:
        # When a returnable default is given, use a sentinel value to detect when base_get() returns
        # a default value for a missing path, so we can exit early from the loop and not mistakenly
        # iterate over the default.
        sentinel = object()

    for key in to_path(path):
        obj = base_get(obj, key, default=sentinel)

        if obj is sentinel:
            # Path doesn't exist so set return obj to the default.
            obj = default
            break

    return obj


def has(obj: t.Any, path: PathT) -> bool:
    """
    Checks if `path` exists as a key of `obj`.

    Args:
        obj: Object to test.
        path: Path to test for. Can be a list of nested keys or a ``.`` delimited string of
            path describing the path.

    Returns:
        Whether `obj` has `path`.

    Example:

        >>> has([1, 2, 3], 1)
        True
        >>> has({'a': 1, 'b': 2}, 'b')
        True
        >>> has({'a': 1, 'b': 2}, 'c')
        False
        >>> has({'a': {'b': [0, {'c': [1, 2]}]}}, 'a.b.1.c.1')
        True
        >>> has({'a': {'b': [0, {'c': [1, 2]}]}}, 'a.b.1.c.2')
        False

    .. versionadded:: 1.0.0

    .. versionchanged:: 3.0.0
        Return ``False`` on ``ValueError`` when checking path.

    .. versionchanged:: 3.3.0

        - Added :func:`deep_has` as alias.
        - Added :func:`has_path` as alias.

    .. versionchanged:: 4.0.0
        Removed aliases ``deep_has`` and ``has_path``.
    """
    try:
        get(obj, path, default=UNSET)
        exists = True
    except (KeyError, IndexError, TypeError, ValueError):
        exists = False

    return exists


@t.overload
def invert(obj: t.Mapping[T, T2]) -> t.Dict[T2, T]:
    ...


@t.overload
def invert(obj: t.Iterable[T]) -> t.Dict[T, int]:
    ...


def invert(obj) -> t.Dict:
    """
    Creates an object composed of the inverted keys and values of the given object.

    Args:
        obj: Dict to invert.

    Returns:
        Inverted dict.

    Example:

        >>> results = invert({'a': 1, 'b': 2, 'c': 3})
        >>> results == {1: 'a', 2: 'b', 3: 'c'}
        True

    Note:
        Assumes `obj` values are hashable as ``dict`` keys.

    .. versionadded:: 1.0.0

    .. versionchanged:: 2.0.0
        Added ``multivalue`` argument.

    .. versionchanged:: 4.0.0
        Moved ``multivalue=True`` functionality to :func:`invert_by`.
    """
    return {value: key for key, value in iterator(obj)}


@t.overload
def invert_by(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2], T3]) -> t.Dict[T3, t.List[T]]:
    ...


@t.overload
def invert_by(obj: t.Mapping[T, T2], iteratee: None = None) -> t.Dict[T2, t.List[T]]:
    ...


@t.overload
def invert_by(obj: t.Iterable[T], iteratee: t.Callable[[T], T2]) -> t.Dict[T2, t.List[int]]:
    ...


@t.overload
def invert_by(obj: t.Iterable[T], iteratee: None = None) -> t.Dict[T, t.List[int]]:
    ...


def invert_by(obj, iteratee=None):
    """
    This method is like :func:`invert` except that the inverted object is generated from the results
    of running each element of object through iteratee. The corresponding inverted value of each
    inverted key is a list of keys responsible for generating the inverted value. The iteratee is
    invoked with one argument: ``(value)``.

    Args:
        obj: Object to invert.
        iteratee: Iteratee applied per iteration.

    Returns:
        Inverted dict.

    Example:

        >>> obj = {'a': 1, 'b': 2, 'c': 1}
        >>> results = invert_by(obj)  # {1: ['a', 'c'], 2: ['b']}
        >>> set(results[1]) == set(['a', 'c'])
        True
        >>> set(results[2]) == set(['b'])
        True
        >>> results2 = invert_by(obj, lambda value: 'group' + str(value))
        >>> results2['group1'] == results[1]
        True
        >>> results2['group2'] == results[2]
        True

    Note:
        Assumes `obj` values are hashable as ``dict`` keys.

    .. versionadded:: 4.0.0
    """
    callback = pyd.iteratee(iteratee)
    result = {}

    for key, value in iterator(obj):
        result.setdefault(callback(value), []).append(key)

    return result


def invoke(obj: t.Any, path: PathT, *args: t.Any, **kwargs: t.Any) -> t.Any:
    """
    Invokes the method at path of object.

    Args:
        obj: The object to query.
        path: The path of the method to invoke.
        args: Arguments to pass to method call.
        kwargs: Keyword arguments to pass to method call.

    Returns:
        Result of the invoked method.

    Example:

        >>> obj = {'a': [{'b': {'c': [1, 2, 3, 4]}}]}
        >>> invoke(obj, 'a[0].b.c.pop', 1)
        2
        >>> obj
        {'a': [{'b': {'c': [1, 3, 4]}}]}

    .. versionadded:: 1.0.0
    """
    paths = to_path(path)
    target_path = pyd.initial(paths)
    method_name = pyd.last(paths)

    try:
        # potential error is caught
        method = getattr(get(obj, target_path), method_name)  # type: ignore
    except AttributeError:
        ret = None
    else:
        ret = method(*args, **kwargs)

    return ret


@t.overload
def keys(obj: t.Iterable[T]) -> t.List[T]:
    ...


@t.overload
def keys(obj: t.Any) -> t.List:
    ...


def keys(obj):
    """
    Creates a list composed of the keys of `obj`.

    Args:
        obj: Object to extract keys from.

    Returns:
        List of keys.

    Example:

        >>> keys([1, 2, 3])
        [0, 1, 2]
        >>> set(keys({'a': 1, 'b': 2, 'c': 3})) == set(['a', 'b', 'c'])
        True

    .. versionadded:: 1.0.0

    .. versionchanged:: 1.1.0
        Added ``keys_in`` as alias.

    .. versionchanged:: 4.0.0
        Removed alias ``keys_in``.
    """
    return [key for key, _ in iterator(obj)]


@t.overload
def map_keys(
    obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T, t.Dict[T, T2]], T3]
) -> t.Dict[T3, T2]:
    ...


@t.overload
def map_keys(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], T3]) -> t.Dict[T3, T2]:
    ...


@t.overload
def map_keys(obj: t.Mapping[t.Any, T2], iteratee: t.Callable[[T2], T3]) -> t.Dict[T3, T2]:
    ...


@t.overload
def map_keys(obj: t.Iterable[T], iteratee: t.Callable[[T, int, t.List[T]], T2]) -> t.Dict[T2, T]:
    ...


@t.overload
def map_keys(obj: t.Iterable[T], iteratee: t.Callable[[T, int], T2]) -> t.Dict[T2, T]:
    ...


@t.overload
def map_keys(obj: t.Iterable[T], iteratee: t.Callable[[T], T2]) -> t.Dict[T2, T]:
    ...


@t.overload
def map_keys(obj: t.Iterable, iteratee: t.Union[IterateeObjT, None] = None) -> t.Dict:
    ...


def map_keys(obj, iteratee=None):
    """
    The opposite of :func:`map_values`, this method creates an object with the same values as object
    and keys generated by running each own enumerable string keyed property of object through
    iteratee. The iteratee is invoked with three arguments: ``(value, key, object)``.

    Args:
        obj: Object to map.
        iteratee: Iteratee applied per iteration.

    Returns:
        Results of running `obj` through `iteratee`.

    Example:

        >>> callback = lambda value, key: key * 2
        >>> results = map_keys({'a': 1, 'b': 2, 'c': 3}, callback)
        >>> results == {'aa': 1, 'bb': 2, 'cc': 3}
        True

    .. versionadded:: 3.3.0
    """
    return {result: value for result, value, _, _ in iteriteratee(obj, iteratee)}


@t.overload
def map_values(
    obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T, t.Dict[T, T2]], T3]
) -> t.Dict[T, T3]:
    ...


@t.overload
def map_values(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], T3]) -> t.Dict[T, T3]:
    ...


@t.overload
def map_values(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2], T3]) -> t.Dict[T, T3]:
    ...


@t.overload
def map_values(obj: t.Iterable[T], iteratee: t.Callable[[T, int, t.List[T]], T2]) -> t.Dict[T, T2]:
    ...


@t.overload
def map_values(obj: t.Iterable[T], iteratee: t.Callable[[T, int], T2]) -> t.Dict[T, T2]:
    ...


@t.overload
def map_values(obj: t.Iterable[T], iteratee: t.Callable[[T], T2]) -> t.Dict[T, T2]:
    ...


@t.overload
def map_values(obj: t.Iterable, iteratee: t.Union[IterateeObjT, None] = None) -> t.Dict:
    ...


def map_values(obj, iteratee=None):
    """
    Creates an object with the same keys as object and values generated by running each string keyed
    property of object through iteratee. The iteratee is invoked with three arguments: ``(value,
    key, object)``.

    Args:
        obj: Object to map.
        iteratee: Iteratee applied per iteration.

    Returns:
        Results of running `obj` through `iteratee`.

    Example:

        >>> results = map_values({'a': 1, 'b': 2, 'c': 3}, lambda x: x * 2)
        >>> results == {'a': 2, 'b': 4, 'c': 6}
        True
        >>> results = map_values({'a': 1, 'b': {'d': 4}, 'c': 3}, {'d': 4})
        >>> results == {'a': False, 'b': True, 'c': False}
        True

    .. versionadded:: 1.0.0
    """
    return {key: result for result, _, key, _ in iteriteratee(obj, iteratee)}


def map_values_deep(
    obj: t.Iterable, iteratee: t.Union[t.Callable, None] = None, property_path: t.Any = UNSET
) -> t.Any:
    """
    Map all non-object values in `obj` with return values from `iteratee`. The iteratee is invoked
    with two arguments: ``(obj_value, property_path)`` where ``property_path`` contains the list of
    path keys corresponding to the path of ``obj_value``.

    Args:
        obj: Object to map.
        iteratee: Iteratee applied to each value.
        property_path: Path key(s) to access.

    Returns:
        The modified object.

    Warning:
        `obj` is modified in place.

    Example:

        >>> x = {'a': 1, 'b': {'c': 2}}
        >>> y = map_values_deep(x, lambda val: val * 2)
        >>> y == {'a': 2, 'b': {'c': 4}}
        True
        >>> z = map_values_deep(x, lambda val, props: props)
        >>> z == {'a': ['a'], 'b': {'c': ['b', 'c']}}
        True

    .. versionadded: 2.2.0

    .. versionchanged:: 3.0.0
        Allow iteratees to accept partial arguments.

    .. versionchanged:: 4.0.0
        Renamed from ``deep_map_values`` to ``map_values_deep``.
    """
    properties = to_path(property_path)

    if pyd.is_object(obj):

        def deep_iteratee(value, key):
            return map_values_deep(value, iteratee, pyd.flatten([properties, key]))

        return assign(obj, map_values(obj, deep_iteratee))  # type: ignore
    else:
        return callit(iteratee, obj, properties)


@t.overload
def merge(
    obj: t.Mapping[T, T2], *sources: t.Mapping[T3, T4]
) -> t.Dict[t.Union[T, T3], t.Union[T2, T4]]:
    ...


@t.overload
def merge(obj: t.Sequence[T], *sources: t.Sequence[T2]) -> t.List[t.Union[T, T2]]:
    ...


def merge(obj, *sources):
    """
    Recursively merges properties of the source object(s) into the destination object. Subsequent
    sources will overwrite property assignments of previous sources.

    Args:
        obj: Destination object to merge source(s) into.
        sources: Source objects to merge from. subsequent sources overwrite previous ones.

    Returns:
        Merged object.

    Warning:
        `obj` is modified in place.

    Example:

        >>> obj = {'a': 2}
        >>> obj2 = merge(obj, {'a': 1}, {'b': 2, 'c': 3}, {'d': 4})
        >>> obj2 == {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        True
        >>> obj is obj2
        True

    .. versionadded:: 1.0.0

    .. versionchanged:: 2.3.2
        Apply :func:`clone_deep` to each `source` before assigning to `obj`.

    .. versionchanged:: 2.3.2
        Allow `iteratee` to be passed by reference if it is the last positional argument.

    .. versionchanged:: 4.0.0
        Moved iteratee argument to :func:`merge_with`.

    .. versionchanged:: 4.9.3
        Fixed regression in v4.8.0 that caused exception when `obj` was ``None``.
    """
    return merge_with(obj, *sources)


def merge_with(obj: t.Any, *sources: t.Any, **kwargs: t.Any) -> t.Any:
    """
    This method is like :func:`merge` except that it accepts customizer which is invoked to produce
    the merged values of the destination and source properties. If customizer returns ``None``,
    merging is handled by this method instead. The customizer is invoked with five arguments:
    ``(obj_value, src_value, key, obj, source)``.

    Args:
        obj: Destination object to merge source(s) into.
        sources: Source objects to merge from. subsequent sources
            overwrite previous ones.

    Keyword Args:
        iteratee: Iteratee function to handle merging
            (must be passed in as keyword argument).

    Returns:
        Merged object.

    Warning:
        `obj` is modified in place.

    Example:

        >>> cbk = lambda obj_val, src_val: obj_val + src_val
        >>> obj1 = {'a': [1], 'b': [2]}
        >>> obj2 = {'a': [3], 'b': [4]}
        >>> res = merge_with(obj1, obj2, cbk)
        >>> obj1 == {'a': [1, 3], 'b': [2, 4]}
        True

    .. versionadded:: 4.0.0

    .. versionchanged:: 4.9.3
        Fixed regression in v4.8.0 that caused exception when `obj` was ``None``.
    """
    if obj is None:
        return None

    list_sources = list(sources)
    iteratee = kwargs.pop("iteratee", None)

    if iteratee is None and list_sources and callable(list_sources[-1]):
        iteratee = list_sources.pop()

    list_sources = [copy.deepcopy(source) for source in list_sources]

    if callable(iteratee):
        iteratee = partial(callit, iteratee, argcount=getargcount(iteratee, maxargs=5))
    else:
        iteratee = None

    return _merge_with(obj, *list_sources, iteratee=iteratee, **kwargs)


def _merge_with(obj, *sources, **kwargs):
    iteratee = kwargs.get("iteratee")
    setter = kwargs.get("_setter")

    if setter is None:
        setter = base_set

    for source in sources:
        for key, src_value in iterator(source):
            obj_value = base_get(obj, key, default=None)
            all_sequences = isinstance(src_value, list) and isinstance(obj_value, list)
            all_mappings = isinstance(src_value, dict) and isinstance(obj_value, dict)

            _result = None
            if iteratee:
                _result = iteratee(obj_value, src_value, key, obj, source)

            if _result is not None:
                result = _result
            elif all_sequences or all_mappings:
                result = _merge_with(obj_value, src_value, iteratee=iteratee, _setter=setter)
            else:
                result = src_value

            setter(obj, key, result)

    return obj


@t.overload
def omit(obj: t.Mapping[T, T2], *properties: PathT) -> t.Dict[T, T2]:
    ...


@t.overload
def omit(obj: t.Iterable[T], *properties: PathT) -> t.Dict[int, T]:
    ...


@t.overload
def omit(obj: t.Any, *properties: PathT) -> t.Dict:
    ...


def omit(obj, *properties):
    """
    The opposite of :func:`pick`. This method creates an object composed of the property paths of
    `obj` that are not omitted.

    Args:
        obj: Object to process.
        *properties: Property values to omit.

    Returns:
        Results of omitting properties.

    Example:

        >>> omit({'a': 1, 'b': 2, 'c': 3}, 'b', 'c') == {'a': 1}
        True
        >>> omit({'a': 1, 'b': 2, 'c': 3 }, ['a', 'c']) == {'b': 2}
        True
        >>> omit([1, 2, 3, 4], 0, 3) == {1: 2, 2: 3}
        True
        >>> omit({'a': {'b': {'c': 'd'}}}, 'a.b.c') == {'a': {'b': {}}}
        True

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Moved iteratee argument to :func:`omit_by`.

    .. versionchanged:: 4.2.0
        Support deep paths.
    """
    return omit_by(obj, pyd.flatten(properties))


@t.overload
def omit_by(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], t.Any]) -> t.Dict[T, T2]:
    ...


@t.overload
def omit_by(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2], t.Any]) -> t.Dict[T, T2]:
    ...


@t.overload
def omit_by(obj: t.Dict[T, T2], iteratee: None = None) -> t.Dict[T, T2]:
    ...


@t.overload
def omit_by(obj: t.Iterable[T], iteratee: t.Callable[[T, int], t.Any]) -> t.Dict[int, T]:
    ...


@t.overload
def omit_by(obj: t.Iterable[T], iteratee: t.Callable[[T], t.Any]) -> t.Dict[int, T]:
    ...


@t.overload
def omit_by(obj: t.List[T], iteratee: None = None) -> t.Dict[int, T]:
    ...


@t.overload
def omit_by(obj: t.Any, iteratee: t.Union[t.Callable, None] = None) -> t.Dict:
    ...


def omit_by(obj, iteratee=None):
    """
    The opposite of :func:`pick_by`. This method creates an object composed of the string keyed
    properties of object that predicate doesn't return truthy for. The predicate is invoked with two
    arguments: ``(value, key)``.

    Args:
        obj: Object to process.
        iteratee: Iteratee used to determine which properties to omit.

    Returns:
        Results of omitting properties.

    Example:

        >>> omit_by({'a': 1, 'b': '2', 'c': 3}, lambda v: isinstance(v, int))
        {'b': '2'}

    .. versionadded:: 4.0.0

    .. versionchanged:: 4.2.0
        Support deep paths for `iteratee`.
    """
    if not callable(iteratee):
        paths = pyd.map_(iteratee, to_path)

        if any(len(path) > 1 for path in paths):
            cloned = clone_deep(obj)
        else:
            cloned = to_dict(obj)

        def _unset(obj, path):
            pyd.unset(obj, path)
            return obj

        ret = pyd.reduce_(paths, _unset, cloned)
    else:
        argcount = getargcount(iteratee, maxargs=2)

        ret = {
            key: value
            for key, value in iterator(obj)
            if not callit(iteratee, value, key, argcount=argcount)
        }

    return ret


def parse_int(value: t.Any, radix: t.Union[int, None] = None) -> t.Union[int, None]:
    """
    Converts the given `value` into an integer of the specified `radix`. If `radix` is falsey, a
    radix of ``10`` is used unless the `value` is a hexadecimal, in which case a radix of 16 is
    used.

    Args:
        value: Value to parse.
        radix: Base to convert to.

    Returns:
        Integer if parsable else ``None``.

    Example:

        >>> parse_int('5')
        5
        >>> parse_int('12', 8)
        10
        >>> parse_int('x') is None
        True

    .. versionadded:: 1.0.0
    """
    if not radix and pyd.is_string(value):
        try:
            # Check if value is hexadecimal and if so use base-16 conversion.
            int(value, 16)
        except ValueError:
            pass
        else:
            radix = 16

    if not radix:
        radix = 10

    try:
        # NOTE: Must convert value to string when supplying radix to int(). Dropping radix arg when
        # 10 is needed to allow floats to parse correctly.
        args = (value,) if radix == 10 else (to_string(value), radix)
        parsed = int(*args)
    except (ValueError, TypeError):
        parsed = None

    return parsed


@t.overload
def pick(obj: t.Mapping[T, T2], *properties: PathT) -> t.Dict[T, T2]:
    ...


@t.overload
def pick(obj: t.Union[t.Tuple[T, ...], t.List[T]], *properties: PathT) -> t.Dict[int, T]:
    ...


@t.overload
def pick(obj: t.Any, *properties: PathT) -> t.Dict:
    ...


def pick(obj, *properties):
    """
    Creates an object composed of the picked object properties.

    Args:
        obj: Object to pick from.
        properties: Property values to pick.

    Returns:
        Dict containing picked properties.

    Example:

        >>> pick({'a': 1, 'b': 2, 'c': 3}, 'a', 'b') == {'a': 1, 'b': 2}
        True

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Moved iteratee argument to :func:`pick_by`.
    """
    return pick_by(obj, pyd.flatten(properties))


@t.overload
def pick_by(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2], t.Any]) -> t.Dict[T, T2]:
    ...


@t.overload
def pick_by(obj: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], t.Any]) -> t.Dict[T, T2]:
    ...


@t.overload
def pick_by(obj: t.Dict[T, T2], iteratee: None = None) -> t.Dict[T, T2]:
    ...


@t.overload
def pick_by(
    obj: t.Union[t.Tuple[T, ...], t.List[T]], iteratee: t.Callable[[T, int], t.Any]
) -> t.Dict[int, T]:
    ...


@t.overload
def pick_by(
    obj: t.Union[t.Tuple[T, ...], t.List[T]], iteratee: t.Callable[[T], t.Any]
) -> t.Dict[int, T]:
    ...


@t.overload
def pick_by(obj: t.Union[t.Tuple[T, ...], t.List[T]], iteratee: None = None) -> t.Dict[int, T]:
    ...


@t.overload
def pick_by(obj: t.Any, iteratee: t.Union[t.Callable, None] = None) -> t.Dict:
    ...


def pick_by(obj, iteratee=None):
    """
    Creates an object composed of the object properties predicate returns truthy for. The predicate
    is invoked with two arguments: ``(value, key)``.

    Args:
        obj: Object to pick from.
        iteratee: Iteratee used to determine which properties to pick.

    Returns:
        Dict containing picked properties.

    Example:

        >>> obj = {'a': 1, 'b': '2', 'c': 3 }
        >>> pick_by(obj, lambda v: isinstance(v, int)) == {'a': 1, 'c': 3}
        True

    .. versionadded:: 4.0.0
    """
    obj = to_dict(obj)

    if iteratee is None or callable(iteratee):
        paths = keys(obj)
        if iteratee is None:
            iteratee = pyd.identity
            argcount = 1
        else:
            argcount = getargcount(iteratee, maxargs=2)
    else:
        paths = iteratee if iteratee is not None else []

        def iteratee(value, path):  # pylint: disable=function-redefined
            return has(obj, path)

        argcount = 2

    result = {}

    for path in paths:
        value = get(obj, path)

        if callit(iteratee, value, path, argcount=argcount):
            set_(result, path, value)

    return result


def rename_keys(obj: t.Dict[T, T2], key_map: t.Dict[t.Any, T3]) -> t.Dict[t.Union[T, T3], T2]:
    """
    Rename the keys of `obj` using `key_map` and return new object.

    Args:
        obj: Object to rename.
        key_map: Renaming map whose keys correspond to existing keys in `obj` and whose
            values are the new key name.

    Returns:
        Renamed `obj`.

    Example:

        >>> obj = rename_keys({'a': 1, 'b': 2, 'c': 3}, {'a': 'A', 'b': 'B'})
        >>> obj == {'A': 1, 'B': 2, 'c': 3}
        True

    .. versionadded:: 2.0.0
    """
    return {key_map.get(key, key): value for key, value in obj.items()}


def set_(obj: T, path: PathT, value: t.Any) -> T:
    """
    Sets the value of an object described by `path`. If any part of the object path doesn't exist,
    it will be created.

    Args:
        obj: Object to modify.
        path: Target path to set value to.
        value: Value to set.

    Returns:
        Modified `obj`.

    Warning:
        `obj` is modified in place.

    Example:

        >>> set_({}, 'a.b.c', 1)
        {'a': {'b': {'c': 1}}}
        >>> set_({}, 'a.0.c', 1)
        {'a': {'0': {'c': 1}}}
        >>> set_([1, 2], '[2][0]', 1)
        [1, 2, [1]]
        >>> set_({}, 'a.b[0].c', 1)
        {'a': {'b': [{'c': 1}]}}

    .. versionadded:: 2.2.0

    .. versionchanged:: 3.3.0
        Added :func:`set_` as main definition and :func:`deep_set` as alias.

    .. versionchanged:: 4.0.0

        - Modify `obj` in place.
        - Support creating default path values as ``list`` or ``dict`` based on whether key or index
          substrings are used.
        - Remove alias ``deep_set``.
    """
    return set_with(obj, path, value)


def set_with(obj: T, path: PathT, value: t.Any, customizer: t.Union[t.Callable, None] = None) -> T:
    """
    This method is like :func:`set_` except that it accepts customizer which is invoked to produce
    the objects of path. If customizer returns undefined path creation is handled by the method
    instead. The customizer is invoked with three arguments: ``(nested_value, key, nested_object)``.

    Args:
        obj: Object to modify.
        path: Target path to set value to.
        value: Value to set.
        customizer: The function to customize assigned values.

    Returns:
        Modified `obj`.

    Warning:
        `obj` is modified in place.

    Example:

        >>> set_with({}, '[0][1]', 'a', lambda: {})
        {0: {1: 'a'}}

    .. versionadded:: 4.0.0

    .. versionchanged:: 4.3.1
        Fixed bug where a callable `value` was called when being set.
    """
    return update_with(obj, path, pyd.constant(value), customizer=customizer)


def to_boolean(
    obj: t.Any,
    true_values: t.Tuple[str, ...] = ("true", "1"),
    false_values: t.Tuple[str, ...] = ("false", "0"),
) -> t.Union[bool, None]:
    """
    Convert `obj` to boolean. This is not like the builtin ``bool`` function. By default, commonly
    considered strings values are converted to their boolean equivalent, i.e., ``'0'`` and
    ``'false'`` are converted to ``False`` while ``'1'`` and ``'true'`` are converted to ``True``.
    If a string value is provided that isn't recognized as having a common boolean conversion, then
    the returned value is ``None``. Non-string values of `obj` are converted using ``bool``.
    Optionally, `true_values` and `false_values` can be overridden but each value must be a string.

    Args:
        obj: Object to convert.
        true_values: Values to consider ``True``. Each value must be a string.
            Comparision is case-insensitive. Defaults to ``('true', '1')``.
        false_values: Values to consider ``False``. Each value must be a string.
            Comparision is case-insensitive. Defaults to ``('false', '0')``.

    Returns:
        Boolean value of `obj`.

    Example:

        >>> to_boolean('true')
        True
        >>> to_boolean('1')
        True
        >>> to_boolean('false')
        False
        >>> to_boolean('0')
        False
        >>> assert to_boolean('a') is None

    .. versionadded:: 3.0.0
    """
    if pyd.is_string(obj):
        obj = obj.strip()

        def boolean_match(text, vals):
            if text.lower() in [val.lower() for val in vals]:
                return True
            else:
                return re.match("|".join(vals), text)

        if true_values and boolean_match(obj, true_values):
            value = True
        elif false_values and boolean_match(obj, false_values):
            value = False
        else:
            value = None
    else:
        value = bool(obj)

    return value


@t.overload
def to_dict(obj: t.Mapping[T, T2]) -> t.Dict[T, T2]:
    ...


@t.overload
def to_dict(obj: t.Iterable[T]) -> t.Dict[int, T]:
    ...


@t.overload
def to_dict(obj: t.Any) -> t.Dict:
    ...


def to_dict(obj):
    """
    Convert `obj` to ``dict`` by creating a new ``dict`` using `obj` keys and values.

    Args:
        obj: Object to convert.

    Returns:
        Object converted to ``dict``.

    Example:

        >>> obj = {'a': 1, 'b': 2}
        >>> obj2 = to_dict(obj)
        >>> obj2 == obj
        True
        >>> obj2 is not obj
        True

    .. versionadded:: 3.0.0

    .. versionchanged:: 4.0.0
        Removed alias ``to_plain_object``.

    .. versionchanged:: 4.2.0
        Use ``pydash.helpers.iterator`` to generate key/value pairs.

    .. versionchanged:: 4.7.1
        Try to convert to ``dict`` using ``dict()`` first, then fallback to using
        ``pydash.helpers.iterator``.
    """
    return dict(iterator(obj))


def to_integer(obj: t.Any) -> int:
    """
    Converts `obj` to an integer.

    Args:
        obj: Object to convert.

    Returns:
        Converted integer or ``0`` if it can't be converted.

    Example:

        >>> to_integer(3.2)
        3
        >>> to_integer('3.2')
        3
        >>> to_integer('3.9')
        3
        >>> to_integer('invalid')
        0

    .. versionadded:: 4.0.0
    """
    try:
        # Convert to float first to handle converting floats as string since int('1.1') would fail
        # but this won't.
        num = int(float(obj))
    except (ValueError, TypeError):
        num = 0

    return num


@t.overload
def to_list(obj: t.Dict[t.Any, T], split_strings: bool = True) -> t.List[T]:
    ...


@t.overload
def to_list(obj: t.Iterable[T], split_strings: bool = True) -> t.List[T]:
    ...


@t.overload
def to_list(obj: T, split_strings: bool = True) -> t.List[T]:
    ...


def to_list(obj, split_strings=True):
    """
    Converts an obj, an iterable or a single item to a list.

    Args:
        obj: Object to convert item or wrap.
        split_strings: Whether to split strings into single chars. Defaults to
            ``True``.

    Returns:
        Converted obj or wrapped item.

    Example:

        >>> results = to_list({'a': 1, 'b': 2, 'c': 3})
        >>> assert set(results) == set([1, 2, 3])

        >>> to_list((1, 2, 3, 4))
        [1, 2, 3, 4]

        >>> to_list(1)
        [1]

        >>> to_list([1])
        [1]

        >>> to_list(a for a in [1, 2, 3])
        [1, 2, 3]

        >>> to_list('cat')
        ['c', 'a', 't']

        >>> to_list('cat', split_strings=False)
        ['cat']

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.3.0

        - Wrap non-iterable items in a list.
        - Convert other iterables to list.
        - Byte objects are returned as single character strings in Python 3.
    """
    if isinstance(obj, list):
        return obj[:]
    elif isinstance(obj, dict):
        return obj.values()
    elif not split_strings and isinstance(obj, (str, bytes)):
        return [obj]
    elif split_strings and isinstance(obj, bytes):
        # in python3 iterating over bytes gives integers instead of strings
        return list(chr(c) if isinstance(c, int) else c for c in obj)
    else:
        try:
            return list(obj)
        except TypeError:
            return [obj]


def to_number(obj: t.Any, precision: int = 0) -> t.Union[float, None]:
    """
    Convert `obj` to a number. All numbers are retuned as ``float``. If precision is negative, round
    `obj` to the nearest positive integer place. If `obj` can't be converted to a number, ``None``
    is returned.

    Args:
        obj: Object to convert.
        precision: Precision to round number to. Defaults to ``0``.

    Returns:
        Converted number or ``None`` if it can't be converted.

    Example:

        >>> to_number('1234.5678')
        1235.0
        >>> to_number('1234.5678', 4)
        1234.5678
        >>> to_number(1, 2)
        1.0

    .. versionadded:: 3.0.0
    """
    try:
        factor = pow(10, precision)

        if precision < 0:
            # Round down since negative `precision` means we are going to the nearest positive
            # integer place.
            rounder: t.Callable = math.floor
        else:
            rounder = round

        num = rounder(float(obj) * factor) / factor
    except Exception:
        num = None

    return num


@t.overload
def to_pairs(obj: t.Mapping[T, T2]) -> t.List[t.List[t.Union[T, T2]]]:
    ...


@t.overload
def to_pairs(obj: t.Iterable[T]) -> t.List[t.List[t.Union[int, T]]]:
    ...


@t.overload
def to_pairs(obj: t.Any) -> t.List:
    ...


def to_pairs(obj):
    """
    Creates a two-dimensional list of an object's key-value pairs, i.e., ``[[key1, value1], [key2,
    value2]]``.

    Args:
        obj: Object to process.

    Returns:
        Two dimensional list of object's key-value pairs.

    Example:

        >>> to_pairs([1, 2, 3, 4])
        [[0, 1], [1, 2], [2, 3], [3, 4]]
        >>> to_pairs({'a': 1})
        [['a', 1]]

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Renamed from ``pairs`` to ``to_pairs``.
    """
    return [[key, value] for key, value in iterator(obj)]


def to_string(obj: t.Any) -> str:
    """
    Converts an object to string.

    Args:
        obj: Object to convert.

    Returns:
        String representation of `obj`.

    Example:

        >>> to_string(1) == '1'
        True
        >>> to_string(None) == ''
        True
        >>> to_string([1, 2, 3]) == '[1, 2, 3]'
        True
        >>> to_string('a') == 'a'
        True

    .. versionadded:: 2.0.0

    .. versionchanged:: 3.0.0
        Convert ``None`` to empty string.
    """
    if pyd.is_string(obj):
        res = obj
    elif obj is None:
        res = ""
    else:
        res = str(obj)
    return res


@t.overload
def transform(
    obj: t.Mapping[T, T2], iteratee: t.Callable[[T3, T2, T, t.Dict[T, T2]], t.Any], accumulator: T3
) -> T3:
    ...


@t.overload
def transform(
    obj: t.Mapping[T, T2], iteratee: t.Callable[[T3, T2, T], t.Any], accumulator: T3
) -> T3:
    ...


@t.overload
def transform(
    obj: t.Mapping[t.Any, T2], iteratee: t.Callable[[T3, T2], t.Any], accumulator: T3
) -> T3:
    ...


@t.overload
def transform(
    obj: t.Mapping[t.Any, t.Any], iteratee: t.Callable[[T3], t.Any], accumulator: T3
) -> T3:
    ...


@t.overload
def transform(
    obj: t.Iterable[T], iteratee: t.Callable[[T3, T, int, t.List[T]], t.Any], accumulator: T3
) -> T3:
    ...


@t.overload
def transform(obj: t.Iterable[T], iteratee: t.Callable[[T3, T, int], t.Any], accumulator: T3) -> T3:
    ...


@t.overload
def transform(obj: t.Iterable[T], iteratee: t.Callable[[T3, T], t.Any], accumulator: T3) -> T3:
    ...


@t.overload
def transform(obj: t.Iterable[t.Any], iteratee: t.Callable[[T3], t.Any], accumulator: T3) -> T3:
    ...


@t.overload
def transform(obj: t.Any, iteratee: t.Any = None, accumulator: t.Any = None) -> t.Any:
    ...


def transform(obj, iteratee=None, accumulator=None):
    """
    An alernative to :func:`pydash.collections.reduce`, this method transforms `obj` to a new
    accumulator object which is the result of running each of its properties through an iteratee,
    with each iteratee execution potentially mutating the accumulator object. The iteratee is
    invoked with four arguments: ``(accumulator, value, key, object)``. Iteratees may exit iteration
    early by explicitly returning ``False``.

    Args:
        obj: Object to process.
        iteratee: Iteratee applied per iteration.
        accumulator: Accumulated object. Defaults to ``list``.

    Returns:
        Accumulated object.

    Example:

        >>> transform([1, 2, 3, 4], lambda acc, v, k: acc.append((k, v)))
        [(0, 1), (1, 2), (2, 3), (3, 4)]

    .. versionadded:: 1.0.0
    """
    if iteratee is None:
        iteratee = pyd.identity
        argcount = 1
    else:
        argcount = getargcount(iteratee, maxargs=4)

    if accumulator is None:
        accumulator = []

    walk = (
        None
        for key, item in iterator(obj)
        if callit(iteratee, accumulator, item, key, obj, argcount=argcount) is False
    )
    next(walk, None)

    return accumulator


@t.overload
def update(
    obj: t.Dict[t.Any, T2],
    path: PathT,
    updater: t.Callable[[T2], t.Any],
) -> t.Dict:
    ...


@t.overload
def update(
    obj: t.List[T],
    path: PathT,
    updater: t.Callable[[T], t.Any],
) -> t.List:
    ...


@t.overload
def update(
    obj: T,
    path: PathT,
    updater: t.Callable,
) -> T:
    ...


def update(obj, path, updater):
    """
    This method is like :func:`set_` except that accepts updater to produce the value to set. Use
    :func:`update_with` to customize path creation. The updater is invoked with one argument:
    ``(value)``.

    Args:
        obj: Object to modify.
        path: A string or list of keys that describe the object path to modify.
        updater: Function that returns updated value.

    Returns:
        Updated `obj`.

    Warning:
        `obj` is modified in place.

    Example:

        >>> update({}, ['a', 'b'], lambda value: value)
        {'a': {'b': None}}
        >>> update([], [0, 0], lambda value: 1)
        [[1]]

    .. versionadded:: 4.0.0
    """
    return update_with(obj, path, updater)


@t.overload
def update_with(
    obj: t.Dict[t.Any, T2],
    path: PathT,
    updater: t.Callable[[T2], t.Any],
    customizer: t.Union[t.Callable, None],
) -> t.Dict:
    ...


@t.overload
def update_with(
    obj: t.List[T],
    path: PathT,
    updater: t.Callable[[T], t.Any],
    customizer: t.Union[t.Callable, None] = None,
) -> t.List:
    ...


@t.overload
def update_with(
    obj: T,
    path: PathT,
    updater: t.Callable,
    customizer: t.Union[t.Callable, None] = None,
) -> T:
    ...


def update_with(obj, path, updater, customizer=None):  # noqa: C901
    """
    This method is like :func:`update` except that it accepts customizer which is invoked to produce
    the objects of path. If customizer returns ``None``, path creation is handled by the method
    instead. The customizer is invoked with three arguments: ``(nested_value, key, nested_object)``.

    Args:
        obj: Object to modify.
        path: A string or list of keys that describe the object path to modify.
        updater: Function that returns updated value.
        customizer: The function to customize assigned values.

    Returns:
        Updated `obj`.

    Warning:
        `obj` is modified in place.

    Example:

        >>> update_with({}, '[0][1]', lambda: 'a', lambda: {})
        {0: {1: 'a'}}

    .. versionadded:: 4.0.0
    """
    if not callable(updater):
        updater = pyd.constant(updater)

    if customizer is not None and not callable(customizer):
        call_customizer = partial(callit, clone, customizer, argcount=1)
    elif customizer:
        call_customizer = partial(callit, customizer, argcount=getargcount(customizer, maxargs=3))
    else:
        call_customizer = None

    default_type = dict if isinstance(obj, dict) else list
    tokens = to_path_tokens(path)

    if not pyd.is_list(tokens):  # pragma: no cover
        tokens = [tokens]

    last_key = pyd.last(tokens)

    if isinstance(last_key, PathToken):
        last_key = last_key.key

    target = obj

    for idx, token in enumerate(pyd.initial(tokens)):
        if isinstance(token, PathToken):
            key = token.key
            default_factory = pyd.get(tokens, [idx + 1, "default_factory"], default=default_type)
        else:
            key = token
            default_factory = default_type

        obj_val = base_get(target, key, default=None)
        path_obj = None

        if call_customizer:
            path_obj = call_customizer(obj_val, key, target)

        if path_obj is None:
            path_obj = default_factory()

        base_set(target, key, path_obj, allow_override=False)

        try:
            target = base_get(target, key, default=None)
        except TypeError as exc:  # pragma: no cover
            try:
                target = target[int(key)]
                _failed = False
            except Exception:
                _failed = True

            if _failed:
                raise TypeError(f"Unable to update object at index {key!r}. {exc}")

    value = base_get(target, last_key, default=None)
    base_set(target, last_key, callit(updater, value))

    return obj


def unset(obj: t.Union[t.List, t.Dict], path: PathT) -> bool:  # noqa: C901
    """
    Removes the property at `path` of `obj`.

    Note:
        Only ``list``, ``dict``, or objects with a ``pop()`` method can be unset by this function.

    Args:
        obj: The object to modify.
        path: The path of the property to unset.

    Returns:
        Whether the property was deleted.

    Warning:
        `obj` is modified in place.

    Example:

        >>> obj = {'a': [{'b': {'c': 7}}]}
        >>> unset(obj, 'a[0].b.c')
        True
        >>> obj
        {'a': [{'b': {}}]}
        >>> unset(obj, 'a[0].b.c')
        False
    """
    tokens = to_path_tokens(path)

    if not pyd.is_list(tokens):  # pragma: no cover
        tokens = [tokens]

    last_key = pyd.last(tokens)

    if isinstance(last_key, PathToken):
        last_key = last_key.key

    target = obj

    for token in pyd.initial(tokens):
        if isinstance(token, PathToken):
            key = token.key
        else:
            key = token

        try:
            try:
                target = target[key]
            except TypeError:
                target = target[int(key)]
        except Exception:
            # Allow different types reassignment
            target = UNSET  # type: ignore

        if target is UNSET:
            break

    did_unset = False

    if target is not UNSET:
        try:
            try:
                target.pop(last_key)
                did_unset = True
            except TypeError:
                target.pop(int(last_key))
                did_unset = True
        except Exception:
            pass

    return did_unset


@t.overload
def values(obj: t.Mapping[t.Any, T2]) -> t.List[T2]:
    ...


@t.overload
def values(obj: t.Iterable[T]) -> t.List[T]:
    ...


@t.overload
def values(obj: t.Any) -> t.List:
    ...


def values(obj):
    """
    Creates a list composed of the values of `obj`.

    Args:
        obj: Object to extract values from.

    Returns:
        List of values.

    Example:

        >>> results = values({'a': 1, 'b': 2, 'c': 3})
        >>> set(results) == set([1, 2, 3])
        True
        >>> values([2, 4, 6, 8])
        [2, 4, 6, 8]

    .. versionadded:: 1.0.0

    .. versionchanged:: 1.1.0
        Added ``values_in`` as alias.

    .. versionchanged:: 4.0.0
        Removed alias ``values_in``.
    """
    return [value for _, value in iterator(obj)]


#
# Utility methods not a part of the main API
#


def base_clone(value, is_deep=False, customizer=None, key=None, _cloned=False):
    """Base clone function that supports deep clone and customizer callback."""
    clone_by = copy.deepcopy if is_deep else copy.copy
    result = None

    if callable(customizer) and not _cloned:
        argcount = getargcount(customizer, maxargs=4)
        cbk = partial(callit, customizer, argcount=argcount)
    elif _cloned:
        cbk = customizer
    else:
        cbk = None

    if cbk:
        result = cbk(value, key, value)

    if result is not None:
        return result

    if not _cloned:
        result = clone_by(value)
    else:
        result = value

    if cbk and not pyd.is_string(value) and not isinstance(value, bytes):
        for key, subvalue in iterator(value):
            if is_deep:
                val = base_clone(subvalue, is_deep, cbk, key, _cloned=True)
            else:
                val = cbk(subvalue, key, value)

            if val is not None:
                result[key] = val

    return result
