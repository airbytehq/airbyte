"""
Numerical/mathematical related functions.

.. versionadded:: 2.1.0
"""

import math
import operator
import typing as t

import pydash as pyd

from .helpers import UNSET, Unset, iterator, iterator_with_default, iteriteratee
from .types import IterateeObjT, NumberNoDecimalT, NumberT, SupportsMul, SupportsRound


if t.TYPE_CHECKING:
    from decimal import Decimal  # pragma: no cover

    from _typeshed import SupportsAdd, SupportsRichComparisonT, SupportsSub  # pragma: no cover


__all__ = (
    "add",
    "ceil",
    "clamp",
    "divide",
    "floor",
    "max_",
    "max_by",
    "mean",
    "mean_by",
    "median",
    "min_",
    "min_by",
    "moving_mean",
    "multiply",
    "power",
    "round_",
    "scale",
    "slope",
    "std_deviation",
    "sum_",
    "sum_by",
    "subtract",
    "transpose",
    "variance",
    "zscore",
)

T = t.TypeVar("T")
T2 = t.TypeVar("T2")
T3 = t.TypeVar("T3")


INFINITY = float("inf")


@t.overload
def add(a: "SupportsAdd[T, T2]", b: T) -> T2:
    ...


@t.overload
def add(a: T, b: "SupportsAdd[T, T2]") -> T2:
    ...


def add(a, b):
    """
    Adds two numbers.

    Args:
        a: First number to add.
        b: Second number to add.

    Returns:
        number

    Example:

        >>> add(10, 5)
        15

    .. versionadded:: 2.1.0

    .. versionchanged:: 3.3.0
        Support adding two numbers when passed as positional arguments.

    .. versionchanged:: 4.0.0
        Only support two argument addition.
    """
    return a + b


@t.overload
def sum_(collection: t.Mapping[t.Any, "SupportsAdd[int, T]"]) -> T:
    ...


@t.overload
def sum_(collection: t.Iterable["SupportsAdd[int, T]"]) -> T:
    ...


def sum_(collection):
    """
    Sum each element in `collection`.

    Args:
        collection: Collection to process or first number to add.

    Returns:
        Result of summation.

    Example:

        >>> sum_([1, 2, 3, 4])
        10

    .. versionadded:: 2.1.0

    .. versionchanged:: 3.3.0
        Support adding two numbers when passed as positional arguments.

    .. versionchanged:: 4.0.0
        Move iteratee support to :func:`sum_by`. Move two argument addition to
        :func:`add`.
    """
    return sum_by(collection)


@t.overload
def sum_by(
    collection: t.Mapping[T, T2],
    iteratee: t.Callable[[T2, T, t.Dict[T, T2]], "SupportsAdd[int, T3]"],
) -> T3:
    ...


@t.overload
def sum_by(
    collection: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], "SupportsAdd[int, T3]"]
) -> T3:
    ...


@t.overload
def sum_by(
    collection: t.Mapping[t.Any, T2], iteratee: t.Callable[[T2], "SupportsAdd[int, T3]"]
) -> T3:
    ...


@t.overload
def sum_by(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int, t.List[T]], "SupportsAdd[int, T2]"]
) -> T2:
    ...


@t.overload
def sum_by(collection: t.Iterable[T], iteratee: t.Callable[[T, int], "SupportsAdd[int, T2]"]) -> T2:
    ...


@t.overload
def sum_by(collection: t.Iterable[T], iteratee: t.Callable[[T], "SupportsAdd[int, T2]"]) -> T2:
    ...


@t.overload
def sum_by(collection: t.Mapping[t.Any, "SupportsAdd[int, T]"], iteratee: None = None) -> T:
    ...


@t.overload
def sum_by(collection: t.Iterable["SupportsAdd[int, T]"], iteratee: None = None) -> T:
    ...


def sum_by(collection, iteratee=None):
    """
    Sum each element in `collection`. If iteratee is passed, each element of `collection` is passed
    through an iteratee before the summation is computed.

    Args:
        collection: Collection to process or first number to add.
        iteratee: Iteratee applied per iteration or second number to add.

    Returns:
        Result of summation.

    Example:

        >>> sum_by([1, 2, 3, 4], lambda x: x ** 2)
        30

    .. versionadded:: 4.0.0
    """
    return sum(result[0] for result in iteriteratee(collection, iteratee))


@t.overload
def mean(collection: t.Mapping[t.Any, "SupportsAdd[int, t.Any]"]) -> float:
    ...


@t.overload
def mean(collection: t.Iterable["SupportsAdd[int, t.Any]"]) -> float:
    ...


def mean(collection):
    """
    Calculate arithmetic mean of each element in `collection`.

    Args:
        collection: Collection to process.

    Returns:
        Result of mean.

    Example:

        >>> mean([1, 2, 3, 4])
        2.5

    .. versionadded:: 2.1.0

    .. versionchanged:: 4.0.0

        - Removed ``average`` and ``avg`` aliases.
        - Moved iteratee functionality to :func:`mean_by`.
    """
    return mean_by(collection)


@t.overload
def mean_by(
    collection: t.Mapping[T, T2],
    iteratee: t.Callable[[T2, T, t.Dict[T, T2]], "SupportsAdd[int, t.Any]"],
) -> float:
    ...


@t.overload
def mean_by(
    collection: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], "SupportsAdd[int, t.Any]"]
) -> float:
    ...


@t.overload
def mean_by(
    collection: t.Mapping[t.Any, T2], iteratee: t.Callable[[T2], "SupportsAdd[int, t.Any]"]
) -> float:
    ...


@t.overload
def mean_by(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int, t.List[T]], "SupportsAdd[int, t.Any]"]
) -> float:
    ...


@t.overload
def mean_by(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int], "SupportsAdd[int, t.Any]"]
) -> float:
    ...


@t.overload
def mean_by(
    collection: t.Iterable[T], iteratee: t.Callable[[T], "SupportsAdd[int, t.Any]"]
) -> float:
    ...


@t.overload
def mean_by(
    collection: t.Mapping[t.Any, "SupportsAdd[int, t.Any]"], iteratee: None = None
) -> float:
    ...


@t.overload
def mean_by(collection: t.Iterable["SupportsAdd[int, t.Any]"], iteratee: None = None) -> float:
    ...


def mean_by(collection, iteratee=None):
    """
    Calculate arithmetic mean of each element in `collection`. If iteratee is passed, each element
    of `collection` is passed through an iteratee before the mean is computed.

    Args:
        collection: Collection to process.
        iteratee: Iteratee applied per iteration.

    Returns:
        Result of mean.

    Example:

        >>> mean_by([1, 2, 3, 4], lambda x: x ** 2)
        7.5

    .. versionadded:: 4.0.0
    """
    return sum_by(collection, iteratee) / len(collection)


def ceil(x: NumberT, precision: int = 0) -> float:
    """
    Round number up to precision.

    Args:
        x: Number to round up.
        precision: Rounding precision. Defaults to ``0``.

    Returns:
        Number rounded up.

    Example:

        >>> ceil(3.275) == 4.0
        True
        >>> ceil(3.215, 1) == 3.3
        True
        >>> ceil(6.004, 2) == 6.01
        True

    .. versionadded:: 3.3.0
    """
    return rounder(math.ceil, x, precision)


NumT = t.TypeVar("NumT", int, float, "Decimal")
NumT2 = t.TypeVar("NumT2", int, float, "Decimal")
NumT3 = t.TypeVar("NumT3", int, float, "Decimal")


def clamp(x: NumT, lower: NumT2, upper: t.Union[NumT3, None] = None) -> t.Union[NumT, NumT2, NumT3]:
    """
    Clamps number within the inclusive lower and upper bounds.

    Args:
        x: Number to clamp.
        lower: Lower bound.
        upper: Upper bound

    Returns:
        number

    Example:

        >>> clamp(-10, -5, 5)
        -5
        >>> clamp(10, -5, 5)
        5
        >>> clamp(10, 5)
        5
        >>> clamp(-10, 5)
        -10

    .. versionadded:: 4.0.0
    """
    if upper is None:
        upper = lower  # type: ignore
        lower = x  # type: ignore

    if x < lower:
        x = lower  # type: ignore
    elif x > upper:  # type: ignore
        x = upper  # type: ignore

    return x


def divide(dividend: t.Union[NumberT, None], divisor: t.Union[NumberT, None]) -> float:
    """
    Divide two numbers.

    Args:
        dividend: The first number in a division.
        divisor: The second number in a division.

    Returns:
        Returns the quotient.

    Example:

        >>> divide(20, 5)
        4.0
        >>> divide(1.5, 3)
        0.5
        >>> divide(None, None)
        1.0
        >>> divide(5, None)
        5.0

    .. versionadded:: 4.0.0
    """
    return call_math_operator(dividend, divisor, operator.truediv, 1)


def floor(x: NumberT, precision: int = 0) -> float:
    """
    Round number down to precision.

    Args:
        x: Number to round down.
        precision: Rounding precision. Defaults to ``0``.

    Returns:
        Number rounded down.

    Example:

        >>> floor(3.75) == 3.0
        True
        >>> floor(3.215, 1) == 3.2
        True
        >>> floor(0.046, 2) == 0.04
        True

    .. versionadded:: 3.3.0
    """
    return rounder(math.floor, x, precision)


@t.overload
def max_(
    collection: t.Mapping[t.Any, "SupportsRichComparisonT"], default: Unset = UNSET
) -> "SupportsRichComparisonT":
    ...


@t.overload
def max_(
    collection: t.Mapping[t.Any, "SupportsRichComparisonT"], default: T
) -> t.Union["SupportsRichComparisonT", T]:
    ...


@t.overload
def max_(
    collection: t.Iterable["SupportsRichComparisonT"], default: Unset = UNSET
) -> "SupportsRichComparisonT":
    ...


@t.overload
def max_(
    collection: t.Iterable["SupportsRichComparisonT"], default: T
) -> t.Union["SupportsRichComparisonT", T]:
    ...


def max_(collection, default=UNSET):
    """
    Retrieves the maximum value of a `collection`.

    Args:
        collection: Collection to iterate over.
        default: Value to return if `collection` is empty.

    Returns:
        Maximum value.

    Example:

        >>> max_([1, 2, 3, 4])
        4
        >>> max_([], default=-1)
        -1

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Moved iteratee iteratee support to :func:`max_by`.
    """
    return max_by(collection, default=default)


@t.overload
def max_by(
    collection: t.Mapping[t.Any, "SupportsRichComparisonT"],
    iteratee: None = None,
    default: Unset = UNSET,
) -> "SupportsRichComparisonT":
    ...


@t.overload
def max_by(
    collection: t.Mapping[t.Any, T2],
    iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
    default: Unset = UNSET,
) -> T2:
    ...


@t.overload
def max_by(
    collection: t.Mapping[t.Any, T2],
    iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
    *,
    default: T
) -> t.Union[T2, T]:
    ...


@t.overload
def max_by(
    collection: t.Mapping[t.Any, "SupportsRichComparisonT"], iteratee: None = None, *, default: T
) -> t.Union["SupportsRichComparisonT", T]:
    ...


@t.overload
def max_by(
    collection: t.Iterable["SupportsRichComparisonT"], iteratee: None = None, default: Unset = UNSET
) -> "SupportsRichComparisonT":
    ...


@t.overload
def max_by(
    collection: t.Iterable[T2],
    iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
    default: Unset = UNSET,
) -> T2:
    ...


@t.overload
def max_by(
    collection: t.Iterable[T2], iteratee: t.Callable[[T2], "SupportsRichComparisonT"], *, default: T
) -> t.Union[T2, T]:
    ...


@t.overload
def max_by(
    collection: t.Iterable["SupportsRichComparisonT"], iteratee: None = None, *, default: T
) -> t.Union["SupportsRichComparisonT", T]:
    ...


@t.overload
def max_by(collection: t.Iterable[T], iteratee: IterateeObjT, default: Unset = UNSET) -> T:
    ...


@t.overload
def max_by(collection: t.Iterable[T], iteratee: IterateeObjT, default: T2) -> t.Union[T, T2]:
    ...


def max_by(collection, iteratee=None, default=UNSET):
    """
    Retrieves the maximum value of a `collection`.

    Args:
        collection: Collection to iterate over.
        iteratee: Iteratee applied per iteration.
        default: Value to return if `collection` is empty.

    Returns:
        Maximum value.

    Example:

        >>> max_by([1.0, 1.5, 1.8], math.floor)
        1.0
        >>> max_by([{'a': 1}, {'a': 2}, {'a': 3}], 'a')
        {'a': 3}
        >>> max_by([], default=-1)
        -1

    .. versionadded:: 4.0.0
    """
    if isinstance(collection, dict):
        collection = collection.values()

    return max(iterator_with_default(collection, default), key=pyd.iteratee(iteratee))


@t.overload
def median(
    collection: t.Mapping[T, T2], iteratee: t.Callable[[T2, T, t.Dict[T, T2]], NumberT]
) -> t.Union[float, int]:
    ...


@t.overload
def median(
    collection: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], NumberT]
) -> t.Union[float, int]:
    ...


@t.overload
def median(
    collection: t.Mapping[t.Any, T2], iteratee: t.Callable[[T2], NumberT]
) -> t.Union[float, int]:
    ...


@t.overload
def median(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int, t.List[T]], NumberT]
) -> t.Union[float, int]:
    ...


@t.overload
def median(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int], NumberT]
) -> t.Union[float, int]:
    ...


@t.overload
def median(collection: t.Iterable[T], iteratee: t.Callable[[T], NumberT]) -> t.Union[float, int]:
    ...


@t.overload
def median(collection: t.Iterable[NumberT], iteratee: None = None) -> t.Union[float, int]:
    ...


def median(collection, iteratee=None):
    """
    Calculate median of each element in `collection`. If iteratee is passed, each element of
    `collection` is passed through an iteratee before the median is computed.

    Args:
        collection: Collection to process.
        iteratee: Iteratee applied per iteration.

    Returns:
        Result of median.

    Example:

        >>> median([1, 2, 3, 4, 5])
        3
        >>> median([1, 2, 3, 4])
        2.5

    .. versionadded:: 2.1.0
    """
    length = len(collection)
    middle = (length + 1) / 2
    collection = sorted(ret[0] for ret in iteriteratee(collection, iteratee))

    if pyd.is_odd(length):
        result = collection[int(middle - 1)]
    else:
        left = int(middle - 1.5)
        right = int(middle - 0.5)
        result = (collection[left] + collection[right]) / 2

    return result


@t.overload
def min_(
    collection: t.Mapping[t.Any, "SupportsRichComparisonT"], default: Unset = UNSET
) -> "SupportsRichComparisonT":
    ...


@t.overload
def min_(
    collection: t.Mapping[t.Any, "SupportsRichComparisonT"], default: T
) -> t.Union["SupportsRichComparisonT", T]:
    ...


@t.overload
def min_(
    collection: t.Iterable["SupportsRichComparisonT"], default: Unset = UNSET
) -> "SupportsRichComparisonT":
    ...


@t.overload
def min_(
    collection: t.Iterable["SupportsRichComparisonT"], default: T
) -> t.Union["SupportsRichComparisonT", T]:
    ...


def min_(collection, default=UNSET):
    """
    Retrieves the minimum value of a `collection`.

    Args:
        collection: Collection to iterate over.
        default: Value to return if `collection` is empty.

    Returns:
        Minimum value.

    Example:

        >>> min_([1, 2, 3, 4])
        1
        >>> min_([], default=100)
        100

    .. versionadded:: 1.0.0

    .. versionchanged:: 4.0.0
        Moved iteratee iteratee support to :func:`min_by`.
    """
    return min_by(collection, default=default)


@t.overload
def min_by(
    collection: t.Mapping[t.Any, "SupportsRichComparisonT"],
    iteratee: None = None,
    default: Unset = UNSET,
) -> "SupportsRichComparisonT":
    ...


@t.overload
def min_by(
    collection: t.Mapping[t.Any, T2],
    iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
    default: Unset = UNSET,
) -> T2:
    ...


@t.overload
def min_by(
    collection: t.Mapping[t.Any, T2],
    iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
    *,
    default: T
) -> t.Union[T2, T]:
    ...


@t.overload
def min_by(
    collection: t.Mapping[t.Any, "SupportsRichComparisonT"], iteratee: None = None, *, default: T
) -> t.Union["SupportsRichComparisonT", T]:
    ...


@t.overload
def min_by(
    collection: t.Iterable["SupportsRichComparisonT"], iteratee: None = None, default: Unset = UNSET
) -> "SupportsRichComparisonT":
    ...


@t.overload
def min_by(
    collection: t.Iterable[T2],
    iteratee: t.Callable[[T2], "SupportsRichComparisonT"],
    default: Unset = UNSET,
) -> T2:
    ...


@t.overload
def min_by(
    collection: t.Iterable[T2], iteratee: t.Callable[[T2], "SupportsRichComparisonT"], *, default: T
) -> t.Union[T2, T]:
    ...


@t.overload
def min_by(
    collection: t.Iterable["SupportsRichComparisonT"], iteratee: None = None, *, default: T
) -> t.Union["SupportsRichComparisonT", T]:
    ...


@t.overload
def min_by(collection: t.Iterable[T], iteratee: IterateeObjT, default: Unset = UNSET) -> T:
    ...


@t.overload
def min_by(collection: t.Iterable[T], iteratee: IterateeObjT, default: T2) -> t.Union[T, T2]:
    ...


def min_by(collection, iteratee=None, default=UNSET):
    """
    Retrieves the minimum value of a `collection`.

    Args:
        collection: Collection to iterate over.
        iteratee: Iteratee applied per iteration.
        default: Value to return if `collection` is empty.

    Returns:
        Minimum value.

    Example:

        >>> min_by([1.8, 1.5, 1.0], math.floor)
        1.8
        >>> min_by([{'a': 1}, {'a': 2}, {'a': 3}], 'a')
        {'a': 1}
        >>> min_by([], default=100)
        100

    .. versionadded:: 4.0.0
    """
    if isinstance(collection, dict):
        collection = collection.values()
    return min(iterator_with_default(collection, default), key=pyd.iteratee(iteratee))


def moving_mean(array: t.Sequence["SupportsAdd[int, t.Any]"], size: t.SupportsInt) -> t.List[float]:
    """
    Calculate moving mean of each element of `array`.

    Args:
        array: List to process.
        size: Window size.

    Returns:
        Result of moving average.

    Example:

        >>> moving_mean(range(10), 1)
        [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
        >>> moving_mean(range(10), 5)
        [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        >>> moving_mean(range(10), 10)
        [4.5]

    .. versionadded:: 2.1.0

    .. versionchanged:: 4.0.0
        Rename to ``moving_mean`` and remove ``moving_average`` and ``moving_avg`` aliases.
    """
    result = []
    size = int(size)

    for i in range(size - 1, len(array) + 1):
        window = array[i - size : i]

        if len(window) == size:
            result.append(mean(window))

    return result


@t.overload
def multiply(multiplier: SupportsMul[int, T2], multiplicand: None) -> T2:
    ...


@t.overload
def multiply(multiplier: None, multiplicand: SupportsMul[int, T2]) -> T2:
    ...


@t.overload
def multiply(multiplier: None, multiplicand: None) -> int:
    ...


@t.overload
def multiply(multiplier: SupportsMul[T, T2], multiplicand: T) -> T2:
    ...


@t.overload
def multiply(multiplier: T, multiplicand: SupportsMul[T, T2]) -> T2:
    ...


def multiply(multiplier, multiplicand):
    """
    Multiply two numbers.

    Args:
        multiplier: The first number in a multiplication.
        multiplicand: The second number in a multiplication.

    Returns:
        Returns the product.

    Example:

        >>> multiply(4, 5)
        20
        >>> multiply(10, 4)
        40
        >>> multiply(None, 10)
        10
        >>> multiply(None, None)
        1

    .. versionadded:: 4.0.0
    """
    return call_math_operator(multiplier, multiplicand, operator.mul, 1)


@t.overload
def power(x: int, n: int) -> t.Union[int, float]:
    ...


@t.overload
def power(x: float, n: t.Union[int, float]) -> float:
    ...


@t.overload
def power(x: t.List[int], n: int) -> t.List[t.Union[int, float]]:
    ...


@t.overload
def power(x: t.List[float], n: t.List[t.Union[int, float]]) -> t.List[float]:
    ...


def power(x, n):
    """
    Calculate exponentiation of `x` raised to the `n` power.

    Args:
        x: Base number.
        n: Exponent.

    Returns:
        Result of calculation.

    Example:

        >>> power(5, 2)
        25
        >>> power(12.5, 3)
        1953.125

    .. versionadded:: 2.1.0

    .. versionchanged:: 4.0.0
        Removed alias ``pow_``.
    """
    if pyd.is_number(x):
        result = pow(x, n)
    elif pyd.is_list(x):
        result = [pow(item, n) for item in x]
    else:
        result = None

    return result


@t.overload
def round_(x: t.List[SupportsRound[NumberT]], precision: int = 0) -> t.List[float]:
    ...


@t.overload
def round_(x: SupportsRound[NumberT], precision: int = 0) -> float:
    ...


def round_(x, precision=0):
    """
    Round number to precision.

    Args:
        x: Number to round.
        precision: Rounding precision. Defaults to ``0``.

    Returns:
        Rounded number.

    Example:

        >>> round_(3.275) == 3.0
        True
        >>> round_(3.275, 1) == 3.3
        True

    .. versionadded:: 2.1.0

    .. versionchanged:: 4.0.0
        Remove alias ``curve``.
    """
    return rounder(round, x, precision)


@t.overload
def scale(array: t.Iterable["Decimal"], maximum: "Decimal") -> t.List["Decimal"]:
    ...


@t.overload
def scale(array: t.Iterable[NumberNoDecimalT], maximum: NumberNoDecimalT) -> t.List[float]:
    ...


@t.overload
def scale(array: t.Iterable[NumberT], maximum: int = 1) -> t.List[float]:
    ...


def scale(array, maximum: NumberT = 1):
    """
    Scale list of value to a maximum number.

    Args:
        array: Numbers to scale.
        maximum: Maximum scale value.

    Returns:
        Scaled numbers.

    Example:

        >>> scale([1, 2, 3, 4])
        [0.25, 0.5, 0.75, 1.0]
        >>> scale([1, 2, 3, 4], 1)
        [0.25, 0.5, 0.75, 1.0]
        >>> scale([1, 2, 3, 4], 4)
        [1.0, 2.0, 3.0, 4.0]
        >>> scale([1, 2, 3, 4], 2)
        [0.5, 1.0, 1.5, 2.0]

    .. versionadded:: 2.1.0
    """
    array_max = max(array)
    factor = maximum / array_max
    return [item * factor for item in array]


@t.overload
def slope(
    point1: t.Union[t.Tuple["Decimal", "Decimal"], t.List["Decimal"]],
    point2: t.Union[t.Tuple["Decimal", "Decimal"], t.List["Decimal"]],
) -> "Decimal":
    ...


@t.overload
def slope(
    point1: t.Union[t.Tuple[NumberNoDecimalT, NumberNoDecimalT], t.List[NumberNoDecimalT]],
    point2: t.Union[t.Tuple[NumberNoDecimalT, NumberNoDecimalT], t.List[NumberNoDecimalT]],
) -> float:
    ...


def slope(point1, point2):
    """
    Calculate the slope between two points.

    Args:
        point1: X and Y coordinates of first point.
        point2: X and Y cooredinates of second point.

    Returns:
        Calculated slope.

    Example:

        >>> slope((1, 2), (4, 8))
        2.0

    .. versionadded:: 2.1.0
    """
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]

    if x1 == x2:
        result = INFINITY
    else:
        result = (y2 - y1) / (x2 - x1)

    return result


def std_deviation(array: t.List[NumberT]) -> float:
    """
    Calculate standard deviation of list of numbers.

    Args:
        array: List to process.

    Returns:
        Calculated standard deviation.

    Example:

        >>> round(std_deviation([1, 18, 20, 4]), 2) == 8.35
        True

    .. versionadded:: 2.1.0

    .. versionchanged:: 4.0.0
        Remove alias ``sigma``.
    """
    return math.sqrt(variance(array))


@t.overload
def subtract(minuend: "SupportsSub[T, T2]", subtrahend: T) -> T2:
    ...


@t.overload
def subtract(minuend: T, subtrahend: "SupportsSub[T, T2]") -> T2:
    ...


def subtract(minuend, subtrahend):
    """
    Subtracts two numbers.

    Args:
        minuend: Value passed in by the user.
        subtrahend: Value passed in by the user.

    Returns:
        Result of the difference from the given values.

    Example:

        >>> subtract(10, 5)
        5
        >>> subtract(-10, 4)
        -14
        >>> subtract(2, 0.5)
        1.5

    .. versionadded:: 4.0.0
    """
    return call_math_operator(minuend, subtrahend, operator.sub, 0)


def transpose(array: t.Iterable[t.Iterable[T]]) -> t.List[t.List[T]]:
    """
    Transpose the elements of `array`.

    Args:
        array: List to process.

    Returns:
        Transposed list.

    Example:

        >>> transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

    .. versionadded:: 2.1.0
    """
    trans: t.List[t.List[T]] = []

    for y, row in iterator(array):
        for x, col in iterator(row):
            trans = pyd.set_(trans, [x, y], col)

    return trans


@t.overload
def variance(array: t.Mapping[t.Any, "SupportsAdd[int, t.Any]"]) -> float:
    ...


@t.overload
def variance(array: t.Iterable["SupportsAdd[int, t.Any]"]) -> float:
    ...


def variance(array):
    """
    Calculate the variance of the elements in `array`.

    Args:
        array: List to process.

    Returns:
        Calculated variance.

    Example:

        >>> variance([1, 18, 20, 4])
        69.6875

    .. versionadded:: 2.1.0
    """
    avg = mean(array)

    def var(x):
        return power(x - avg, 2)

    return pyd._(array).map_(var).mean().value()


@t.overload
def zscore(
    collection: t.Mapping[T, T2], iteratee: t.Callable[[T2, T, t.Dict[T, T2]], NumberT]
) -> t.List[float]:
    ...


@t.overload
def zscore(collection: t.Mapping[T, T2], iteratee: t.Callable[[T2, T], NumberT]) -> t.List[float]:
    ...


@t.overload
def zscore(collection: t.Mapping[t.Any, T2], iteratee: t.Callable[[T2], NumberT]) -> t.List[float]:
    ...


@t.overload
def zscore(
    collection: t.Iterable[T], iteratee: t.Callable[[T, int, t.List[T]], NumberT]
) -> t.List[float]:
    ...


@t.overload
def zscore(collection: t.Iterable[T], iteratee: t.Callable[[T, int], NumberT]) -> t.List[float]:
    ...


@t.overload
def zscore(collection: t.Iterable[T], iteratee: t.Callable[[T], NumberT]) -> t.List[float]:
    ...


@t.overload
def zscore(collection: t.Iterable[NumberT], iteratee: None = None) -> t.List[float]:
    ...


def zscore(collection, iteratee=None):
    """
    Calculate the standard score assuming normal distribution. If iteratee is passed, each element
    of `collection` is passed through an iteratee before the standard score is computed.

    Args:
        collection: Collection to process.
        iteratee: Iteratee applied per iteration.

    Returns:
        Calculated standard score.

    Example:

        >>> results = zscore([1, 2, 3])

        # [-1.224744871391589, 0.0, 1.224744871391589]

    .. versionadded:: 2.1.0
    """
    array = pyd.map_(collection, iteratee)
    avg = mean(array)
    sig = std_deviation(array)

    return [(item - avg) / sig for item in array]


#
# Utility methods not a part of the main API
#


def call_math_operator(value1, value2, op, default):
    """Return the result of the math operation on the given values."""
    if not value1:
        value1 = default

    if not value2:
        value2 = default

    if not pyd.is_number(value1):
        try:
            value1 = float(value1)
        except Exception:
            pass

    if not pyd.is_number(value2):
        try:
            value2 = float(value2)
        except Exception:
            pass

    return op(value1, value2)


def rounder(func, x, precision):
    precision = pow(10, precision)

    def rounder_func(item):
        return func(item * precision) / precision

    result = None

    if pyd.is_number(x):
        result = rounder_func(x)
    elif pyd.is_iterable(x):
        try:
            result = [rounder_func(item) for item in x]
        except TypeError:
            pass

    return result
