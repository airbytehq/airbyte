"""The pure-Python implementation of the whenever library."""

# The MIT License (MIT)
#
# Copyright (c) Arie Bovenberg
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Maintainer's notes:
#
# - Why is everything in one file?
#   - Flat is better than nested
#   - It prevents circular imports since the classes 'know' about each other
#   - It's easier to vendor the main functionality, if needed.
# - There is some code duplication in this file. This is intentional:
#   - It makes it easier to understand the code
#   - It's sometimes necessary for the type checker
#   - It saves some overhead
# - We don't make use of certain "obvious" modules like re or pathlib.
#   This is to keep the import time down.
from __future__ import annotations

import enum
import os.path
import sys
import warnings
from abc import ABC, abstractmethod
from collections import OrderedDict
from datetime import (
    date as _date,
    datetime as _datetime,
    time as _time,
    timedelta as _timedelta,
    timezone as _timezone,
)
from io import BytesIO
from math import fmod
from struct import pack, unpack
from time import time_ns
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Literal,
    Mapping,
    NewType,
    NoReturn,
    TypeVar,
    Union,
    cast,
    no_type_check,
    overload,
)
from weakref import WeakValueDictionary

# zoneinfo is a relatively expensive import, so we import it lazily
if TYPE_CHECKING:
    from zoneinfo import ZoneInfo

__all__ = [
    # Date and time
    "Date",
    "YearMonth",
    "MonthDay",
    "Time",
    "Instant",
    "OffsetDateTime",
    "ZonedDateTime",
    "SystemDateTime",
    "PlainDateTime",
    # Deltas and time units
    "DateDelta",
    "TimeDelta",
    "DateTimeDelta",
    "years",
    "months",
    "weeks",
    "days",
    "hours",
    "minutes",
    "seconds",
    "milliseconds",
    "microseconds",
    "nanoseconds",
    # Exceptions
    "SkippedTime",
    "RepeatedTime",
    "InvalidOffsetError",
    "ImplicitlyIgnoringDST",
    "TimeZoneNotFoundError",
    "Weekday",
]


class Weekday(enum.Enum):
    """Day of the week; ``.value`` corresponds with ISO numbering."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


# Helpers that pre-compute/lookup as much as possible
_UTC = _timezone.utc
_object_new = object.__new__
_MAX_DELTA_MONTHS = 9999 * 12
_MAX_DELTA_DAYS = 9999 * 366
_MAX_DELTA_NANOS = _MAX_DELTA_DAYS * 24 * 3_600_000_000_000
_UNSET = object()
_PY312 = sys.version_info >= (3, 12)
_PY311 = sys.version_info >= (3, 11)
_Nanos = int  # type alias for subsecond nanoseconds


class _ImmutableBase:
    __slots__ = ()

    # Immutable classes don't need to be copied
    @no_type_check
    def __copy__(self):
        return self

    @no_type_check
    def __deepcopy__(self, _):
        return self

    @no_type_check
    @classmethod
    def __get_pydantic_core_schema__(cls, *_, **kwargs):
        from ._utils import pydantic_schema

        return pydantic_schema(cls)


if TYPE_CHECKING:
    from typing import final
else:

    def final(cls):

        def init_subclass_not_allowed(cls, **kwargs):  # pragma: no cover
            raise TypeError("Subclassing not allowed")

        cls.__init_subclass__ = init_subclass_not_allowed
        return cls


@final
class Date(_ImmutableBase):
    """A date without a time component

    Example
    -------
    >>> d = Date(2021, 1, 2)
    Date(2021-01-02)
    """

    __slots__ = ("_py_date",)

    MIN: ClassVar[Date]
    """The minimum possible date"""
    MAX: ClassVar[Date]
    """The maximum possible date"""

    def __init__(self, year: int, month: int, day: int) -> None:
        self._py_date = _date(year, month, day)

    @classmethod
    def today_in_system_tz(cls) -> Date:
        """Get the current date in the system's local timezone.

        Alias for ``SystemDateTime.now().date()``.

        Example
        -------
        >>> Date.today_in_system_tz()
        Date(2021-01-02)
        """
        # Use now() so this function gets patched like the other now functions
        return SystemDateTime.now().date()

    @property
    def year(self) -> int:
        return self._py_date.year

    @property
    def month(self) -> int:
        return self._py_date.month

    @property
    def day(self) -> int:
        return self._py_date.day

    def year_month(self) -> YearMonth:
        """The year and month (without a day component)

        Example
        -------
        >>> Date(2021, 1, 2).year_month()
        YearMonth(2021-01)
        """
        return YearMonth._from_py_unchecked(self._py_date.replace(day=1))

    def month_day(self) -> MonthDay:
        """The month and day (without a year component)

        Example
        -------
        >>> Date(2021, 1, 2).month_day()
        MonthDay(--01-02)
        """
        return MonthDay._from_py_unchecked(
            self._py_date.replace(year=_DUMMY_LEAP_YEAR)
        )

    def day_of_week(self) -> Weekday:
        """The day of the week

        Example
        -------
        >>> Date(2021, 1, 2).day_of_week()
        Weekday.SATURDAY
        >>> Weekday.SATURDAY.value
        6  # the ISO value
        """
        return Weekday(self._py_date.isoweekday())

    def at(self, t: Time, /) -> PlainDateTime:
        """Combine a date with a time to create a datetime

        Example
        -------
        >>> d = Date(2021, 1, 2)
        >>> d.at(Time(12, 30))
        PlainDateTime(2021-01-02 12:30:00)

        You can use methods like :meth:`~PlainDateTime.assume_utc`
        or :meth:`~PlainDateTime.assume_tz` to find the corresponding exact time.
        """
        return PlainDateTime._from_py_unchecked(
            _datetime.combine(self._py_date, t._py_time), t._nanos
        )

    def py_date(self) -> _date:
        """Convert to a standard library :class:`~datetime.date`"""
        return self._py_date

    @classmethod
    def from_py_date(cls, d: _date, /) -> Date:
        """Create from a :class:`~datetime.date`

        Example
        -------
        >>> Date.from_py_date(date(2021, 1, 2))
        Date(2021-01-02)
        """
        self = _object_new(cls)
        if type(d) is _date:
            pass
        elif type(d) is _datetime:
            d = d.date()
        elif isinstance(d, _date):
            # the only subclass-safe way to ensure we have exactly a datetime.date
            d = _date(d.year, d.month, d.day)
        else:
            raise TypeError(f"Expected date, got {type(d)!r}")
        self._py_date = d
        return self

    def format_common_iso(self) -> str:
        """Format as the common ISO 8601 date format.

        Inverse of :meth:`parse_common_iso`.

        Example
        -------
        >>> Date(2021, 1, 2).format_common_iso()
        '2021-01-02'
        """
        return self._py_date.isoformat()

    @classmethod
    def parse_common_iso(cls, s: str, /) -> Date:
        """Parse a date from an ISO8601 string

        The following formats are accepted:
        - ``YYYY-MM-DD`` ("extended" format)
        - ``YYYYMMDD`` ("basic" format)

        Inverse of :meth:`format_common_iso`

        Example
        -------
        >>> Date.parse_common_iso("2021-01-02")
        Date(2021-01-02)
        """
        return cls._from_py_unchecked(_date_from_iso(s))

    def replace(self, **kwargs: Any) -> Date:
        """Create a new instance with the given fields replaced

        Example
        -------
        >>> d = Date(2021, 1, 2)
        >>> d.replace(day=4)
        Date(2021-01-04)
        """
        return Date._from_py_unchecked(self._py_date.replace(**kwargs))

    @no_type_check
    def add(self, *args, **kwargs) -> Date:
        """Add a components to a date.

        See :ref:`the docs on arithmetic <arithmetic>` for more information.

        Example
        -------
        >>> d = Date(2021, 1, 2)
        >>> d.add(years=1, months=2, days=3)
        Date(2022-03-05)
        >>> Date(2020, 2, 29).add(years=1)
        Date(2021-02-28)
        """
        return self._shift(1, *args, **kwargs)

    @no_type_check
    def subtract(self, *args, **kwargs) -> Date:
        """Subtract components from a date.

        See :ref:`the docs on arithmetic <arithmetic>` for more information.

        Example
        -------
        >>> d = Date(2021, 1, 2)
        >>> d.subtract(years=1, months=2, days=3)
        Date(2019-10-30)
        >>> Date(2021, 3, 1).subtract(years=1)
        Date(2020-03-01)
        """
        return self._shift(-1, *args, **kwargs)

    @no_type_check
    def _shift(
        self, sign: int, delta: DateDelta | _UNSET = _UNSET, /, **kwargs
    ) -> Date:
        if kwargs:
            if delta is not _UNSET:
                raise TypeError(
                    "Cannot combine positional and keyword arguments"
                )
            return self._shift_kwargs(sign, **kwargs)
        elif delta is not _UNSET:
            return self._shift_kwargs(
                sign, months=delta._months, days=delta._days
            )
        else:  # no arguments, just return self
            return self

    @no_type_check
    def _shift_kwargs(self, sign, years=0, months=0, weeks=0, days=0) -> Date:
        return Date._from_py_unchecked(
            self._add_months(sign * (years * 12 + months))._py_date
            + _timedelta(weeks * 7 + days) * sign
        )

    def days_until(self, other: Date, /) -> int:
        """Calculate the number of days from this date to another date.
        If the other date is before this date, the result is negative.

        Example
        -------
        >>> Date(2021, 1, 2).days_until(Date(2021, 1, 5))
        3

        Note
        ----
        If you're interested in calculating the difference
        in terms of days **and** months, use the subtraction operator instead.
        """
        return (other._py_date - self._py_date).days

    def days_since(self, other: Date, /) -> int:
        """Calculate the number of days this day is after another date.
        If the other date is after this date, the result is negative.

        Example
        -------
        >>> Date(2021, 1, 5).days_since(Date(2021, 1, 2))
        3

        Note
        ----
        If you're interested in calculating the difference
        in terms of days **and** months, use the subtraction operator instead.
        """
        return (self._py_date - other._py_date).days

    def _add_months(self, mos: int) -> Date:
        year_overflow, month_new = divmod(self.month - 1 + mos, 12)
        month_new += 1
        year_new = self.year + year_overflow
        return Date(
            year_new,
            month_new,
            min(self.day, _days_in_month(year_new, month_new)),
        )

    def _add_days(self, days: int) -> Date:
        return Date._from_py_unchecked(self._py_date + _timedelta(days))

    def __add__(self, p: DateDelta) -> Date:
        """Add a delta to a date.
        Behaves the same as :meth:`add`
        """
        return (  # type: ignore[no-any-return]
            self.add(months=p._months, days=p._days)
            if isinstance(p, DateDelta)
            else NotImplemented
        )

    @overload
    def __sub__(self, d: DateDelta) -> Date: ...

    @overload
    def __sub__(self, d: Date) -> DateDelta: ...

    def __sub__(self, d: DateDelta | Date) -> Date | DateDelta:
        """Subtract a delta from a date, or subtract two dates

        Subtracting a delta works the same as :meth:`subtract`.

        >>> Date(2021, 1, 2) - DateDelta(weeks=1, days=3)
        Date(2020-12-26)

        The difference between two dates is calculated in months and days,
        such that:

        >>> delta = d1 - d2
        >>> d2 + delta == d1  # always

        The following is not always true:

        >>> d1 - (d1 - d2) == d2  # not always true!
        >>> -(d2 - d1) == d1 - d2  # not always true!

        Examples:

        >>> Date(2023, 4, 15) - Date(2011, 6, 24)
        DateDelta(P12Y9M22D)
        >>> # Truncation
        >>> Date(2024, 4, 30) - Date(2023, 5, 31)
        DateDelta(P11M)
        >>> Date(2024, 3, 31) - Date(2023, 6, 30)
        DateDelta(P9M1D)
        >>> # the other way around, the result is different
        >>> Date(2023, 6, 30) - Date(2024, 3, 31)
        DateDelta(-P9M)

        Note
        ----
        If you'd like to calculate the difference in days only (no months),
        use the :meth:`days_until` or :meth:`days_since` instead.
        """
        if isinstance(d, DateDelta):
            return self.subtract(months=d._months, days=d._days)  # type: ignore[no-any-return]
        elif isinstance(d, Date):
            mos = self.month - d.month + 12 * (self.year - d.year)
            shifted = d._add_months(mos)

            # yes, it's a bit duplicated, but preferable to being clever.
            if d > self:
                if shifted < self:  # i.e. we've overshot
                    mos += 1
                    shifted = d._add_months(mos)
                    dys = (
                        -shifted.day
                        - _days_in_month(self.year, self.month)
                        + self.day
                    )
                else:
                    dys = self.day - shifted.day
            else:
                if shifted > self:  # i.e. we've overshot
                    mos -= 1
                    shifted = d._add_months(mos)
                    dys = (
                        -shifted.day
                        + _days_in_month(shifted.year, shifted.month)
                        + self.day
                    )
                else:
                    dys = self.day - shifted.day
            return DateDelta(months=mos, days=dys)
        return NotImplemented

    __str__ = format_common_iso

    def __repr__(self) -> str:
        return f"Date({self})"

    def __eq__(self, other: object) -> bool:
        """Compare for equality

        Example
        -------
        >>> d = Date(2021, 1, 2)
        >>> d == Date(2021, 1, 2)
        True
        >>> d == Date(2021, 1, 3)
        False
        """
        if not isinstance(other, Date):
            return NotImplemented
        return self._py_date == other._py_date

    def __hash__(self) -> int:
        return hash(self._py_date)

    def __lt__(self, other: Date) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return self._py_date < other._py_date

    def __le__(self, other: Date) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return self._py_date <= other._py_date

    def __gt__(self, other: Date) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return self._py_date > other._py_date

    def __ge__(self, other: Date) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return self._py_date >= other._py_date

    @classmethod
    def _from_py_unchecked(cls, d: _date, /) -> Date:
        self = _object_new(cls)
        self._py_date = d
        return self

    @no_type_check
    def __reduce__(self):
        return _unpkl_date, (pack("<HBB", self.year, self.month, self.day),)


# A separate unpickling function allows us to make backwards-compatible changes
# to the pickling format in the future
@no_type_check
def _unpkl_date(data: bytes) -> Date:
    return Date(*unpack("<HBB", data))


Date.MIN = Date._from_py_unchecked(_date.min)
Date.MAX = Date._from_py_unchecked(_date.max)


@final
class YearMonth(_ImmutableBase):
    """A year and month without a day component

    Useful for representing recurring events or billing periods.

    Example
    -------
    >>> ym = YearMonth(2021, 1)
    YearMonth(2021-01)
    """

    # We store the underlying data in a datetime.date object,
    # which allows us to benefit from its functionality and performance.
    # It isn't exposed to the user, so it's not a problem.
    __slots__ = ("_py_date",)

    MIN: ClassVar[YearMonth]
    """The minimum possible year-month"""
    MAX: ClassVar[YearMonth]
    """The maximum possible year-month"""

    def __init__(self, year: int, month: int) -> None:
        self._py_date = _date(year, month, 1)

    @property
    def year(self) -> int:
        return self._py_date.year

    @property
    def month(self) -> int:
        return self._py_date.month

    def format_common_iso(self) -> str:
        """Format as the common ISO 8601 year-month format.

        Inverse of :meth:`parse_common_iso`.

        Example
        -------
        >>> YearMonth(2021, 1).format_common_iso()
        '2021-01'
        """
        return self._py_date.isoformat()[:7]

    @classmethod
    def parse_common_iso(cls, s: str, /) -> YearMonth:
        """Create from the common ISO 8601 format ``YYYY-MM`` or ``YYYYMM``.

        Inverse of :meth:`format_common_iso`

        Example
        -------
        >>> YearMonth.parse_common_iso("2021-01")
        YearMonth(2021-01)
        """
        return cls._from_py_unchecked(_yearmonth_from_iso(s))

    def replace(self, **kwargs: Any) -> YearMonth:
        """Create a new instance with the given fields replaced

        Example
        -------
        >>> d = YearMonth(2021, 12)
        >>> d.replace(month=3)
        YearMonth(2021-03)
        """
        if "day" in kwargs:
            raise TypeError(
                "replace() got an unexpected keyword argument 'day'"
            )
        return YearMonth._from_py_unchecked(self._py_date.replace(**kwargs))

    def on_day(self, day: int, /) -> Date:
        """Create a date from this year-month with a given day

        Example
        -------
        >>> YearMonth(2021, 1).on_day(2)
        Date(2021-01-02)
        """
        return Date._from_py_unchecked(self._py_date.replace(day=day))

    __str__ = format_common_iso

    def __repr__(self) -> str:
        return f"YearMonth({self})"

    def __eq__(self, other: object) -> bool:
        """Compare for equality

        Example
        -------
        >>> ym = YearMonth(2021, 1)
        >>> ym == YearMonth(2021, 1)
        True
        >>> ym == YearMonth(2021, 2)
        False
        """
        if not isinstance(other, YearMonth):
            return NotImplemented
        return self._py_date == other._py_date

    def __lt__(self, other: YearMonth) -> bool:
        if not isinstance(other, YearMonth):
            return NotImplemented
        return self._py_date < other._py_date

    def __le__(self, other: YearMonth) -> bool:
        if not isinstance(other, YearMonth):
            return NotImplemented
        return self._py_date <= other._py_date

    def __gt__(self, other: YearMonth) -> bool:
        if not isinstance(other, YearMonth):
            return NotImplemented
        return self._py_date > other._py_date

    def __ge__(self, other: YearMonth) -> bool:
        if not isinstance(other, YearMonth):
            return NotImplemented
        return self._py_date >= other._py_date

    def __hash__(self) -> int:
        return hash(self._py_date)

    @classmethod
    def _from_py_unchecked(cls, d: _date, /) -> YearMonth:
        assert d.day == 1
        self = _object_new(cls)
        self._py_date = d
        return self

    @no_type_check
    def __reduce__(self):
        return _unpkl_ym, (pack("<HB", self.year, self.month),)


# A separate unpickling function allows us to make backwards-compatible changes
# to the pickling format in the future
@no_type_check
def _unpkl_ym(data: bytes) -> YearMonth:
    return YearMonth(*unpack("<HB", data))


YearMonth.MIN = YearMonth._from_py_unchecked(_date.min)
YearMonth.MAX = YearMonth._from_py_unchecked(_date.max.replace(day=1))


_DUMMY_LEAP_YEAR = 4


@final
class MonthDay(_ImmutableBase):
    """A month and day without a year component.

    Useful for representing recurring events or birthdays.

    Example
    -------
    >>> MonthDay(11, 23)
    MonthDay(--11-23)
    """

    # We store the underlying data in a datetime.date object,
    # which allows us to benefit from its functionality and performance.
    # It isn't exposed to the user, so it's not a problem.
    __slots__ = ("_py_date",)

    MIN: ClassVar[MonthDay]
    """The minimum possible month-day"""
    MAX: ClassVar[MonthDay]
    """The maximum possible month-day"""

    def __init__(self, month: int, day: int) -> None:
        self._py_date = _date(_DUMMY_LEAP_YEAR, month, day)

    @property
    def month(self) -> int:
        return self._py_date.month

    @property
    def day(self) -> int:
        return self._py_date.day

    def format_common_iso(self) -> str:
        """Format as the common ISO 8601 month-day format.

        Inverse of ``parse_common_iso``.

        Example
        -------
        >>> MonthDay(10, 8).format_common_iso()
        '--10-08'

        Note
        ----
        This format is officially only part of the 2000 edition of the
        ISO 8601 standard. There is no alternative for month-day
        in the newer editions. However, it is still widely used in other libraries.
        """
        return f"-{self._py_date.isoformat()[4:]}"

    @classmethod
    def parse_common_iso(cls, s: str, /) -> MonthDay:
        """Create from the common ISO 8601 format ``--MM-DD`` or ``--MMDD``.

        Inverse of :meth:`format_common_iso`

        Example
        -------
        >>> MonthDay.parse_common_iso("--11-23")
        MonthDay(--11-23)
        """
        return cls._from_py_unchecked(_monthday_from_iso(s))

    def replace(self, **kwargs: Any) -> MonthDay:
        """Create a new instance with the given fields replaced

        Example
        -------
        >>> d = MonthDay(11, 23)
        >>> d.replace(month=3)
        MonthDay(--03-23)
        """
        if "year" in kwargs:
            raise TypeError(
                "replace() got an unexpected keyword argument 'year'"
            )
        return MonthDay._from_py_unchecked(self._py_date.replace(**kwargs))

    def in_year(self, year: int, /) -> Date:
        """Create a date from this month-day with a given day

        Example
        -------
        >>> MonthDay(8, 1).in_year(2025)
        Date(2025-08-01)

        Note
        ----
        This method will raise a ``ValueError`` if the month-day is a leap day
        and the year is not a leap year.
        """
        return Date._from_py_unchecked(self._py_date.replace(year=year))

    def is_leap(self) -> bool:
        """Check if the month-day is February 29th

        Example
        -------
        >>> MonthDay(2, 29).is_leap()
        True
        >>> MonthDay(3, 1).is_leap()
        False
        """
        return self._py_date.month == 2 and self._py_date.day == 29

    __str__ = format_common_iso

    def __repr__(self) -> str:
        return f"MonthDay({self})"

    def __eq__(self, other: object) -> bool:
        """Compare for equality

        Example
        -------
        >>> md = MonthDay(10, 1)
        >>> md == MonthDay(10, 1)
        True
        >>> md == MonthDay(10, 2)
        False
        """
        if not isinstance(other, MonthDay):
            return NotImplemented
        return self._py_date == other._py_date

    def __lt__(self, other: MonthDay) -> bool:
        if not isinstance(other, MonthDay):
            return NotImplemented
        return self._py_date < other._py_date

    def __le__(self, other: MonthDay) -> bool:
        if not isinstance(other, MonthDay):
            return NotImplemented
        return self._py_date <= other._py_date

    def __gt__(self, other: MonthDay) -> bool:
        if not isinstance(other, MonthDay):
            return NotImplemented
        return self._py_date > other._py_date

    def __ge__(self, other: MonthDay) -> bool:
        if not isinstance(other, MonthDay):
            return NotImplemented
        return self._py_date >= other._py_date

    def __hash__(self) -> int:
        return hash(self._py_date)

    @classmethod
    def _from_py_unchecked(cls, d: _date, /) -> MonthDay:
        assert d.year == _DUMMY_LEAP_YEAR
        self = _object_new(cls)
        self._py_date = d
        return self

    @no_type_check
    def __reduce__(self):
        return _unpkl_md, (pack("<BB", self.month, self.day),)


# A separate unpickling function allows us to make backwards-compatible changes
# to the pickling format in the future
@no_type_check
def _unpkl_md(data: bytes) -> MonthDay:
    return MonthDay(*unpack("<BB", data))


MonthDay.MIN = MonthDay._from_py_unchecked(
    _date.min.replace(year=_DUMMY_LEAP_YEAR)
)
MonthDay.MAX = MonthDay._from_py_unchecked(
    _date.max.replace(year=_DUMMY_LEAP_YEAR)
)


@final
class Time(_ImmutableBase):
    """Time of day without a date component

    Example
    -------
    >>> t = Time(12, 30, 0)
    Time(12:30:00)

    """

    __slots__ = ("_py_time", "_nanos")

    MIN: ClassVar[Time]
    """The minimum time, at midnight"""
    MIDNIGHT: ClassVar[Time]
    """Alias for :attr:`MIN`"""
    NOON: ClassVar[Time]
    """The time at noon"""
    MAX: ClassVar[Time]
    """The maximum time, just before midnight"""

    def __init__(
        self,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        *,
        nanosecond: int = 0,
    ) -> None:
        self._py_time = _time(hour, minute, second)
        if nanosecond < 0 or nanosecond >= 1_000_000_000:
            raise ValueError("Nanosecond out of range")
        self._nanos = nanosecond

    @property
    def hour(self) -> int:
        return self._py_time.hour

    @property
    def minute(self) -> int:
        return self._py_time.minute

    @property
    def second(self) -> int:
        return self._py_time.second

    @property
    def nanosecond(self) -> int:
        return self._nanos

    def on(self, d: Date, /) -> PlainDateTime:
        """Combine a time with a date to create a datetime

        Example
        -------
        >>> t = Time(12, 30)
        >>> t.on(Date(2021, 1, 2))
        PlainDateTime(2021-01-02 12:30:00)

        Then, use methods like :meth:`~PlainDateTime.assume_utc`
        or :meth:`~PlainDateTime.assume_tz`
        to find the corresponding exact time.
        """
        return PlainDateTime._from_py_unchecked(
            _datetime.combine(d._py_date, self._py_time),
            self._nanos,
        )

    def py_time(self) -> _time:
        """Convert to a standard library :class:`~datetime.time`"""
        return self._py_time.replace(microsecond=self._nanos // 1_000)

    @classmethod
    def from_py_time(cls, t: _time, /) -> Time:
        """Create from a :class:`~datetime.time`

        Example
        -------
        >>> Time.from_py_time(time(12, 30, 0))
        Time(12:30:00)

        `fold` value is ignored.
        """
        if type(t) is _time:
            t = t.replace(tzinfo=None, fold=0)
        elif isinstance(t, _time):
            # subclass-safe way to ensure we have exactly a datetime.time
            t = _time(t.hour, t.minute, t.second, t.microsecond)
        else:
            raise TypeError(f"Expected datetime.time, got {type(t)!r}")
        return cls._from_py_unchecked(
            t.replace(microsecond=0), t.microsecond * 1_000
        )

    def format_common_iso(self) -> str:
        """Format as the common ISO 8601 time format.

        Inverse of :meth:`parse_common_iso`.

        Example
        -------
        >>> Time(12, 30, 0).format_common_iso()
        '12:30:00'
        """
        return (
            (self._py_time.isoformat() + f".{self._nanos:09d}").rstrip("0")
            if self._nanos
            else self._py_time.isoformat()
        )

    @classmethod
    def parse_common_iso(cls, s: str, /) -> Time:
        """Create from the common ISO 8601 time format

        Inverse of :meth:`format_common_iso`

        Example
        -------
        >>> Time.parse_common_iso("12:30:00")
        Time(12:30:00)
        """
        return cls._from_py_unchecked(*_time_from_iso(s))

    def replace(self, **kwargs: Any) -> Time:
        """Create a new instance with the given fields replaced

        Example
        -------
        >>> t = Time(12, 30, 0)
        >>> d.replace(minute=3, nanosecond=4_000)
        Time(12:03:00.000004)

        """
        _check_invalid_replace_kwargs(kwargs)
        nanos = _pop_nanos_kwarg(kwargs, self._nanos)
        return Time._from_py_unchecked(self._py_time.replace(**kwargs), nanos)

    def _to_ns_since_midnight(self) -> int:
        return (
            self._py_time.hour * 3_600_000_000_000
            + self._py_time.minute * 60_000_000_000
            + self._py_time.second * 1_000_000_000
            + self._nanos
        )

    @classmethod
    def _from_ns_since_midnight(cls, ns: int) -> Time:
        assert 0 <= ns < 86_400_000_000_000
        (hours, ns) = divmod(ns, 3_600_000_000_000)
        (minutes, ns) = divmod(ns, 60_000_000_000)
        (seconds, ns) = divmod(ns, 1_000_000_000)
        return cls._from_py_unchecked(_time(hours, minutes, seconds), ns)

    def round(
        self,
        unit: Literal[
            "hour",
            "minute",
            "second",
            "millisecond",
            "microsecond",
            "nanosecond",
        ] = "second",
        increment: int = 1,
        mode: Literal[
            "ceil", "floor", "half_ceil", "half_floor", "half_even"
        ] = "half_even",
    ) -> Time:
        """Round the time to the specified unit and increment.
        Various rounding modes are available.

        Examples
        --------
        >>> Time(12, 39, 59).round("minute", 15)
        Time(12:45:00)
        >>> Time(8, 9, 13).round("second", 5, mode="floor")
        Time(08:09:10)
        """
        if unit == "day":  # type: ignore[comparison-overlap]
            raise ValueError("Cannot round Time to day")
        return self._round_unchecked(
            increment_to_ns(unit, increment, any_hour_ok=False),
            mode,
            86_400_000_000_000,
        )[0]

    def _round_unchecked(
        self,
        increment_ns: int,
        mode: str,
        day_in_ns: int,
    ) -> tuple[Time, int]:  # the time, and whether the result is "next day"

        quotient, remainder_ns = divmod(
            self._to_ns_since_midnight(), increment_ns
        )

        if mode == "half_even":  # check the default mode first
            threshold_ns = increment_ns // 2 + (quotient % 2 == 0) or 1
        elif mode == "ceil":
            threshold_ns = 1  # Always round up
        elif mode == "floor":
            threshold_ns = increment_ns + 1  # Never round up
        elif mode == "half_floor":
            threshold_ns = increment_ns // 2 + 1
        elif mode == "half_ceil":
            threshold_ns = increment_ns // 2 or 1
        else:
            raise ValueError(f"Invalid rounding mode: {mode!r}")

        round_up = remainder_ns >= threshold_ns
        ns_since_midnight = (quotient + round_up) * increment_ns
        next_day, ns_since_midnight = divmod(ns_since_midnight, day_in_ns)
        return self._from_ns_since_midnight(ns_since_midnight), next_day

    @classmethod
    def _from_py_unchecked(cls, t: _time, nanos: int, /) -> Time:
        assert not t.microsecond
        self = _object_new(cls)
        self._py_time = t
        self._nanos = nanos
        return self

    __str__ = format_common_iso

    def __repr__(self) -> str:
        return f"Time({self})"

    def __eq__(self, other: object) -> bool:
        """Compare for equality

        Example
        -------
        >>> t = Time(12, 30, 0)
        >>> t == Time(12, 30, 0)
        True
        >>> t == Time(12, 30, 1)
        False
        """
        if not isinstance(other, Time):
            return NotImplemented
        return (self._py_time, self._nanos) == (other._py_time, other._nanos)

    def __hash__(self) -> int:
        return hash((self._py_time, self._nanos))

    def __lt__(self, other: Time) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return (self._py_time, self._nanos) < (other._py_time, self._nanos)

    def __le__(self, other: Time) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return (self._py_time, self._nanos) <= (other._py_time, other._nanos)

    def __gt__(self, other: Time) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return (self._py_time, self._nanos) > (other._py_time, other._nanos)

    def __ge__(self, other: Time) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return (self._py_time, self._nanos) >= (other._py_time, other._nanos)

    @no_type_check
    def __reduce__(self):
        return (
            _unpkl_time,
            (
                pack(
                    "<BBBI",
                    self._py_time.hour,
                    self._py_time.minute,
                    self._py_time.second,
                    self._nanos,
                ),
            ),
        )


_NS_PER_UNIT = {
    "minute": 60_000_000_000,
    "second": 1_000_000_000,
    "millisecond": 1_000_000,
    "microsecond": 1_000,
    "nanosecond": 1,
}


def increment_to_ns(unit: str, increment: int, any_hour_ok: bool) -> int:
    if increment < 1 or increment > 1_000 or increment != int(increment):
        raise ValueError("Invalid increment")
    if unit == "day":
        if increment == 1:
            return 86_400_000_000_000
        else:
            raise ValueError("Invalid increment for day")
    elif unit == "hour":
        if 24 % increment and not any_hour_ok:
            raise ValueError("Invalid increment for hour")
        else:
            return 3_600_000_000_000 * increment
    elif unit in ("minute", "second"):
        if 60 % increment:
            raise ValueError(f"Invalid increment for {unit}")
        else:
            return _NS_PER_UNIT[unit] * increment
    elif unit in ("millisecond", "microsecond", "nanosecond"):
        if 1_000 % increment:
            raise ValueError(f"Invalid increment for {unit}")
        else:
            return _NS_PER_UNIT[unit] * increment
    else:
        raise ValueError(f"Invalid unit: {unit}")


# A separate unpickling function allows us to make backwards-compatible changes
# to the pickling format in the future
def _unpkl_time(data: bytes) -> Time:
    *args, nanos = unpack("<BBBI", data)
    return Time._from_py_unchecked(_time(*args), nanos)


Time.MIN = Time()
Time.MIDNIGHT = Time()
Time.NOON = Time(12)
Time.MAX = Time(23, 59, 59, nanosecond=999_999_999)


@final
class TimeDelta(_ImmutableBase):
    """A duration consisting of a precise time: hours, minutes, (nano)seconds

    The inputs are normalized, so 90 minutes becomes 1 hour and 30 minutes,
    for example.

    Examples
    --------
    >>> d = TimeDelta(hours=1, minutes=30)
    TimeDelta(PT1h30m)
    >>> d.in_minutes()
    90.0

    Note
    ----
    A shorter way to instantiate a timedelta is to use the helper functions
    :func:`~whenever.hours`, :func:`~whenever.minutes`, etc.

    """

    __slots__ = ("_total_ns",)

    def __init__(
        self,
        *,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
    ) -> None:
        assert type(nanoseconds) is int  # catch this common mistake
        ns = self._total_ns = (
            # Cast individual components to int to avoid floating point errors
            int(hours * 3_600_000_000_000)
            + int(minutes * 60_000_000_000)
            + int(seconds * 1_000_000_000)
            + int(milliseconds * 1_000_000)
            + int(microseconds * 1_000)
            + nanoseconds
        )
        if abs(ns) > _MAX_DELTA_NANOS:
            raise ValueError("TimeDelta out of range")

    ZERO: ClassVar[TimeDelta]
    """A delta of zero"""
    MAX: ClassVar[TimeDelta]
    """The maximum possible delta"""
    MIN: ClassVar[TimeDelta]
    """The minimum possible delta"""
    _date_part: ClassVar[DateDelta]

    @property
    def _time_part(self) -> TimeDelta:
        return self

    def in_days_of_24h(self) -> float:
        """The total size in days (of exactly 24 hours each)

        Note
        ----
        Note that this may not be the same as days on the calendar,
        since some days have 23 or 25 hours due to daylight saving time.
        """
        return self._total_ns / 86_400_000_000_000

    def in_hours(self) -> float:
        """The total size in hours

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30)
        >>> d.in_hours()
        1.5
        """
        return self._total_ns / 3_600_000_000_000

    def in_minutes(self) -> float:
        """The total size in minutes

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30, seconds=30)
        >>> d.in_minutes()
        90.5
        """
        return self._total_ns / 60_000_000_000

    def in_seconds(self) -> float:
        """The total size in seconds

        Example
        -------
        >>> d = TimeDelta(minutes=2, seconds=1, microseconds=500_000)
        >>> d.in_seconds()
        121.5
        """
        return self._total_ns / 1_000_000_000

    def in_milliseconds(self) -> float:
        """The total size in milliseconds

        >>> d = TimeDelta(seconds=2, microseconds=50)
        >>> d.in_milliseconds()
        2_000.05
        """
        return self._total_ns / 1_000_000

    def in_microseconds(self) -> float:
        """The total size in microseconds

        >>> d = TimeDelta(seconds=2, nanoseconds=50)
        >>> d.in_microseconds()
        2_000_000.05
        """
        return self._total_ns / 1_000

    def in_nanoseconds(self) -> int:
        """The total size in nanoseconds

        >>> d = TimeDelta(seconds=2, nanoseconds=50)
        >>> d.in_nanoseconds()
        2_000_000_050
        """
        return self._total_ns

    def in_hrs_mins_secs_nanos(self) -> tuple[int, int, int, int]:
        """Convert to a tuple of (hours, minutes, seconds, nanoseconds)

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30, microseconds=5_000_090)
        >>> d.in_hrs_mins_secs_nanos()
        (1, 30, 5, 90_000)
        """
        hours, rem = divmod(abs(self._total_ns), 3_600_000_000_000)
        mins, rem = divmod(rem, 60_000_000_000)
        secs, ns = divmod(rem, 1_000_000_000)
        return (
            (hours, mins, secs, ns)
            if self._total_ns >= 0
            else (-hours, -mins, -secs, -ns)
        )

    def py_timedelta(self) -> _timedelta:
        """Convert to a :class:`~datetime.timedelta`

        Inverse of :meth:`from_py_timedelta`

        Note
        ----
        Nanoseconds are truncated to microseconds.
        If you need more control over rounding, use :meth:`round` first.

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30)
        >>> d.py_timedelta()
        timedelta(seconds=5400)
        """
        return _timedelta(microseconds=self._total_ns // 1_000)

    @classmethod
    def from_py_timedelta(cls, td: _timedelta, /) -> TimeDelta:
        """Create from a :class:`~datetime.timedelta`

        Inverse of :meth:`py_timedelta`

        Example
        -------
        >>> TimeDelta.from_py_timedelta(timedelta(seconds=5400))
        TimeDelta(PT1h30m)
        """
        if type(td) is not _timedelta:
            raise TypeError("Expected datetime.timedelta exactly")
        return TimeDelta(
            microseconds=td.microseconds,
            seconds=td.seconds,
            hours=td.days * 24,
        )

    def format_common_iso(self) -> str:
        """Format as the *popular interpretation* of the ISO 8601 duration format.
        May not strictly adhere to (all versions of) the standard.
        See :ref:`here <iso8601-durations>` for more information.

        Inverse of :meth:`parse_common_iso`.

        Example
        -------
        >>> TimeDelta(hours=1, minutes=30).format_common_iso()
        'PT1H30M'
        """
        hrs, mins, secs, ns = abs(self).in_hrs_mins_secs_nanos()
        seconds = (
            f"{secs + ns / 1_000_000_000:.9f}".rstrip("0") if ns else str(secs)
        )
        return f"{(self._total_ns < 0) * '-'}PT" + (
            (
                f"{hrs}H" * bool(hrs)
                + f"{mins}M" * bool(mins)
                + f"{seconds}S" * bool(secs or ns)
            )
            or "0S"
        )

    @classmethod
    def parse_common_iso(cls, s: str, /) -> TimeDelta:
        """Parse the *popular interpretation* of the ISO 8601 duration format.
        Does not parse all possible ISO 8601 durations.
        See :ref:`here <iso8601-durations>` for more information.

        Inverse of :meth:`format_common_iso`

        Example
        -------
        >>> TimeDelta.parse_common_iso("PT1H80M")
        TimeDelta(PT2h20m)

        Note
        ----
        Any duration with a date part is considered invalid.
        ``PT0S`` is valid, but ``P0D`` is not.
        """
        exc = ValueError(f"Invalid format: {s!r}")
        prev_unit = ""
        nanos = 0

        if len(s) < 4 or not s.isascii():
            raise exc

        s = s.upper()
        if s.startswith("PT"):
            sign = 1
            rest = s[2:]
        elif s.startswith("-PT"):
            sign = -1
            rest = s[3:]
        elif s.startswith("+PT"):
            sign = 1
            rest = s[3:]
        else:
            raise exc

        while rest:
            rest, value, unit = _parse_timedelta_component(rest, exc)

            if unit == "H" and prev_unit == "":
                nanos += value * 3_600_000_000_000
            elif unit == "M" and prev_unit in "H":
                nanos += value * 60_000_000_000
            elif unit == "S":
                nanos += value
                if rest:
                    raise exc
                break
            else:
                raise exc  # components out of order

            prev_unit = unit

        if nanos > _MAX_DELTA_NANOS:
            raise ValueError("TimeDelta out of range")

        return TimeDelta._from_nanos_unchecked(sign * nanos)

    def round(
        self,
        unit: Literal[
            "hour",
            "minute",
            "second",
            "millisecond",
            "microsecond",
            "nanosecond",
        ] = "second",
        increment: int = 1,
        mode: Literal[
            "ceil", "floor", "half_ceil", "half_floor", "half_even"
        ] = "half_even",
    ) -> TimeDelta:
        """Round the delta to the specified unit and increment.
        Various rounding modes are available.

        Examples
        --------
        >>> t = TimeDelta(seconds=12345)
        TimeDelta(PT3h25m45s)
        >>> t.round("minute")
        TimeDelta(PT3h26m)
        >>> t.round("second", increment=10, mode="floor")
        TimeDelta(PT3h25m40s)
        """
        if unit == "day":  # type: ignore[comparison-overlap]
            raise ValueError(CANNOT_ROUND_DAY_MSG)

        increment_ns = increment_to_ns(unit, increment, any_hour_ok=True)
        quotient, remainder_ns = divmod(self._total_ns, increment_ns)

        if mode == "half_even":  # check the default case first
            threshold_ns = increment_ns // 2 + (quotient % 2 == 0) or 1
        elif mode == "ceil":
            threshold_ns = 1  # Always round up
        elif mode == "floor":
            threshold_ns = increment_ns + 1  # Never round up
        elif mode == "half_floor":
            threshold_ns = increment_ns // 2 + 1
        elif mode == "half_ceil":
            threshold_ns = increment_ns // 2 or 1
        else:
            raise ValueError(f"Invalid rounding mode: {mode!r}")

        round_up = remainder_ns >= threshold_ns
        rounded_ns = (quotient + round_up) * increment_ns
        if abs(rounded_ns) > _MAX_DELTA_NANOS:
            raise ValueError("Resulting TimeDelta out of range")
        return self._from_nanos_unchecked(rounded_ns)

    def __add__(self, other: TimeDelta) -> TimeDelta:
        """Add two deltas together

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30)
        >>> d + TimeDelta(minutes=30)
        TimeDelta(PT2h)
        """
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return TimeDelta(nanoseconds=self._total_ns + other._total_ns)

    def __sub__(self, other: TimeDelta) -> TimeDelta:
        """Subtract two deltas

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30)
        >>> d - TimeDelta(minutes=30)
        TimeDelta(PT1h)
        """
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return TimeDelta(nanoseconds=self._total_ns - other._total_ns)

    def __eq__(self, other: object) -> bool:
        """Compare for equality

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30)
        >>> d == TimeDelta(minutes=90)
        True
        >>> d == TimeDelta(hours=2)
        False
        """
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return self._total_ns == other._total_ns

    def __hash__(self) -> int:
        return hash(self._total_ns)

    def __lt__(self, other: TimeDelta) -> bool:
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return self._total_ns < other._total_ns

    def __le__(self, other: TimeDelta) -> bool:
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return self._total_ns <= other._total_ns

    def __gt__(self, other: TimeDelta) -> bool:
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return self._total_ns > other._total_ns

    def __ge__(self, other: TimeDelta) -> bool:
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return self._total_ns >= other._total_ns

    def __bool__(self) -> bool:
        """True if the value is non-zero

        Example
        -------
        >>> bool(TimeDelta())
        False
        >>> bool(TimeDelta(minutes=1))
        True
        """
        return bool(self._total_ns)

    def __mul__(self, other: float) -> TimeDelta:
        """Multiply by a number

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30)
        >>> d * 2.5
        TimeDelta(PT3h45m)
        """
        if not isinstance(other, (int, float)):
            return NotImplemented
        return TimeDelta(nanoseconds=int(self._total_ns * other))

    def __rmul__(self, other: float) -> TimeDelta:
        return self * other

    def __neg__(self) -> TimeDelta:
        """Negate the value

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30)
        >>> -d
        TimeDelta(-PT1h30m)
        """
        return TimeDelta(nanoseconds=-self._total_ns)

    def __pos__(self) -> TimeDelta:
        """Return the value unchanged

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30)
        >>> +d
        TimeDelta(PT1h30m)
        """
        return self

    @overload
    def __truediv__(self, other: float) -> TimeDelta: ...

    @overload
    def __truediv__(self, other: TimeDelta) -> float: ...

    def __truediv__(self, other: float | TimeDelta) -> TimeDelta | float:
        """Divide by a number or another delta

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=30)
        >>> d / 2.5
        TimeDelta(PT36m)
        >>> d / TimeDelta(minutes=30)
        3.0

        Note
        ----
        Because TimeDelta is limited to nanosecond precision, the result of
        division may not be exact.
        """
        if isinstance(other, TimeDelta):
            return self._total_ns / other._total_ns
        elif isinstance(other, (int, float)):
            return TimeDelta(nanoseconds=int(self._total_ns / other))
        return NotImplemented

    def __floordiv__(self, other: TimeDelta) -> int:
        """Floor division by another delta

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=39)
        >>> d // time_delta(minutes=15)
        6
        """
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return self._total_ns // other._total_ns

    def __mod__(self, other: TimeDelta) -> TimeDelta:
        """Modulo by another delta

        Example
        -------
        >>> d = TimeDelta(hours=1, minutes=39)
        >>> d % TimeDelta(minutes=15)
        TimeDelta(PT9m)
        """
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return TimeDelta(nanoseconds=self._total_ns % other._total_ns)

    def __abs__(self) -> TimeDelta:
        """The absolute value

        Example
        -------
        >>> d = TimeDelta(hours=-1, minutes=-30)
        >>> abs(d)
        TimeDelta(PT1h30m)
        """
        return TimeDelta._from_nanos_unchecked(abs(self._total_ns))

    __str__ = format_common_iso

    def __repr__(self) -> str:
        iso = self.format_common_iso()
        # lowercase everything besides the prefix (don't forget the sign!)
        cased = iso[:3] + iso[3:].lower()
        return f"TimeDelta({cased})"

    @no_type_check
    def __reduce__(self):
        return _unpkl_tdelta, (
            pack("<qI", *divmod(self._total_ns, 1_000_000_000)),
        )

    @classmethod
    def _from_nanos_unchecked(cls, ns: int) -> TimeDelta:
        new = _object_new(cls)
        new._total_ns = ns
        return new


# A separate unpickling function allows us to make backwards-compatible changes
# to the pickling format in the future
@no_type_check
def _unpkl_tdelta(data: bytes) -> TimeDelta:
    s, ns = unpack("<qI", data)
    return TimeDelta(seconds=s, nanoseconds=ns)


_MAX_TDELTA_DIGITS = 35  # consistent with Rust extension


def _parse_timedelta_component(
    fullstr: str, exc: Exception
) -> tuple[str, int, Literal["H", "M", "S"]]:
    try:
        split_index, unit = next(
            (i, c) for i, c in enumerate(fullstr) if c in "HMS"
        )
    except StopIteration:
        raise exc

    raw, rest = fullstr[:split_index], fullstr[split_index + 1 :]

    if unit == "S":
        digits, sep, nanos_raw = _split_nextchar(raw, ".,")

        if (
            len(digits) > _MAX_TDELTA_DIGITS
            or not digits.isdigit()
            or len(nanos_raw) > 9
            or (sep and not nanos_raw.isdigit())
        ):
            raise exc

        value = int(digits) * 1_000_000_000 + int(nanos_raw.ljust(9, "0"))
    else:
        if len(raw) > _MAX_TDELTA_DIGITS or not raw.isdigit():
            raise exc
        value = int(raw)

    return rest, value, cast(Literal["H", "M", "S"], unit)


TimeDelta.ZERO = TimeDelta()
TimeDelta.MAX = TimeDelta(seconds=9999 * 366 * 24 * 3_600)
TimeDelta.MIN = TimeDelta(seconds=-9999 * 366 * 24 * 3_600)


@final
class DateDelta(_ImmutableBase):
    """A duration of time consisting of calendar units
    (years, months, weeks, and days)
    """

    __slots__ = ("_months", "_days")

    def __init__(
        self, *, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0
    ) -> None:
        months = self._months = months + 12 * years
        days = self._days = days + 7 * weeks
        if (months > 0 and days < 0) or (months < 0 and days > 0):
            raise ValueError("Mixed sign in date delta")
        elif (
            abs(self._months) > _MAX_DELTA_MONTHS
            or abs(self._days) > _MAX_DELTA_DAYS
        ):
            raise ValueError("Date delta months out of range")

    ZERO: ClassVar[DateDelta]
    """A delta of zero"""
    _time_part = TimeDelta.ZERO

    @property
    def _date_part(self) -> DateDelta:
        return self

    def in_months_days(self) -> tuple[int, int]:
        """Convert to a tuple of months and days.

        Example
        -------
        >>> p = DateDelta(months=25, days=9)
        >>> p.in_months_days()
        (25, 9)
        >>> DateDelta(months=-13, weeks=-5)
        (-13, -35)
        """
        return self._months, self._days

    def in_years_months_days(self) -> tuple[int, int, int]:
        """Convert to a tuple of years, months, and days.

        Example
        -------
        >>> p = DateDelta(years=1, months=2, days=11)
        >>> p.in_years_months_days()
        (1, 2, 11)
        """
        years = int(self._months / 12)
        months = int(fmod(self._months, 12))
        return years, months, self._days

    def format_common_iso(self) -> str:
        """Format as the *popular interpretation* of the ISO 8601 duration format.
        May not strictly adhere to (all versions of) the standard.
        See :ref:`here <iso8601-durations>` for more information.

        Inverse of :meth:`parse_common_iso`.

        The format looks like this:

        .. code-block:: text

            P(nY)(nM)(nD)

        For example:

        .. code-block:: text

            P1D
            P2M
            P1Y2M3W4D

        Example
        -------
        >>> p = DateDelta(years=1, months=2, weeks=3, days=11)
        >>> p.format_common_iso()
        'P1Y2M3W11D'
        >>> DateDelta().format_common_iso()
        'P0D'
        """
        if self._months < 0 or self._days < 0:
            sign = "-"
            months, days = -self._months, -self._days
        else:
            sign = ""
            months, days = self._months, self._days

        years = months // 12
        months %= 12

        date = (
            f"{years}Y" * bool(years),
            f"{months}M" * bool(months),
            f"{days}D" * bool(days),
        )
        return sign + "P" + ("".join(date) or "0D")

    __str__ = format_common_iso

    @classmethod
    def parse_common_iso(cls, s: str, /) -> DateDelta:
        """Parse the *popular interpretation* of the ISO 8601 duration format.
        Does not parse all possible ISO 8601 durations.
        See :ref:`here <iso8601-durations>` for more information.

        Inverse of :meth:`format_common_iso`

        Example
        -------
        >>> DateDelta.parse_common_iso("P1W11D")
        DateDelta(P1w11d)
        >>> DateDelta.parse_common_iso("-P3m")
        DateDelta(-P3m)

        Note
        ----
        Only durations without time component are accepted.
        ``P0D`` is valid, but ``PT0S`` is not.

        Note
        ----
        The number of digits in each component is limited to 8.
        """
        exc = ValueError(f"Invalid format: {s!r}")
        prev_unit = ""
        months = 0
        days = 0

        if len(s) < 3 or not s.isascii():
            raise exc

        s = s.upper()
        if s[0] == "P":
            sign = 1
            rest = s[1:]
        elif s.startswith("-P"):
            sign = -1
            rest = s[2:]
        elif s.startswith("+P"):
            sign = 1
            rest = s[2:]
        else:
            raise exc

        while rest:
            rest, value, unit = _parse_datedelta_component(rest, exc)

            if unit == "Y" and prev_unit == "":
                months += value * 12
            elif unit == "M" and prev_unit in "Y":
                months += value
            elif unit == "W" and prev_unit in "YM":
                days += value * 7
            elif unit == "D" and prev_unit in "YMW":
                days += value
                if rest:
                    raise exc  # leftover characters
                break
            else:
                raise exc  # components out of order

            prev_unit = unit

        try:
            return DateDelta(months=sign * months, days=sign * days)
        except ValueError:
            raise exc

    @overload
    def __add__(self, other: DateDelta) -> DateDelta: ...

    @overload
    def __add__(self, other: TimeDelta) -> DateTimeDelta: ...

    def __add__(
        self, other: DateDelta | TimeDelta
    ) -> DateDelta | DateTimeDelta:
        """Add the fields of another delta to this one

        Example
        -------
        >>> p = DateDelta(weeks=2, months=1)
        >>> p + DateDelta(weeks=1, days=4)
        DateDelta(P1m25d)
        """
        if isinstance(other, DateDelta):
            return DateDelta(
                months=self._months + other._months,
                days=self._days + other._days,
            )
        elif isinstance(other, TimeDelta):
            new = _object_new(DateTimeDelta)
            new._date_part = self
            new._time_part = other
            return new
        else:
            return NotImplemented

    def __radd__(self, other: TimeDelta) -> DateTimeDelta:
        if isinstance(other, TimeDelta):
            new = _object_new(DateTimeDelta)
            new._date_part = self
            new._time_part = other
            return new
        return NotImplemented

    @overload
    def __sub__(self, other: DateDelta) -> DateDelta: ...

    @overload
    def __sub__(self, other: TimeDelta) -> DateTimeDelta: ...

    def __sub__(
        self, other: DateDelta | TimeDelta
    ) -> DateDelta | DateTimeDelta:
        """Subtract the fields of another delta from this one

        Example
        -------
        >>> p = DateDelta(weeks=2, days=3)
        >>> p - DateDelta(days=2)
        DateDelta(P15d)
        """
        if isinstance(other, DateDelta):
            return DateDelta(
                months=self._months - other._months,
                days=self._days - other._days,
            )
        elif isinstance(other, TimeDelta):
            return self + (-other)
        else:
            return NotImplemented

    def __rsub__(self, other: TimeDelta) -> DateTimeDelta:
        if isinstance(other, TimeDelta):
            return -self + other
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        """Compare for equality, normalized to months and days.

        `a == b` is equivalent to `a.in_months_days() == b.in_months_days()`

        Example
        -------
        >>> p = DateDelta(weeks=4, days=2)
        DateDelta(P30d)
        >>> p == DateDelta(weeks=3, days=9)
        True
        >>> p == DateDelta(weeks=2, days=4)
        True  # same number of days
        >>> p == DateDelta(months=1)
        False  # months and days cannot be compared directly
        """
        if not isinstance(other, DateDelta):
            return NotImplemented
        return self._months == other._months and self._days == other._days

    def __hash__(self) -> int:
        return hash((self._months, self._days))

    def __bool__(self) -> bool:
        """True if any contains any non-zero data

        Example
        -------
        >>> bool(DateDelta())
        False
        >>> bool(DateDelta(days=-1))
        True
        """
        return bool(self._months or self._days)

    def __repr__(self) -> str:
        iso = self.format_common_iso()
        # lowercase everything besides the prefix (don't forget the sign!)
        cased = iso[:2] + iso[2:].lower()
        return f"DateDelta({cased})"

    def __neg__(self) -> DateDelta:
        """Negate the contents

        Example
        -------
        >>> p = DateDelta(weeks=2, days=3)
        >>> -p
        DateDelta(-P17d)
        """
        return DateDelta(months=-self._months, days=-self._days)

    def __pos__(self) -> DateDelta:
        """Return the value unchanged

        Example
        -------
        >>> p = DateDelta(weeks=2, days=-3)
        DateDelta(P11d)
        >>> +p
        DateDelta(P11d)
        """
        return self

    def __mul__(self, other: int) -> DateDelta:
        """Multiply the contents by a round number

        Example
        -------
        >>> p = DateDelta(years=1, weeks=2)
        >>> p * 2
        DateDelta(P2y28d)
        """
        if not isinstance(other, int):
            return NotImplemented
        return DateDelta(
            months=self._months * other,
            days=self._days * other,
        )

    def __rmul__(self, other: int) -> DateDelta:
        if isinstance(other, int):
            return self * other
        return NotImplemented

    def __abs__(self) -> DateDelta:
        """If the contents are negative, return the positive version

        Example
        -------
        >>> p = DateDelta(months=-2, days=-3)
        >>> abs(p)
        DateDelta(P2m3d)
        """
        return DateDelta(months=abs(self._months), days=abs(self._days))

    @no_type_check
    def __reduce__(self):
        return (_unpkl_ddelta, (self._months, self._days))


# A separate unpickling function allows us to make backwards-compatible changes
# to the pickling format in the future
def _unpkl_ddelta(months: int, days: int) -> DateDelta:
    return DateDelta(months=months, days=days)


_MAX_DDELTA_DIGITS = 8  # consistent with Rust extension


def _parse_datedelta_component(s: str, exc: Exception) -> tuple[str, int, str]:
    try:
        split_index, unit = next(
            (i, c) for i, c in enumerate(s) if c in "YMWD"
        )
    except StopIteration:
        raise exc

    raw, rest = s[:split_index], s[split_index + 1 :]

    if not raw.isdigit() or len(raw) > _MAX_DDELTA_DIGITS:
        raise exc

    return rest, int(raw), unit


DateDelta.ZERO = DateDelta()
TimeDelta._date_part = DateDelta.ZERO


@final
class DateTimeDelta(_ImmutableBase):
    """A duration with both a date and time component."""

    __slots__ = ("_date_part", "_time_part")

    def __init__(
        self,
        *,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
    ) -> None:
        self._date_part = DateDelta(
            years=years, months=months, weeks=weeks, days=days
        )
        self._time_part = TimeDelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
            nanoseconds=nanoseconds,
        )
        if (
            (self._date_part._months < 0 or self._date_part._days < 0)
            and self._time_part._total_ns > 0
        ) or (
            (self._date_part._months > 0 or self._date_part._days > 0)
            and self._time_part._total_ns < 0
        ):
            raise ValueError("Mixed sign in date-time delta")

    ZERO: ClassVar[DateTimeDelta]
    """A delta of zero"""

    def date_part(self) -> DateDelta:
        """The date part of the delta"""
        return self._date_part

    def time_part(self) -> TimeDelta:
        """The time part of the delta"""
        return self._time_part

    def in_months_days_secs_nanos(self) -> tuple[int, int, int, int]:
        """Convert to a tuple of (months, days, seconds, nanoseconds)

        Example
        -------
        >>> d = DateTimeDelta(weeks=1, days=11, hours=4, microseconds=2)
        >>> d.in_months_days_secs_nanos()
        (0, 18, 14_400, 2000)
        """
        subsec_nanos = int(fmod(self._time_part._total_ns, 1_000_000_000))
        whole_seconds = int(self._time_part._total_ns / 1_000_000_000)
        return self._date_part.in_months_days() + (whole_seconds, subsec_nanos)

    def format_common_iso(self) -> str:
        """Format as the *popular interpretation* of the ISO 8601 duration format.
        May not strictly adhere to (all versions of) the standard.
        See :ref:`here <iso8601-durations>` for more information.

        Inverse of :meth:`parse_common_iso`.

        The format is:

        .. code-block:: text

            P(nY)(nM)(nD)T(nH)(nM)(nS)

        Example
        -------
        >>> d = DateTimeDelta(
        ...     weeks=1,
        ...     days=11,
        ...     hours=4,
        ...     milliseconds=12,
        ... )
        >>> d.format_common_iso()
        'P1W11DT4H0.012S'
        """
        sign = (
            self._date_part._months < 0
            or self._date_part._days < 0
            or self._time_part._total_ns < 0
        ) * "-"
        date = abs(self._date_part).format_common_iso()[1:] * bool(
            self._date_part
        )
        time = abs(self._time_part).format_common_iso()[1:] * bool(
            self._time_part
        )
        return sign + "P" + ((date + time) or "0D")

    @classmethod
    def parse_common_iso(cls, s: str, /) -> DateTimeDelta:
        """Parse the *popular interpretation* of the ISO 8601 duration format.
        Does not parse all possible ISO 8601 durations.
        See :ref:`here <iso8601-durations>` for more information.

        Examples:

        .. code-block:: text

           P4D        # 4 days
           PT4H       # 4 hours
           PT3M40.5S  # 3 minutes and 40.5 seconds
           P1W11DT4H  # 1 week, 11 days, and 4 hours
           -PT7H4M    # -7 hours and -4 minutes (-7:04:00)
           +PT7H4M    # 7 hours and 4 minutes (7:04:00)

        Inverse of :meth:`format_common_iso`

        Example
        -------
        >>> DateTimeDelta.parse_common_iso("-P1W11DT4H")
        DateTimeDelta(-P1w11dT4h)
        """
        exc = ValueError(f"Invalid format: {s!r}")
        prev_unit = ""
        months = 0
        days = 0
        nanos = 0

        if len(s) < 3 or not s.isascii() or s.endswith("T"):
            raise exc

        s = s.upper()
        if s[0] == "P":
            sign = 1
            rest = s[1:]
        elif s.startswith("-P"):
            sign = -1
            rest = s[2:]
        elif s.startswith("+P"):
            sign = 1
            rest = s[2:]
        else:
            raise exc

        while rest and not rest.startswith("T"):
            rest, value, unit = _parse_datedelta_component(rest, exc)

            if unit == "Y" and prev_unit == "":
                months += value * 12
            elif unit == "M" and prev_unit in "Y":
                months += value
            elif unit == "W" and prev_unit in "YM":
                days += value * 7
            elif unit == "D" and prev_unit in "YMW":
                days += value
                break
            else:
                raise exc  # components out of order

            prev_unit = unit

        try:
            ddelta = DateDelta(months=sign * months, days=sign * days)
        except ValueError:
            raise exc

        prev_unit = ""
        if rest and not rest.startswith("T"):
            raise exc

        # skip the "T" separator
        rest = rest[1:]

        while rest:
            rest, value, unit = _parse_timedelta_component(rest, exc)

            if unit == "H" and prev_unit == "":
                nanos += value * 3_600_000_000_000
            elif unit == "M" and prev_unit in "H":
                nanos += value * 60_000_000_000
            elif unit == "S":
                nanos += value
                if rest:
                    raise exc
                break
            else:
                raise exc

            prev_unit = unit

        if nanos > _MAX_DELTA_NANOS:
            raise exc

        tdelta = TimeDelta._from_nanos_unchecked(sign * nanos)

        return cls._from_parts(ddelta, tdelta)

    def __add__(self, other: Delta) -> DateTimeDelta:
        """Add two deltas together

        Example
        -------
        >>> d = DateTimeDelta(weeks=1, days=11, hours=4)
        >>> d + DateTimeDelta(months=2, days=3, minutes=90)
        DateTimeDelta(P1m1w14dT5h30m)
        """
        new = _object_new(DateTimeDelta)
        if isinstance(other, DateTimeDelta):
            new._date_part = self._date_part + other._date_part
            new._time_part = self._time_part + other._time_part
        elif isinstance(other, TimeDelta):
            new._date_part = self._date_part
            new._time_part = self._time_part + other
        elif isinstance(other, DateDelta):
            new._date_part = self._date_part + other
            new._time_part = self._time_part
        else:
            return NotImplemented
        return new

    def __radd__(self, other: TimeDelta | DateDelta) -> DateTimeDelta:
        if isinstance(other, (TimeDelta, DateDelta)):
            return self + other
        return NotImplemented

    def __sub__(
        self, other: DateTimeDelta | TimeDelta | DateDelta
    ) -> DateTimeDelta:
        """Subtract two deltas

        Example
        -------
        >>> d = DateTimeDelta(weeks=1, days=11, hours=4)
        >>> d - DateTimeDelta(months=2, days=3, minutes=90)
        DateTimeDelta(-P2m1w8dT2h30m)
        """
        if isinstance(other, DateTimeDelta):
            d = self._date_part - other._date_part
            t = self._time_part - other._time_part
        elif isinstance(other, TimeDelta):
            d = self._date_part
            t = self._time_part - other
        elif isinstance(other, DateDelta):
            d = self._date_part - other
            t = self._time_part
        else:
            return NotImplemented
        return self._from_parts(d, t)

    def __rsub__(self, other: TimeDelta | DateDelta) -> DateTimeDelta:
        new = _object_new(DateTimeDelta)
        if isinstance(other, TimeDelta):
            new._date_part = -self._date_part
            new._time_part = other - self._time_part
        elif isinstance(other, DateDelta):
            new._date_part = other - self._date_part
            new._time_part = -self._time_part
        else:
            return NotImplemented
        return new

    def __eq__(self, other: object) -> bool:
        """Compare for equality

        Example
        -------
        >>> d = DateTimeDelta(
        ...     weeks=1,
        ...     days=23,
        ...     hours=4,
        ... )
        >>> d == DateTimeDelta(
        ...     weeks=1,
        ...     days=23,
        ...     minutes=4 * 60,  # normalized
        ... )
        True
        >>> d == DateTimeDelta(
        ...     weeks=4,
        ...     days=2,  # days/weeks are normalized
        ...     hours=4,
        ... )
        True
        >>> d == DateTimeDelta(
        ...     months=1,  # months/days cannot be compared directly
        ...     hours=4,
        ... )
        False
        """
        if not isinstance(other, DateTimeDelta):
            return NotImplemented
        return (
            self._date_part == other._date_part
            and self._time_part == other._time_part
        )

    def __hash__(self) -> int:
        return hash((self._date_part, self._time_part))

    def __bool__(self) -> bool:
        """True if any field is non-zero

        Example
        -------
        >>> bool(DateTimeDelta())
        False
        >>> bool(DateTimeDelta(minutes=1))
        True
        """
        return bool(self._date_part or self._time_part)

    def __mul__(self, other: int) -> DateTimeDelta:
        """Multiply by a number

        Example
        -------
        >>> d = DateTimeDelta(weeks=1, days=11, hours=4)
        >>> d * 2
        DateTimeDelta(P2w22dT8h)
        """
        # OPTIMIZE: use unchecked constructor
        return self._from_parts(
            self._date_part * other, self._time_part * other
        )

    def __rmul__(self, other: int) -> DateTimeDelta:
        return self * other

    def __neg__(self) -> DateTimeDelta:
        """Negate the delta

        Example
        -------
        >>> d = DateTimeDelta(days=11, hours=4)
        >>> -d
        DateTimeDelta(-P11dT4h)
        """
        # OPTIMIZE: use unchecked constructor
        return self._from_parts(-self._date_part, -self._time_part)

    def __pos__(self) -> DateTimeDelta:
        """Return the delta unchanged

        Example
        -------
        >>> d = DateTimeDelta(weeks=1, days=-11, hours=4)
        >>> +d
        DateTimeDelta(P1W11DT4H)
        """
        return self

    def __abs__(self) -> DateTimeDelta:
        """The absolute value of the delta

        Example
        -------
        >>> d = DateTimeDelta(weeks=1, days=-11, hours=4)
        >>> abs(d)
        DateTimeDelta(P1w11dT4h)
        """
        new = _object_new(DateTimeDelta)
        new._date_part = abs(self._date_part)
        new._time_part = abs(self._time_part)
        return new

    __str__ = format_common_iso

    def __repr__(self) -> str:
        iso = self.format_common_iso()
        # lowercase everything besides the prefix and separator
        cased = "".join(c if c in "PT" else c.lower() for c in iso)
        return f"DateTimeDelta({cased})"

    @classmethod
    def _from_parts(cls, d: DateDelta, t: TimeDelta) -> DateTimeDelta:
        new = _object_new(cls)
        new._date_part = d
        new._time_part = t
        if ((d._months < 0 or d._days < 0) and t._total_ns > 0) or (
            (d._months > 0 or d._days > 0) and t._total_ns < 0
        ):
            raise ValueError("Mixed sign in date-time delta")
        return new

    @no_type_check
    def __reduce__(self):
        secs, nanos = divmod(self._time_part._total_ns, 1_000_000_000)
        return (
            _unpkl_dtdelta,
            (self._date_part._months, self._date_part._days, secs, nanos),
        )


# A separate unpickling function allows us to make backwards-compatible changes
# to the pickling format in the future
@no_type_check
def _unpkl_dtdelta(
    months: int, days: int, secs: int, nanos: int
) -> DateTimeDelta:
    new = _object_new(DateTimeDelta)
    new._date_part = DateDelta(months=months, days=days)
    new._time_part = TimeDelta(seconds=secs, nanoseconds=nanos)
    return new


DateTimeDelta.ZERO = DateTimeDelta()
Delta = Union[DateTimeDelta, TimeDelta, DateDelta]
_T = TypeVar("_T")


class _BasicConversions(_ImmutableBase, ABC):
    """Methods for types converting to/from the standard library and ISO8601:

    - :class:`Instant`
    - :class:`PlainDateTime`
    - :class:`ZonedDateTime`
    - :class:`OffsetDateTime`
    - :class:`SystemDateTime`

    (This base class class itself is not for public use.)
    """

    __slots__ = ("_py_dt", "_nanos")
    _py_dt: _datetime
    _nanos: int

    @classmethod
    @abstractmethod
    def from_py_datetime(cls: type[_T], d: _datetime, /) -> _T:
        """Create an instance from a :class:`~datetime.datetime` object.
        Inverse of :meth:`~_BasicConversions.py_datetime`.

        Note
        ----
        The datetime is checked for validity, raising similar exceptions
        to the constructor.
        ``ValueError`` is raised if the datetime doesn't have the correct
        tzinfo matching the class. For example, :class:`ZonedDateTime`
        requires a :class:`~zoneinfo.ZoneInfo` tzinfo.

        Warning
        -------
        No exceptions are raised if the datetime is ambiguous.
        Its ``fold`` attribute is used to disambiguate.
        """

    def py_datetime(self) -> _datetime:
        """Convert to a standard library :class:`~datetime.datetime`

        Note
        ----
        Nanoseconds are truncated to microseconds.
        If you wish to customize the rounding behavior, use
        the ``round()`` method first.
        """
        return self._py_dt.replace(microsecond=self._nanos // 1_000)

    @abstractmethod
    def format_common_iso(self) -> str:
        """Format as common ISO string representation. Each
        subclass has a different format.

        See :ref:`here <iso8601>` for more information.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def parse_common_iso(cls: type[_T], s: str, /) -> _T:
        """Create an instance from common ISO 8601 representation,
        which is different for each subclass.

        See :ref:`here <iso8601>` for more information.
        """

    def __str__(self) -> str:
        """Same as :meth:`format_common_iso`"""
        return self.format_common_iso()

    @classmethod
    def _from_py_unchecked(cls: type[_T], d: _datetime, nanos: int, /) -> _T:
        assert not d.microsecond
        assert 0 <= nanos < 1_000_000_000
        self = _object_new(cls)
        self._py_dt = d  # type: ignore[attr-defined]
        self._nanos = nanos  # type: ignore[attr-defined]
        return self


class _LocalTime(_BasicConversions, ABC):
    """Methods for types that know a local date and time-of-day:

    - :class:`PlainDateTime`
    - :class:`ZonedDateTime`
    - :class:`OffsetDateTime`
    - :class:`SystemDateTime`

    (The class itself is not for public use.)
    """

    __slots__ = ()

    @property
    def year(self) -> int:
        return self._py_dt.year

    @property
    def month(self) -> int:
        return self._py_dt.month

    @property
    def day(self) -> int:
        return self._py_dt.day

    @property
    def hour(self) -> int:
        return self._py_dt.hour

    @property
    def minute(self) -> int:
        return self._py_dt.minute

    @property
    def second(self) -> int:
        return self._py_dt.second

    @property
    def nanosecond(self) -> int:
        return self._nanos

    def date(self) -> Date:
        """The date part of the datetime

        Example
        -------
        >>> d = Instant.from_utc(2021, 1, 2, 3, 4, 5)
        >>> d.date()
        Date(2021-01-02)

        To perform the inverse, use :meth:`Date.at` and a method
        like :meth:`~PlainDateTime.assume_utc` ortestoffset
        :meth:`~PlainDateTime.assume_tz`:

        >>> date.at(time).assume_tz("Europe/London")
        """
        return Date._from_py_unchecked(self._py_dt.date())

    def time(self) -> Time:
        """The time-of-day part of the datetime

        Example
        -------
        >>> d = ZonedDateTime(2021, 1, 2, 3, 4, 5, tz="Europe/Paris")
        ZonedDateTime(2021-01-02T03:04:05+01:00[Europe/Paris])
        >>> d.time()
        Time(03:04:05)

        To perform the inverse, use :meth:`Time.on` and a method
        like :meth:`~PlainDateTime.assume_utc` or
        :meth:`~PlainDateTime.assume_tz`:

        >>> time.on(date).assume_tz("Europe/Paris")
        """
        return Time._from_py_unchecked(self._py_dt.time(), self._nanos)

    # We document these methods as abtract,
    # but they are actually implemented slightly different per subclass
    if not TYPE_CHECKING:  # pragma: no cover

        @abstractmethod
        def replace(self: _T, /, **kwargs: Any) -> _T:
            """Construct a new instance with the given fields replaced.

            Arguments are the same as the constructor,
            but only keyword arguments are allowed.

            Note
            ----
            If you need to shift the datetime by a duration,
            use the addition and subtraction operators instead.
            These account for daylight saving time and other complications.

            Warning
            -------
            The same exceptions as the constructor may be raised.
            For system and zoned datetimes,
            The ``disambiguate`` keyword argument is recommended to
            resolve ambiguities explicitly. For more information, see
            whenever.rtfd.io/en/latest/overview.html#ambiguity-in-timezones

            Example
            -------
            >>> d = PlainDateTime(2020, 8, 15, 23, 12)
            >>> d.replace(year=2021)
            PlainDateTime(2021-08-15 23:12:00)
            >>>
            >>> z = ZonedDateTime(2020, 8, 15, 23, 12, tz="Europe/London")
            >>> z.replace(year=2021)
            ZonedDateTime(2021-08-15T23:12:00+01:00)
            """

        def replace_date(self: _T, date: Date, /, **kwargs) -> _T:
            """Create a new instance with the date replaced

            Example
            -------
            >>> d = PlainDateTime(2020, 8, 15, hour=4)
            >>> d.replace_date(Date(2021, 1, 1))
            PlainDateTime(2021-01-01T04:00:00)
            >>> zdt = ZonedDateTime.now("Europe/London")
            >>> zdt.replace_date(Date(2021, 1, 1))
            ZonedDateTime(2021-01-01T13:00:00.23439+00:00[Europe/London])

            See :meth:`replace` for more information.
            """

        def replace_time(self: _T, time: Time, /, **kwargs) -> _T:
            """Create a new instance with the time replaced

            Example
            -------
            >>> d = PlainDateTime(2020, 8, 15, hour=4)
            >>> d.replace_time(Time(12, 30))
            PlainDateTime(2020-08-15T12:30:00)
            >>> zdt = ZonedDateTime.now("Europe/London")
            >>> zdt.replace_time(Time(12, 30))
            ZonedDateTime(2024-06-15T12:30:00+01:00[Europe/London])

            See :meth:`replace` for more information.
            """

        @abstractmethod
        def add(
            self: _T,
            *,
            years: int = 0,
            months: int = 0,
            weeks: int = 0,
            days: int = 0,
            hours: float = 0,
            minutes: float = 0,
            seconds: float = 0,
            milliseconds: float = 0,
            microseconds: float = 0,
            nanoseconds: int = 0,
            **kwargs,
        ) -> _T:
            """Add date and time units to this datetime.

            Arithmetic on datetimes is complicated.
            Additional keyword arguments ``ignore_dst`` and ``disambiguate``
            may be relevant for certain types and situations.
            See :ref:`the docs on arithmetic <arithmetic>` for more information
            and the reasoning behind it.
            """

        @abstractmethod
        def subtract(
            self: _T,
            *,
            years: int = 0,
            months: int = 0,
            weeks: int = 0,
            days: int = 0,
            hours: float = 0,
            minutes: float = 0,
            seconds: float = 0,
            milliseconds: float = 0,
            microseconds: float = 0,
            nanoseconds: int = 0,
            **kwargs,
        ) -> _T:
            """Inverse of :meth:`add`."""

        def round(
            self: _T,
            unit: Literal[
                "day",
                "hour",
                "minute",
                "second",
                "millisecond",
                "microsecond",
                "nanosecond",
            ] = "second",
            increment: int = 1,
            mode: Literal[
                "ceil", "floor", "half_ceil", "half_floor", "half_even"
            ] = "half_even",
        ) -> _T:
            """Round the datetime to the specified unit and increment.
            Different rounding modes are available.

            Examples
            --------
            >>> d = ZonedDateTime(2020, 8, 15, 23, 24, 18, tz="Europe/Paris")
            >>> d.round("day")
            ZonedDateTime(2020-08-16 00:00:00+02:00[Europe/Paris])
            >>> d.round("minute", increment=15, mode="floor")
            ZonedDateTime(2020-08-15 23:15:00+02:00[Europe/Paris])

            Notes
            -----
            * In the rare case that rounding results in an ambiguous time,
              the offset is preserved if possible.
              Otherwise, the time is resolved according to the "compatible" strategy.
            * Rounding in "day" mode may be affected by DST transitions.
              i.e. on 23-hour days, 11:31 AM is rounded up.
            * For ``OffsetDateTime``, the ``ignore_dst`` parameter is required,
              because it is possible (though unlikely) that the rounded datetime
              will not have the same offset.
            * This method has similar behavior to the ``round()`` method of
              Temporal objects in JavaScript.
            """


class _ExactTime(_BasicConversions):
    """Methods for types that represent a specific moment in time.

    Implemented by:

    - :class:`Instant`
    - :class:`ZonedDateTime`
    - :class:`OffsetDateTime`
    - :class:`SystemDateTime`

    (This base class class itself is not for public use.)
    """

    __slots__ = ()

    # These methods aren't strictly abstract (they don't follow LSP),
    # but we do document them here.
    if not TYPE_CHECKING:  # pragma: no cover

        @classmethod
        def now(cls: type[_T], **kwargs) -> _T:
            """Create an instance from the current time.

            This method on :class:`~ZonedDateTime` and :class:`~OffsetDateTime` requires
            an additional timezone or offset argument, respectively.

            Example
            -------

            >>> Instant.now()
            Instant(2021-08-15T22:12:00.49821Z)
            >>> ZonedDateTime.now("Europe/London")
            ZonedDateTime(2021-08-15 23:12:00.50332+01:00[Europe/London])

            """

    def timestamp(self) -> int:
        """The UNIX timestamp for this datetime. Inverse of :meth:`from_timestamp`.

        Note
        ----
        In contrast to the standard library, this method always returns an integer,
        not a float. This is because floating point timestamps are not precise
        enough to represent all instants to nanosecond precision.
        This decision is consistent with other modern date-time libraries.

        Example
        -------
        >>> Instant.from_utc(1970, 1, 1).timestamp()
        0
        >>> ts = 1_123_000_000
        >>> Instant.from_timestamp(ts).timestamp() == ts
        True
        """
        return int(self._py_dt.timestamp())

    def timestamp_millis(self) -> int:
        """Like :meth:`timestamp`, but with millisecond precision."""
        return int(self._py_dt.timestamp()) * 1_000 + self._nanos // 1_000_000

    def timestamp_nanos(self) -> int:
        """Like :meth:`timestamp`, but with nanosecond precision."""
        return int(self._py_dt.timestamp()) * 1_000_000_000 + self._nanos

    if not TYPE_CHECKING:

        @classmethod
        def from_timestamp(cls: type[_T], i: int | float, /, **kwargs) -> _T:
            """Create an instance from a UNIX timestamp.
            The inverse of :meth:`~_ExactTime.timestamp`.

            :class:`~ZonedDateTime` and :class:`~OffsetDateTime` require
            a ``tz=`` and ``offset=`` kwarg, respectively.

            Note
            ----
            ``from_timestamp()`` also accepts floats, in order to ease
            migration from the standard library.
            Note however that ``timestamp()`` only returns integers.
            The reason is that floating point timestamps are not precise
            enough to represent all instants to nanosecond precision.

            Example
            -------
            >>> Instant.from_timestamp(0)
            Instant(1970-01-01T00:00:00Z)
            >>> ZonedDateTime.from_timestamp(1_123_000_000, tz="America/New_York")
            ZonedDateTime(2005-08-02 12:26:40-04:00[America/New_York])

            """

        @classmethod
        def from_timestamp_millis(cls: type[_T], i: int, /, **kwargs) -> _T:
            """Like :meth:`from_timestamp`, but for milliseconds."""

        @classmethod
        def from_timestamp_nanos(cls: type[_T], i: int, /, **kwargs) -> _T:
            """Like :meth:`from_timestamp`, but for nanoseconds."""

    @overload
    def to_fixed_offset(self, /) -> OffsetDateTime: ...

    @overload
    def to_fixed_offset(
        self, offset: int | TimeDelta, /
    ) -> OffsetDateTime: ...

    def to_fixed_offset(
        self, offset: int | TimeDelta | None = None, /
    ) -> OffsetDateTime:
        """Convert to an OffsetDateTime that represents the same moment in time.

        If not offset is given, the offset is taken from the original datetime.
        """
        return OffsetDateTime._from_py_unchecked(
            self._py_dt.astimezone(
                # mypy doesn't know that offset is never None
                _timezone(self._py_dt.utcoffset())  # type: ignore[arg-type]
                if offset is None
                else _load_offset(offset)
            ),
            self._nanos,
        )

    def to_tz(self, tz: str, /) -> ZonedDateTime:
        """Convert to a ZonedDateTime that represents the same moment in time.

        Raises
        ------
        ~whenever.TimeZoneNotFoundError
            If the timezone ID is not found in the system's timezone database.
        """
        return ZonedDateTime._from_py_unchecked(
            self._py_dt.astimezone(_get_tz(tz)), self._nanos
        )

    def to_system_tz(self) -> SystemDateTime:
        """Convert to a SystemDateTime that represents the same moment in time."""
        return SystemDateTime._from_py_unchecked(
            self._py_dt.astimezone(), self._nanos
        )

    def exact_eq(self: _T, other: _T, /) -> bool:
        """Compare objects by their values
        (instead of whether they represent the same instant).
        Different types are never equal.

        Note
        ----
        If ``a.exact_eq(b)`` is true, then
        ``a == b`` is also true, but the converse is not necessarily true.

        Examples
        --------

        >>> a = OffsetDateTime(2020, 8, 15, hour=12, offset=1)
        >>> b = OffsetDateTime(2020, 8, 15, hour=13, offset=2)
        >>> a == b
        True  # equivalent instants
        >>> a.exact_eq(b)
        False  # different values (hour and offset)
        >>> a.exact_eq(Instant.now())
        TypeError  # different types
        """
        if type(self) is not type(other):
            raise TypeError("Cannot compare different types")
        return (
            self._py_dt,  # type: ignore[attr-defined]
            self._py_dt.utcoffset(),  # type: ignore[attr-defined]
            self._nanos,  # type: ignore[attr-defined]
            self._py_dt.tzinfo,  # type: ignore[attr-defined]
        ) == (
            other._py_dt,  # type: ignore[attr-defined]
            other._py_dt.utcoffset(),  # type: ignore[attr-defined]
            other._nanos,  # type: ignore[attr-defined]
            other._py_dt.tzinfo,  # type: ignore[attr-defined]
        )

    def difference(
        self,
        other: Instant | OffsetDateTime | ZonedDateTime | SystemDateTime,
        /,
    ) -> TimeDelta:
        """Calculate the difference between two instants in time.

        Equivalent to :meth:`__sub__`.

        See :ref:`the docs on arithmetic <arithmetic>` for more information.
        """
        return self - other  # type: ignore[operator, no-any-return]

    def __eq__(self, other: object) -> bool:
        """Check if two datetimes represent at the same moment in time

        ``a == b`` is equivalent to ``a.instant() == b.instant()``

        Note
        ----
        If you want to exactly compare the values on their values
        instead, use :meth:`exact_eq`.

        Example
        -------
        >>> Instant.from_utc(2020, 8, 15, hour=23) == Instant.from_utc(2020, 8, 15, hour=23)
        True
        >>> OffsetDateTime(2020, 8, 15, hour=23, offset=1) == (
        ...     ZonedDateTime(2020, 8, 15, hour=18, tz="America/New_York")
        ... )
        True
        """
        if not isinstance(other, _ExactTime):
            return NotImplemented
        # We can't rely on simple equality, because it isn't equal
        # between two datetimes with different timezones if one of the
        # datetimes needs fold to disambiguate it.
        # See peps.python.org/pep-0495/#aware-datetime-equality-comparison.
        # We want to avoid this legacy edge case, so we normalize to UTC.
        return (self._py_dt.astimezone(_UTC), self._nanos) == (
            other._py_dt.astimezone(_UTC),
            other._nanos,
        )

    def __lt__(self, other: _ExactTime) -> bool:
        """Compare two datetimes by when they occur in time

        ``a < b`` is equivalent to ``a.instant() < b.instant()``

        Example
        -------
        >>> OffsetDateTime(2020, 8, 15, hour=23, offset=8) < (
        ...     ZoneDateTime(2020, 8, 15, hour=20, tz="Europe/Amsterdam")
        ... )
        True
        """
        if not isinstance(other, _ExactTime):
            return NotImplemented
        return (self._py_dt.astimezone(_UTC), self._nanos) < (
            other._py_dt.astimezone(_UTC),
            other._nanos,
        )

    def __le__(self, other: _ExactTime) -> bool:
        """Compare two datetimes by when they occur in time

        ``a <= b`` is equivalent to ``a.instant() <= b.instant()``

        Example
        -------
        >>> OffsetDateTime(2020, 8, 15, hour=23, offset=8) <= (
        ...     ZoneDateTime(2020, 8, 15, hour=20, tz="Europe/Amsterdam")
        ... )
        True
        """
        if not isinstance(other, _ExactTime):
            return NotImplemented
        return (self._py_dt.astimezone(_UTC), self._nanos) <= (
            other._py_dt.astimezone(_UTC),
            other._nanos,
        )

    def __gt__(self, other: _ExactTime) -> bool:
        """Compare two datetimes by when they occur in time

        ``a > b`` is equivalent to ``a.instant() > b.instant()``

        Example
        -------
        >>> OffsetDateTime(2020, 8, 15, hour=19, offset=-8) > (
        ...     ZoneDateTime(2020, 8, 15, hour=20, tz="Europe/Amsterdam")
        ... )
        True
        """
        if not isinstance(other, _ExactTime):
            return NotImplemented
        return (self._py_dt.astimezone(_UTC), self._nanos) > (
            other._py_dt.astimezone(_UTC),
            other._nanos,
        )

    def __ge__(self, other: _ExactTime) -> bool:
        """Compare two datetimes by when they occur in time

        ``a >= b`` is equivalent to ``a.instant() >= b.instant()``

        Example
        -------
        >>> OffsetDateTime(2020, 8, 15, hour=19, offset=-8) >= (
        ...     ZoneDateTime(2020, 8, 15, hour=20, tz="Europe/Amsterdam")
        ... )
        True
        """
        if not isinstance(other, _ExactTime):
            return NotImplemented
        return (self._py_dt.astimezone(_UTC), self._nanos) >= (
            other._py_dt.astimezone(_UTC),
            other._nanos,
        )

    # Mypy doesn't like overloaded overrides, but we'd like to document
    # this 'abstract' behaviour anyway
    if not TYPE_CHECKING:  # pragma: no branch

        @abstractmethod
        def __sub__(self, other: _ExactTime) -> TimeDelta:
            """Calculate the duration between two datetimes

            ``a - b`` is equivalent to ``a.instant() - b.instant()``

            Equivalent to :meth:`difference`.

            See :ref:`the docs on arithmetic <arithmetic>` for more information.

            Example
            -------
            >>> d = Instant.from_utc(2020, 8, 15, hour=23)
            >>> d - ZonedDateTime(2020, 8, 15, hour=20, tz="Europe/Amsterdam")
            TimeDelta(05:00:00)
            """
            if isinstance(other, _ExactTime):
                py_delta = self._py_dt.astimezone(_UTC) - other._py_dt
                return TimeDelta(
                    seconds=py_delta.days * 86_400 + py_delta.seconds,
                    nanoseconds=self._nanos - other._nanos,
                )
            return NotImplemented


class _ExactAndLocalTime(_LocalTime, _ExactTime):
    """Common behavior for all types that know an exact time and
    corresponding local date and time-of-day.

    - :class:`ZonedDateTime`
    - :class:`OffsetDateTime`
    - :class:`SystemDateTime`

    (The class itself it not for public use.)
    """

    __slots__ = ()

    @property
    def offset(self) -> TimeDelta:
        """The UTC offset of the datetime"""
        return TimeDelta._from_nanos_unchecked(
            int(
                self._py_dt.utcoffset().total_seconds()  # type: ignore[union-attr]
                * 1_000_000_000
            )
        )

    def to_instant(self) -> Instant:
        """Get the underlying instant in time

        Example
        -------

        >>> d = ZonedDateTime(2020, 8, 15, hour=23, tz="Europe/Amsterdam")
        >>> d.instant()
        Instant(2020-08-15 21:00:00Z)
        """
        return Instant._from_py_unchecked(
            self._py_dt.astimezone(_UTC), self._nanos
        )

    def instant(self) -> Instant:
        warnings.warn(
            "instant() is deprecated. Use to_instant() instead.",
            DeprecationWarning,
        )
        return self.to_instant()

    def to_plain(self) -> PlainDateTime:
        """Get the underlying date and time (without offset or timezone)

        As an inverse, :class:`PlainDateTime` has methods
        :meth:`~PlainDateTime.assume_utc`, :meth:`~PlainDateTime.assume_fixed_offset`
        , :meth:`~PlainDateTime.assume_tz`, and :meth:`~PlainDateTime.assume_system_tz`
        which may require additional arguments.
        """
        return PlainDateTime._from_py_unchecked(
            self._py_dt.replace(tzinfo=None),
            self._nanos,
        )

    def local(self) -> PlainDateTime:
        warnings.warn(
            "local() is deprecated. Use to_plain() instead.",
            DeprecationWarning,
        )
        return self.to_plain()


@final
class Instant(_ExactTime):
    """Represents a moment in time with nanosecond precision.

    This class is great for representing a specific point in time independent
    of location. It maps 1:1 to UTC or a UNIX timestamp.

    Example
    -------
    >>> from whenever import Instant
    >>> py311_release = Instant.from_utc(2022, 10, 24, hour=17)
    Instant(2022-10-24 17:00:00Z)
    >>> py311_release.add(hours=3).timestamp()
    1666641600
    """

    __slots__ = ()

    def __init__(self) -> None:
        raise TypeError(
            "Instant instances cannot be created through the constructor. "
            "Use `Instant.from_utc` or `Instant.now` instead."
        )

    @classmethod
    def from_utc(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        *,
        nanosecond: int = 0,
    ) -> Instant:
        """Create an Instant defined by a UTC date and time."""
        if nanosecond < 0 or nanosecond >= 1_000_000_000:
            raise ValueError(f"nanosecond out of range: {nanosecond}")
        return cls._from_py_unchecked(
            _datetime(year, month, day, hour, minute, second, 0, _UTC),
            nanosecond,
        )

    MIN: ClassVar[Instant]
    """The minimum representable instant."""

    MAX: ClassVar[Instant]
    """The maximum representable instant."""

    @classmethod
    def now(cls) -> Instant:
        """Create an Instant from the current time."""
        secs, nanos = divmod(time_ns(), 1_000_000_000)
        return cls._from_py_unchecked(_fromtimestamp(secs, _UTC), nanos)

    @classmethod
    def from_timestamp(cls, i: int | float, /) -> Instant:
        """Create an Instant from a UNIX timestamp (in seconds).

        The inverse of the ``timestamp()`` method.
        """
        secs, fract = divmod(i, 1)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _UTC), int(fract * 1_000_000_000)
        )

    @classmethod
    def from_timestamp_millis(cls, i: int, /) -> Instant:
        """Create an Instant from a UNIX timestamp (in milliseconds).

        The inverse of the ``timestamp_millis()`` method.
        """
        if not isinstance(i, int):
            raise TypeError("method requires an integer")
        secs, millis = divmod(i, 1_000)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _UTC), millis * 1_000_000
        )

    @classmethod
    def from_timestamp_nanos(cls, i: int, /) -> Instant:
        """Create an Instant from a UNIX timestamp (in nanoseconds).

        The inverse of the ``timestamp_nanos()`` method.
        """
        if not isinstance(i, int):
            raise TypeError("method requires an integer")
        secs, nanos = divmod(i, 1_000_000_000)
        return cls._from_py_unchecked(_fromtimestamp(secs, _UTC), nanos)

    @classmethod
    def from_py_datetime(cls, d: _datetime, /) -> Instant:
        """Create an Instant from a standard library ``datetime`` object.
        The datetime must be aware.

        The inverse of the ``py_datetime()`` method.
        """
        if d.tzinfo is None or d.utcoffset() is None:
            raise ValueError(
                "Cannot create Instant from a naive datetime. "
                "Use PlainDateTime.from_py_datetime() for this."
            )
        as_utc = d.astimezone(_UTC)
        return cls._from_py_unchecked(
            _strip_subclasses(as_utc.replace(microsecond=0)),
            as_utc.microsecond * 1_000,
        )

    def format_common_iso(self) -> str:
        """Convert to the popular ISO format ``YYYY-MM-DDTHH:MM:SSZ``

        The inverse of the ``parse_common_iso()`` method.
        """
        return (
            self._py_dt.isoformat()[:-6]
            + bool(self._nanos) * f".{self._nanos:09d}".rstrip("0")
            + "Z"
        )

    @classmethod
    def parse_common_iso(cls, s: str, /) -> Instant:
        """Parse an ISO 8601 string. Supports basic and extended formats,
        but not week dates or ordinal dates.

        See the `docs on ISO8601 support <https://whenever.readthedocs.io/en/latest/overview.html#iso-8601>`_ for more information.

        The inverse of the ``format_common_iso()`` method.
        """
        dt, nanos = _offset_dt_from_iso(s)
        return cls._from_py_unchecked(dt.astimezone(_UTC), nanos)

    def format_rfc2822(self) -> str:
        """Format as an RFC 2822 string.

        The inverse of the ``parse_rfc2822()`` method.

        Note
        ----
        The output is also compatible with the (stricter) RFC 9110 standard.

        Example
        -------
        >>> Instant.from_utc(2020, 8, 8, hour=23, minute=12).format_rfc2822()
        "Sat, 08 Aug 2020 23:12:00 GMT"
        """
        return (
            f"{_WEEKDAY_TO_RFC2822[self._py_dt.weekday()]}, "
            f"{self._py_dt.day:02} "
            f"{_MONTH_TO_RFC2822[self._py_dt.month]} {self._py_dt.year:04} "
            f"{self._py_dt.time()} GMT"
        )

    @classmethod
    def parse_rfc2822(cls, s: str, /) -> Instant:
        """Parse a UTC datetime in RFC 2822 format.

        The inverse of the ``format_rfc2822()`` method.

        Example
        -------
        >>> Instant.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 GMT")
        Instant(2020-08-15 23:12:00Z)

        >>> # also valid:
        >>> Instant.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 +0000")
        >>> Instant.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 +0800")
        >>> Instant.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 -0000")
        >>> Instant.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 UT")
        >>> Instant.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 MST")

        Note
        ----
        - Although technically part of the RFC 2822 standard,
          comments within folding whitespace are not supported.
        """
        return cls._from_py_unchecked(_parse_rfc2822(s).astimezone(_UTC), 0)

    def add(
        self,
        *,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
    ) -> Instant:
        """Add a time amount to this instant.

        See the `docs on arithmetic <https://whenever.readthedocs.io/en/latest/overview.html#arithmetic>`_ for more information.
        """
        return self + TimeDelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
            nanoseconds=nanoseconds,
        )

    def subtract(
        self,
        *,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
    ) -> Instant:
        """Subtract a time amount from this instant.

        See the `docs on arithmetic <https://whenever.readthedocs.io/en/latest/overview.html#arithmetic>`_ for more information.
        """
        return self.add(
            hours=-hours,
            minutes=-minutes,
            seconds=-seconds,
            milliseconds=-milliseconds,
            microseconds=-microseconds,
            nanoseconds=-nanoseconds,
        )

    def round(
        self,
        unit: Literal[
            "hour",
            "minute",
            "second",
            "millisecond",
            "microsecond",
            "nanosecond",
        ] = "second",
        increment: int = 1,
        mode: Literal[
            "ceil", "floor", "half_ceil", "half_floor", "half_even"
        ] = "half_even",
    ) -> Instant:
        """Round the instant to the specified unit and increment.
        Various rounding modes are available.

        Examples
        --------
        >>> Instant.from_utc(2020, 1, 1, 12, 39, 59).round("minute", 15)
        Instant(2020-01-01 12:45:00Z)
        >>> Instant.from_utc(2020, 1, 1, 8, 9, 13).round("second", 5, mode="floor")
        Instant(2020-01-01 08:09:10Z)
        """
        if unit == "day":  # type: ignore[comparison-overlap]
            raise ValueError(CANNOT_ROUND_DAY_MSG)
        rounded_time, next_day = Time._from_py_unchecked(
            self._py_dt.time(), self._nanos
        )._round_unchecked(
            increment_to_ns(unit, increment, any_hour_ok=False),
            mode,
            86_400_000_000_000,
        )
        return self._from_py_unchecked(
            _datetime.combine(
                self._py_dt.date() + _timedelta(days=next_day),
                rounded_time._py_time,
                tzinfo=_UTC,
            ),
            rounded_time._nanos,
        )

    def __add__(self, delta: TimeDelta) -> Instant:
        """Add a time amount to this datetime.

        See the `docs on arithmetic <https://whenever.readthedocs.io/en/latest/overview.html#arithmetic>`_ for more information.
        """
        if isinstance(delta, TimeDelta):
            delta_secs, nanos = divmod(
                self._nanos + delta._time_part._total_ns,
                1_000_000_000,
            )
            return self._from_py_unchecked(
                self._py_dt + _timedelta(seconds=delta_secs),
                nanos,
            )
        return NotImplemented

    @overload
    def __sub__(self, other: _ExactTime) -> TimeDelta: ...

    @overload
    def __sub__(self, other: TimeDelta) -> Instant: ...

    def __sub__(self, other: TimeDelta | _ExactTime) -> Instant | TimeDelta:
        """Subtract another exact time or timedelta

        Subtraction of deltas happens in the same way as the :meth:`subtract` method.
        Subtraction of instants happens the same way as the :meth:`~_ExactTime.difference` method.

        See the `docs on arithmetic <https://whenever.readthedocs.io/en/latest/overview.html#arithmetic>`_ for more information.

        Example
        -------
        >>> d = Instant.from_utc(2020, 8, 15, hour=23, minute=12)
        >>> d - hours(24) - seconds(5)
        Instant(2020-08-14 23:11:55Z)
        >>> d - Instant.from_utc(2020, 8, 14)
        TimeDelta(47:12:00)
        """
        if isinstance(other, _ExactTime):
            return super().__sub__(other)  # type: ignore[misc, no-any-return]
        elif isinstance(other, TimeDelta):
            return self + -other
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self._py_dt, self._nanos))

    def __repr__(self) -> str:
        return f"Instant({str(self).replace('T', ' ')})"

    # a custom pickle implementation with a smaller payload
    def __reduce__(self) -> tuple[object, ...]:
        return (
            _unpkl_inst,
            (pack("<qL", int(self._py_dt.timestamp()), self._nanos),),
        )


_UNIX_INSTANT = -int(_datetime(1, 1, 1, tzinfo=_UTC).timestamp()) + 86_400


# Backwards compatibility for instances pickled before 0.8.0
def _unpkl_utc(data: bytes) -> Instant:
    secs, nanos = unpack("<qL", data)
    return Instant._from_py_unchecked(
        _fromtimestamp(secs - _UNIX_INSTANT, _UTC), nanos
    )


# A separate unpickling function allows us to make backwards-compatible changes
# to the pickling format in the future
def _unpkl_inst(data: bytes) -> Instant:
    secs, nanos = unpack("<qL", data)
    return Instant._from_py_unchecked(_fromtimestamp(secs, _UTC), nanos)


@final
class OffsetDateTime(_ExactAndLocalTime):
    """A datetime with a fixed UTC offset.
    Useful for representing a "static" local date and time-of-day
    at a specific location.

    Example
    -------
    >>> # Midnight in Salt Lake City
    >>> OffsetDateTime(2023, 4, 21, offset=-6)
    OffsetDateTime(2023-04-21 00:00:00-06:00)

    Note
    ----
    Adjusting instances of this class do *not* account for daylight saving time.
    If you need to add or subtract durations from an offset datetime
    and account for DST, convert to a ``ZonedDateTime`` first,
    This class knows when the offset changes.
    """

    __slots__ = ()

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        *,
        nanosecond: int = 0,
        offset: int | TimeDelta,
    ) -> None:
        self._py_dt = _check_utc_bounds(
            _datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
                0,
                _load_offset(offset),
            )
        )
        if nanosecond < 0 or nanosecond >= 1_000_000_000:
            raise ValueError(f"nanosecond out of range: {nanosecond}")
        self._nanos = nanosecond

    @classmethod
    def now(
        cls, offset: int | TimeDelta, /, *, ignore_dst: bool = False
    ) -> OffsetDateTime:
        """Create an instance from the current time.

        Important
        ---------
        Getting the current time with a fixed offset implicitly ignores DST
        and other timezone changes. Instead, use ``Instant.now()`` or
        ``ZonedDateTime.now(<tz_id>)`` if you know the timezone.
        Or, if you want to ignore DST and accept potentially incorrect offsets,
        pass ``ignore_dst=True`` to this method. For more information, see
        `the documentation <https://whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic>`_.
        """
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(OFFSET_NOW_DST_MSG)
        secs, nanos = divmod(time_ns(), 1_000_000_000)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _load_offset(offset)), nanos
        )

    def format_common_iso(self) -> str:
        """Convert to the popular ISO format ``YYYY-MM-DDTHH:MM:SS±HH:MM``

        The inverse of the ``parse_common_iso()`` method.
        """
        iso_without_fracs = self._py_dt.isoformat()
        return (
            iso_without_fracs[:19]
            + bool(self._nanos) * f".{self._nanos:09d}".rstrip("0")
            + iso_without_fracs[19:]
        )

    @classmethod
    def parse_common_iso(cls, s: str, /) -> OffsetDateTime:
        """Parse the popular ISO format ``YYYY-MM-DDTHH:MM:SS±HH:MM``

        The inverse of the ``format_common_iso()`` method.

        Example
        -------
        >>> OffsetDateTime.parse_common_iso("2020-08-15T23:12:00+02:00")
        OffsetDateTime(2020-08-15 23:12:00+02:00)
        """
        return cls._from_py_unchecked(*_offset_dt_from_iso(s))

    @classmethod
    def from_timestamp(
        cls, i: int, /, *, offset: int | TimeDelta, ignore_dst: bool = False
    ) -> OffsetDateTime:
        """Create an instance from a UNIX timestamp (in seconds).

        The inverse of the ``timestamp()`` method.

        Important
        ---------
        Creating an instance from a UNIX timestamp implicitly ignores DST
        and other timezone changes. This because you don't strictly
        know if the given offset is correct for an arbitrary timestamp.
        Instead, use ``Instant.from_timestamp()``
        or ``ZonedDateTime.from_timestamp()`` if you know the timezone.
        Or, if you want to ignore DST and accept potentially incorrect offsets,
        pass ``ignore_dst=True`` to this method. For more information, see
        `the documentation <https://whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic>`_.
        """
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(TIMESTAMP_DST_MSG)
        secs, fract = divmod(i, 1)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _load_offset(offset)),
            int(fract * 1_000_000_000),
        )

    @classmethod
    def from_timestamp_millis(
        cls, i: int, /, *, offset: int | TimeDelta, ignore_dst: bool = False
    ) -> OffsetDateTime:
        """Create an instance from a UNIX timestamp (in milliseconds).

        The inverse of the ``timestamp_millis()`` method.

        Important
        ---------
        Creating an instance from a UNIX timestamp implicitly ignores DST
        and other timezone changes. This because you don't strictly
        know if the given offset is correct for an arbitrary timestamp.
        Instead, use ``Instant.from_timestamp_millis()``
        or ``ZonedDateTime.from_timestamp_millis()`` if you know the timezone.
        Or, if you want to ignore DST and accept potentially incorrect offsets,
        pass ``ignore_dst=True`` to this method. For more information, see
        `the documentation <https://whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic>`_.
        """
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(TIMESTAMP_DST_MSG)
        if not isinstance(i, int):
            raise TypeError("method requires an integer")
        secs, millis = divmod(i, 1_000)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _load_offset(offset)), millis * 1_000_000
        )

    @classmethod
    def from_timestamp_nanos(
        cls, i: int, /, *, offset: int | TimeDelta, ignore_dst: bool = False
    ) -> OffsetDateTime:
        """Create an instance from a UNIX timestamp (in nanoseconds).

        The inverse of the ``timestamp_nanos()`` method.

        Important
        ---------
        Creating an instance from a UNIX timestamp implicitly ignores DST
        and other timezone changes. This because you don't strictly
        know if the given offset is correct for an arbitrary timestamp.
        Instead, use ``Instant.from_timestamp_nanos()``
        or ``ZonedDateTime.from_timestamp_nanos()`` if you know the timezone.
        Or, if you want to ignore DST and accept potentially incorrect offsets,
        pass ``ignore_dst=True`` to this method. For more information, see
        `the documentation <https://whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic>`_.
        """
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(TIMESTAMP_DST_MSG)
        if not isinstance(i, int):
            raise TypeError("method requires an integer")
        secs, nanos = divmod(i, 1_000_000_000)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _load_offset(offset)), nanos
        )

    @classmethod
    def from_py_datetime(cls, d: _datetime, /) -> OffsetDateTime:
        """Create an instance from a standard library ``datetime`` object.
        The datetime must be aware.

        The inverse of the ``py_datetime()`` method.

        """
        if d.tzinfo is None or (offset := d.utcoffset()) is None:
            raise ValueError(
                "Cannot create from a naive datetime. "
                "Use PlainDateTime.from_py_datetime() for this."
            )
        elif offset.microseconds:
            raise ValueError("Sub-second offsets are not supported")
        return cls._from_py_unchecked(
            _check_utc_bounds(
                _strip_subclasses(
                    d.replace(microsecond=0, tzinfo=_timezone(offset))
                )
            ),
            d.microsecond * 1_000,
        )

    def replace(
        self, /, ignore_dst: bool = False, **kwargs: Any
    ) -> OffsetDateTime:
        """Construct a new instance with the given fields replaced.

        Important
        ---------
        Replacing fields of an offset datetime implicitly ignores DST
        and other timezone changes. This because it isn't guaranteed that
        the same offset will be valid at the new time.
        If you want to account for DST, convert to a ``ZonedDateTime`` first.
        Or, if you want to ignore DST and accept potentially incorrect offsets,
        pass ``ignore_dst=True`` to this method.
        """
        _check_invalid_replace_kwargs(kwargs)
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(ADJUST_OFFSET_DATETIME_MSG)
        try:
            kwargs["tzinfo"] = _load_offset(kwargs.pop("offset"))
        except KeyError:
            pass
        nanos = _pop_nanos_kwarg(kwargs, self._nanos)
        return self._from_py_unchecked(
            _check_utc_bounds(self._py_dt.replace(**kwargs)), nanos
        )

    def replace_date(
        self, date: Date, /, *, ignore_dst: bool = False
    ) -> OffsetDateTime:
        """Construct a new instance with the date replaced.

        See the ``replace()`` method for more information.
        """
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(ADJUST_OFFSET_DATETIME_MSG)
        return self._from_py_unchecked(
            _check_utc_bounds(
                _datetime.combine(date._py_date, self._py_dt.timetz())
            ),
            self._nanos,
        )

    def replace_time(
        self, time: Time, /, *, ignore_dst: bool = False
    ) -> OffsetDateTime:
        """Construct a new instance with the time replaced.

        See the ``replace()`` method for more information.
        """
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(ADJUST_OFFSET_DATETIME_MSG)
        return self._from_py_unchecked(
            _check_utc_bounds(
                _datetime.combine(
                    self._py_dt.date(), time._py_time, self._py_dt.tzinfo
                )
            ),
            time._nanos,
        )

    def __hash__(self) -> int:
        return hash((self._py_dt, self._nanos))

    def __sub__(self, other: _ExactTime) -> TimeDelta:
        """Calculate the duration relative to another exact time."""
        if isinstance(other, (TimeDelta, DateDelta, DateTimeDelta)):
            raise ImplicitlyIgnoringDST(ADJUST_OFFSET_DATETIME_MSG)
        return super().__sub__(other)  # type: ignore[misc, no-any-return]

    @classmethod
    def parse_strptime(cls, s: str, /, *, format: str) -> OffsetDateTime:
        """Parse a datetime with offset using the standard library ``strptime()`` method.

        Example
        -------
        >>> OffsetDateTime.parse_strptime("2020-08-15+0200", format="%Y-%m-%d%z")
        OffsetDateTime(2020-08-15 00:00:00+02:00)

        Note
        ----
        This method defers to the standard library ``strptime()`` method,
        which may behave differently in different Python versions.
        It also only supports up to microsecond precision.

        Important
        ---------
        An offset *must* be present in the format string.
        This means you MUST include the directive ``%z``, ``%Z``, or ``%:z``.
        To parse a datetime without an offset, use ``PlainDateTime`` instead.
        """
        parsed = _datetime.strptime(s, format)
        if (offset := parsed.utcoffset()) is None:
            raise ValueError(
                "Parsed datetime must have an offset. "
                "Use %z, %Z, or %:z in the format string"
            )
        if offset.microseconds:
            raise ValueError("Sub-second offsets are not supported")
        return cls._from_py_unchecked(
            _check_utc_bounds(parsed.replace(microsecond=0)),
            parsed.microsecond * 1_000,
        )

    def format_rfc2822(self) -> str:
        """Format as an RFC 2822 string.

        The inverse of the ``parse_rfc2822()`` method.

        Example
        -------
        >>> OffsetDateTime(2020, 8, 15, 23, 12, offset=hours(2)).format_rfc2822()
        "Sat, 15 Aug 2020 23:12:00 +0200"
        """
        offset = int(self._py_dt.utcoffset().total_seconds())  # type: ignore[union-attr]
        offset_sign = "-" if offset < 0 else "+"
        offset = abs(offset)
        offset_h = offset // 3600
        offset_m = (offset % 3600) // 60
        return (
            f"{_WEEKDAY_TO_RFC2822[self._py_dt.weekday()]}, "
            f"{self._py_dt.day:02} "
            f"{_MONTH_TO_RFC2822[self._py_dt.month]} {self._py_dt.year:04} "
            f"{self._py_dt.time()} "
            f"{offset_sign}{offset_h:02}{offset_m:02}"
        )

    @classmethod
    def parse_rfc2822(cls, s: str, /) -> OffsetDateTime:
        """Parse an offset datetime in RFC 2822 format.

        The inverse of the ``format_rfc2822()`` method.

        Example
        -------
        >>> OffsetDateTime.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 +0200")
        OffsetDateTime(2020-08-15 23:12:00+02:00)
        >>> # also valid:
        >>> OffsetDateTime.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 UT")
        >>> OffsetDateTime.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 GMT")
        >>> OffsetDateTime.parse_rfc2822("Sat, 15 Aug 2020 23:12:00 MST")

        Note
        ----
        - Strictly speaking, an offset of ``-0000`` means that the offset
          is "unknown". Here, we treat it the same as +0000.
        - Although technically part of the RFC 2822 standard,
          comments within folding whitespace are not supported.
        """
        return cls._from_py_unchecked(_parse_rfc2822(s), 0)

    @no_type_check
    def add(self, *args, **kwargs) -> OffsetDateTime:
        """Add a time amount to this datetime.

        Important
        ---------
        Shifting a fixed-offset datetime implicitly ignore DST
        and other timezone changes. This because it isn't guaranteed that
        the same offset will be valid at the resulting time.
        If you want to account for DST, convert to a ``ZonedDateTime`` first.
        Or, if you want to ignore DST and accept potentially incorrect offsets,
        pass ``ignore_dst=True`` to this method.

        For more information, see
        `the documentation <https://whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic>`_.
        """
        return self._shift(1, *args, **kwargs)

    @no_type_check
    def subtract(self, *args, **kwargs) -> OffsetDateTime:
        """Subtract a time amount from this datetime.

        Important
        ---------
        Shifting a fixed-offset datetime implicitly ignore DST
        and other timezone changes. This because it isn't guaranteed that
        the same offset will be valid at the resulting time.
        If you want to account for DST, convert to a ``ZonedDateTime`` first.
        Or, if you want to ignore DST and accept potentially incorrect offsets,
        pass ``ignore_dst=True`` to this method.

        For more information, see
        `the documentation <https://whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic>`_.
        """
        return self._shift(-1, *args, **kwargs)

    @no_type_check
    def _shift(
        self,
        sign: int,
        arg: Delta | _UNSET = _UNSET,
        /,
        *,
        ignore_dst: bool = False,
        **kwargs,
    ) -> OffsetDateTime:
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(ADJUST_OFFSET_DATETIME_MSG)
        elif kwargs:
            if arg is _UNSET:
                return self._shift_kwargs(sign, **kwargs)
            raise TypeError("Cannot mix positional and keyword arguments")

        elif arg is not _UNSET:
            return self._shift_kwargs(
                sign,
                months=arg._date_part._months,
                days=arg._date_part._days,
                nanoseconds=arg._time_part._total_ns,
            )
        else:
            return self

    def _shift_kwargs(
        self,
        sign: int,
        *,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
    ) -> OffsetDateTime:

        py_dt_with_new_date = self.replace_date(
            self.date()
            ._add_months(sign * (years * 12 + months))
            ._add_days(sign * (weeks * 7 + days)),
            ignore_dst=True,
        )._py_dt

        tdelta = sign * TimeDelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
            nanoseconds=nanoseconds,
        )

        delta_secs, nanos = divmod(
            tdelta._total_ns + self._nanos, 1_000_000_000
        )
        return self._from_py_unchecked(
            (py_dt_with_new_date + _timedelta(seconds=delta_secs)),
            nanos,
        )

    def round(
        self,
        unit: Literal[
            "day",
            "hour",
            "minute",
            "second",
            "millisecond",
            "microsecond",
            "nanosecond",
        ] = "second",
        increment: int = 1,
        mode: Literal[
            "ceil", "floor", "half_ceil", "half_floor", "half_even"
        ] = "half_even",
        *,
        ignore_dst: bool = False,
    ) -> OffsetDateTime:
        """Round the datetime to the specified unit and increment.
        Different rounding modes are available.

        Examples
        --------
        >>> d = OffsetDateTime(2020, 8, 15, 23, 24, 18, offset=+4)
        >>> d.round("day")
        OffsetDateTime(2020-08-16 00:00:00[+04:00])
        >>> d.round("minute", increment=15, mode="floor")
        OffsetDateTime(2020-08-15 23:15:00[+04:00])

        Note
        ----
        * The ``ignore_dst`` parameter is required, because it is possible
          (though unlikely) that the rounded datetime will not have the same offset.
        * This method has similar behavior to the ``round()`` method of
          Temporal objects in JavaScript.
        """
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(OFFSET_ROUNDING_DST_MSG)
        return (
            self.to_plain()
            ._round_unchecked(
                increment_to_ns(unit, increment, any_hour_ok=False),
                mode,
                86_400_000_000_000,
            )
            .assume_fixed_offset(self.offset)
        )

    def __repr__(self) -> str:
        return f"OffsetDateTime({str(self).replace('T', ' ')})"

    # a custom pickle implementation with a smaller payload
    def __reduce__(self) -> tuple[object, ...]:
        return (
            _unpkl_offset,
            (
                pack(
                    "<HBBBBBil",
                    *self._py_dt.timetuple()[:6],
                    self._nanos,
                    int(self._py_dt.utcoffset().total_seconds()),  # type: ignore[union-attr]
                ),
            ),
        )


# A separate function is needed for unpickling, because the
# constructor doesn't accept positional offset argument as
# required by __reduce__.
# Also, it allows backwards-compatible changes to the pickling format.
def _unpkl_offset(data: bytes) -> OffsetDateTime:
    *args, nanos, offset_secs = unpack("<HBBBBBil", data)
    args += (0, _timezone(_timedelta(seconds=offset_secs)))
    return OffsetDateTime._from_py_unchecked(_datetime(*args), nanos)


@final
class ZonedDateTime(_ExactAndLocalTime):
    """A datetime associated with a timezone in the IANA database.
    Useful for representing the exact time at a specific location.

    Example
    -------
    >>> ZonedDateTime(2024, 12, 8, hour=11, tz="Europe/Paris")
    ZonedDateTime(2024-12-08 11:00:00+01:00[Europe/Paris])
    >>> # Explicitly resolve ambiguities during DST transitions
    >>> ZonedDateTime(2023, 10, 29, 1, 15, tz="Europe/London", disambiguate="earlier")
    ZonedDateTime(2023-10-29 01:15:00+01:00[Europe/London])

    Important
    ---------
    To use this type properly, read more about
    `ambiguity in timezones <https://whenever.rtfd.io/en/latest/overview.html#ambiguity-in-timezones>`_.
    """

    __slots__ = ()

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        *,
        nanosecond: int = 0,
        tz: str,
        disambiguate: Disambiguate = "compatible",
    ) -> None:
        self._py_dt = _resolve_ambiguity(
            _datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
                0,
                zone := _get_tz(tz),
            ),
            zone,
            disambiguate,
        )
        if nanosecond < 0 or nanosecond >= 1_000_000_000:
            raise ValueError(f"nanosecond out of range: {nanosecond}")
        self._nanos = nanosecond

    @classmethod
    def now(cls, tz: str, /) -> ZonedDateTime:
        """Create an instance from the current time in the given timezone."""
        secs, nanos = divmod(time_ns(), 1_000_000_000)
        return cls._from_py_unchecked(_fromtimestamp(secs, _get_tz(tz)), nanos)

    def format_common_iso(self) -> str:
        """Convert to the popular ISO format ``YYYY-MM-DDTHH:MM:SS±HH:MM[TZ_ID]``

        The inverse of the ``parse_common_iso()`` method.

        Example
        -------
        >>> ZonedDateTime(2020, 8, 15, hour=23, minute=12, tz="Europe/London")
        ZonedDateTime(2020-08-15 23:12:00+01:00[Europe/London])

        Important
        ---------
        The timezone ID is a recent extension to the ISO 8601 format (RFC 9557).
        Althought it is gaining popularity, it is not yet widely supported
        by ISO 8601 parsers.
        """
        py_isofmt = self._py_dt.isoformat()
        return (
            py_isofmt[:19]  # without the offset
            + bool(self._nanos) * f".{self._nanos:09d}".rstrip("0")
            + py_isofmt[19:]
            + f"[{self._py_dt.tzinfo.key}]"  # type: ignore[union-attr]
        )

    @classmethod
    def parse_common_iso(cls, s: str, /) -> ZonedDateTime:
        """Parse from the popular ISO format ``YYYY-MM-DDTHH:MM:SS±HH:MM[TZ_ID]``

        The inverse of the ``format_common_iso()`` method.

        Example
        -------
        >>> ZonedDateTime.parse_common_iso("2020-08-15T23:12:00+01:00[Europe/London]")
        ZonedDateTime(2020-08-15 23:12:00+01:00[Europe/London])

        Important
        ---------
        The timezone ID is a recent extension to the ISO 8601 format (RFC 9557).
        Althought it is gaining popularity, it is not yet widely supported.
        """
        return cls._from_py_unchecked(*_zdt_from_iso(s))

    @classmethod
    def from_timestamp(cls, i: int, /, *, tz: str) -> ZonedDateTime:
        """Create an instance from a UNIX timestamp (in seconds).

        The inverse of the ``timestamp()`` method.
        """
        secs, fract = divmod(i, 1)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _get_tz(tz)), int(fract * 1_000_000_000)
        )

    @classmethod
    def from_timestamp_millis(cls, i: int, /, *, tz: str) -> ZonedDateTime:
        """Create an instance from a UNIX timestamp (in milliseconds).

        The inverse of the ``timestamp_millis()`` method.
        """
        if not isinstance(i, int):
            raise TypeError("method requires an integer")
        secs, millis = divmod(i, 1_000)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _get_tz(tz)), millis * 1_000_000
        )

    @classmethod
    def from_timestamp_nanos(cls, i: int, /, *, tz: str) -> ZonedDateTime:
        """Create an instance from a UNIX timestamp (in nanoseconds).

        The inverse of the ``timestamp_nanos()`` method.
        """
        if not isinstance(i, int):
            raise TypeError("method requires an integer")
        secs, nanos = divmod(i, 1_000_000_000)
        return cls._from_py_unchecked(_fromtimestamp(secs, _get_tz(tz)), nanos)

    # FUTURE: optional `disambiguate` to override fold?
    @classmethod
    def from_py_datetime(cls, d: _datetime, /) -> ZonedDateTime:
        """Create an instance from a standard library ``datetime`` object
        with a ``ZoneInfo`` tzinfo.

        The inverse of the ``py_datetime()`` method.

        Attention
        ---------
        If the datetime is ambiguous (e.g. during a DST transition),
        the ``fold`` attribute is used to disambiguate the time.
        """
        from zoneinfo import ZoneInfo

        if type(d.tzinfo) is not ZoneInfo:
            raise ValueError(
                "Can only create ZonedDateTime from tzinfo=ZoneInfo (exactly), "
                f"got datetime with tzinfo={d.tzinfo!r}"
            )
        if d.tzinfo.key is None:
            raise ValueError(ZONEINFO_NO_KEY_MSG)

        # This ensures skipped times are disambiguated according to the fold.
        d = d.astimezone(_UTC).astimezone(_get_tz(d.tzinfo.key))
        return cls._from_py_unchecked(
            _strip_subclasses(d.replace(microsecond=0)), d.microsecond * 1_000
        )

    def replace_date(
        self, date: Date, /, disambiguate: Disambiguate | None = None
    ) -> ZonedDateTime:
        """Construct a new instance with the date replaced.

        See the ``replace()`` method for more information.
        """
        return self._from_py_unchecked(
            _resolve_ambiguity(
                _datetime.combine(date._py_date, self._py_dt.timetz()),
                # mypy doesn't know that tzinfo is always a ZoneInfo here
                self._py_dt.tzinfo,  # type: ignore[arg-type]
                # mypy doesn't know that offset is never None here
                disambiguate or self._py_dt.utcoffset(),  # type: ignore[arg-type]
            ),
            self._nanos,
        )

    def replace_time(
        self, time: Time, /, disambiguate: Disambiguate | None = None
    ) -> ZonedDateTime:
        """Construct a new instance with the time replaced.

        See the ``replace()`` method for more information.
        """
        return self._from_py_unchecked(
            _resolve_ambiguity(
                _datetime.combine(
                    self._py_dt, time._py_time, self._py_dt.tzinfo
                ),
                # mypy doesn't know that tzinfo is always a ZoneInfo here
                self._py_dt.tzinfo,  # type: ignore[arg-type]
                # mypy doesn't know that offset is never None here
                disambiguate or self._py_dt.utcoffset(),  # type: ignore[arg-type]
            ),
            time._nanos,
        )

    def replace(
        self, /, disambiguate: Disambiguate | None = None, **kwargs: Any
    ) -> ZonedDateTime:
        """Construct a new instance with the given fields replaced.

        Important
        ---------
        Replacing fields of a ZonedDateTime may result in an ambiguous time
        (e.g. during a DST transition). Therefore, it's recommended to
        specify how to handle such a situation using the ``disambiguate`` argument.

        By default, if the tz remains the same, the offset is used to disambiguate
        if possible, falling back to the "compatible" strategy if needed.

        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#ambiguity-in-timezones>`_
        for more information.
        """

        _check_invalid_replace_kwargs(kwargs)
        try:
            tz = kwargs.pop("tz")
        except KeyError:
            pass
        else:
            kwargs["tzinfo"] = zoneinfo_new = _get_tz(tz)
            if zoneinfo_new is not self._py_dt.tzinfo:
                disambiguate = disambiguate or "compatible"
        nanos = _pop_nanos_kwarg(kwargs, self._nanos)

        return self._from_py_unchecked(
            _resolve_ambiguity(
                self._py_dt.replace(**kwargs),
                kwargs.get("tzinfo", self._py_dt.tzinfo),  # type: ignore[arg-type]
                # mypy doesn't know that offset is never None here
                disambiguate or self._py_dt.utcoffset(),  # type: ignore[arg-type]
            ),
            nanos,
        )

    @property
    def tz(self) -> str:
        """The timezone ID"""
        return self._py_dt.tzinfo.key  # type: ignore[union-attr,no-any-return]

    def __hash__(self) -> int:
        return hash((self._py_dt.astimezone(_UTC), self._nanos))

    def __add__(self, delta: Delta) -> ZonedDateTime:
        """Add an amount of time, accounting for timezone changes (e.g. DST).

        See `the docs <https://whenever.rtfd.io/en/latest/overview.html#arithmetic>`_
        for more information.
        """
        if isinstance(delta, TimeDelta):
            delta_secs, nanos = divmod(
                delta._time_part._total_ns + self._nanos, 1_000_000_000
            )
            return self._from_py_unchecked(
                (
                    self._py_dt.astimezone(_UTC)
                    + _timedelta(seconds=delta_secs)
                ).astimezone(self._py_dt.tzinfo),
                nanos,
            )
        elif isinstance(delta, DateDelta):
            return self.replace_date(self.date() + delta)
        elif isinstance(delta, DateTimeDelta):
            return (
                self.replace_date(self.date() + delta._date_part)
                + delta._time_part
            )
        return NotImplemented

    @overload
    def __sub__(self, other: _ExactTime) -> TimeDelta: ...

    @overload
    def __sub__(self, other: TimeDelta) -> ZonedDateTime: ...

    def __sub__(self, other: TimeDelta | _ExactTime) -> _ExactTime | TimeDelta:
        """Subtract another datetime or duration.

        See `the docs <https://whenever.rtfd.io/en/latest/overview.html#arithmetic>`_
        for more information.
        """
        if isinstance(other, _ExactTime):
            return super().__sub__(other)  # type: ignore[misc, no-any-return]
        elif isinstance(other, (TimeDelta, DateDelta, DateTimeDelta)):
            return self + -other
        return NotImplemented

    @no_type_check
    def add(self, *args, **kwargs) -> ZonedDateTime:
        """Add a time amount to this datetime.

        Important
        ---------
        Shifting a ``ZonedDateTime`` with **calendar units** (e.g. months, weeks)
        may result in an ambiguous time (e.g. during a DST transition).
        Therefore, when adding calendar units, it's recommended to
        specify how to handle such a situation using the ``disambiguate`` argument.

        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#arithmetic>`_
        for more information.
        """
        return self._shift(1, *args, **kwargs)

    @no_type_check
    def subtract(self, *args, **kwargs) -> ZonedDateTime:
        """Subtract a time amount from this datetime.

        Important
        ---------
        Shifting a ``ZonedDateTime`` with **calendar units** (e.g. months, weeks)
        may result in an ambiguous time (e.g. during a DST transition).
        Therefore, when adding calendar units, it's recommended to
        specify how to handle such a situation using the ``disambiguate`` argument.

        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#arithmetic>`_
        for more information.
        """
        return self._shift(-1, *args, **kwargs)

    @no_type_check
    def _shift(
        self,
        sign: int,
        delta: Delta | _UNSET = _UNSET,
        /,
        *,
        disambiguate: Disambiguate | None = None,
        **kwargs,
    ) -> ZonedDateTime:
        if kwargs:
            if delta is _UNSET:
                return self._shift_kwargs(
                    sign, disambiguate=disambiguate, **kwargs
                )
            raise TypeError("Cannot mix positional and keyword arguments")

        elif delta is not _UNSET:
            return self._shift_kwargs(
                sign,
                months=delta._date_part._months,
                days=delta._date_part._days,
                nanoseconds=delta._time_part._total_ns,
                disambiguate=disambiguate,
            )
        else:
            return self

    def _shift_kwargs(
        self,
        sign: int,
        *,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
        disambiguate: Disambiguate | None,
    ) -> ZonedDateTime:
        months_total = sign * (years * 12 + months)
        days_total = sign * (weeks * 7 + days)
        if months_total or days_total:
            self = self.replace_date(
                self.date()._add_months(months_total)._add_days(days_total),
                disambiguate=disambiguate,
            )
        return self + sign * TimeDelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
            nanoseconds=nanoseconds,
        )

    def is_ambiguous(self) -> bool:
        """Whether the date and time-of-day are ambiguous, e.g. due to a DST transition.

        Example
        -------
        >>> ZonedDateTime(2020, 8, 15, 23, tz="Europe/London").is_ambiguous()
        False
        >>> ZonedDateTime(2023, 10, 29, 2, 15, tz="Europe/Amsterdam").is_ambiguous()
        True
        """
        # We make use of a quirk of the standard library here:
        # ambiguous datetimes are never equal across timezones
        return self._py_dt.astimezone(_UTC) != self._py_dt

    def day_length(self) -> TimeDelta:
        """The duration between the start of the current day and the next.
        This is usually 24 hours, but may be different due to timezone transitions.

        Example
        -------
        >>> ZonedDateTime(2020, 8, 15, tz="Europe/London").day_length()
        TimeDelta(24:00:00)
        >>> ZonedDateTime(2023, 10, 29, tz="Europe/Amsterdam").day_length()
        TimeDelta(25:00:00)
        """
        midnight = _datetime.combine(
            self._py_dt.date(), _time(), self._py_dt.tzinfo
        )
        next_midnight = midnight + _timedelta(days=1)
        return TimeDelta.from_py_timedelta(
            next_midnight.astimezone(_UTC) - midnight.astimezone(_UTC)
        )

    def start_of_day(self) -> ZonedDateTime:
        """The start of the current calendar day.

        This is almost always at midnight the same day, but may be different
        for timezones which transition at—and thus skip over—midnight.
        """
        midnight = _datetime.combine(
            self._py_dt.date(), _time(), self._py_dt.tzinfo
        )
        return self._from_py_unchecked(
            midnight.astimezone(_UTC).astimezone(self._py_dt.tzinfo), 0
        )

    def round(
        self,
        unit: Literal[
            "day",
            "hour",
            "minute",
            "second",
            "millisecond",
            "microsecond",
            "nanosecond",
        ] = "second",
        increment: int = 1,
        mode: Literal[
            "ceil", "floor", "half_ceil", "half_floor", "half_even"
        ] = "half_even",
    ) -> ZonedDateTime:
        """Round the datetime to the specified unit and increment.
        Different rounding modes are available.

        Examples
        --------
        >>> d = ZonedDateTime(2020, 8, 15, 23, 24, 18, tz="Europe/Paris")
        >>> d.round("day")
        ZonedDateTime(2020-08-16 00:00:00+02:00[Europe/Paris])
        >>> d.round("minute", increment=15, mode="floor")
        ZonedDateTime(2020-08-15 23:15:00+02:00[Europe/Paris])

        Notes
        -----
        * In the rare case that rounding results in an ambiguous time,
          the offset is preserved if possible.
          Otherwise, the time is resolved according to the "compatible" strategy.
        * Rounding in "day" mode may be affected by DST transitions.
          i.e. on 23-hour days, 11:31 AM is rounded up.
        * This method has similar behavior to the ``round()`` method of
          Temporal objects in JavaScript.
        """
        increment_ns = increment_to_ns(unit, increment, any_hour_ok=False)
        if unit == "day":
            increment_ns = day_ns = self.day_length()._total_ns
        else:
            day_ns = 86_400_000_000_000

        rounded_local = self.to_plain()._round_unchecked(
            increment_ns, mode, day_ns
        )
        return self._from_py_unchecked(
            _resolve_ambiguity_using_prev_offset(
                rounded_local._py_dt.replace(tzinfo=self._py_dt.tzinfo),
                self._py_dt.utcoffset(),  # type: ignore[arg-type]
            ),
            rounded_local._nanos,
        )

    def py_datetime(self) -> _datetime:
        # We convert to UTC first, then to a *non* file based ZoneInfo.
        # We don't just `replace()` the timezone, because in theory
        # they could disagree about the offset. This ensures we keep the
        # same moment in time.
        # FUTURE: write a test for this (a bit complicated)
        from zoneinfo import ZoneInfo

        return (
            self._py_dt.astimezone(_UTC)
            .astimezone(
                ZoneInfo(self._py_dt.tzinfo.key)  # type: ignore[union-attr]
            )
            .replace(
                microsecond=self._nanos // 1_000,
            )
        )

    def __repr__(self) -> str:
        return f"ZonedDateTime({str(self).replace('T', ' ', 1)})"

    # a custom pickle implementation with a smaller payload
    def __reduce__(self) -> tuple[object, ...]:
        return (
            _unpkl_zoned,
            (
                pack(
                    "<HBBBBBil",
                    *self._py_dt.timetuple()[:6],
                    self._nanos,
                    int(self._py_dt.utcoffset().total_seconds()),  # type: ignore[union-attr]
                ),
                self._py_dt.tzinfo.key,  # type: ignore[union-attr]
            ),
        )


# A separate function is needed for unpickling, because the
# constructor doesn't accept positional tz and fold arguments as
# required by __reduce__.
# Also, it allows backwards-compatible changes to the pickling format.
def _unpkl_zoned(
    data: bytes,
    tz: str,
) -> ZonedDateTime:
    *args, nanos, offset_secs = unpack("<HBBBBBil", data)
    args += (0, _get_tz(tz))
    return ZonedDateTime._from_py_unchecked(
        _adjust_fold_to_offset(
            _datetime(*args), _timedelta(seconds=offset_secs)
        ),
        nanos,
    )


@final
class SystemDateTime(_ExactAndLocalTime):
    """Represents a time in the system timezone.
    It is similar to ``OffsetDateTime``,
    but it knows about the system timezone and its DST transitions.

    Example
    -------
    >>> # 8:00 in the system timezone—Paris in this case
    >>> alarm = SystemDateTime(2024, 3, 31, hour=6)
    SystemDateTime(2024-03-31 06:00:00+02:00)
    >>> # Conversion based on Paris' offset
    >>> alarm.instant()
    Instant(2024-03-31 04:00:00Z)
    >>> # DST-safe arithmetic
    >>> bedtime = alarm - hours(8)
    SystemDateTime(2024-03-30 21:00:00+01:00)

    Attention
    ---------
    To use this type properly, read more about `ambiguity <https://whenever.rtfd.io/en/latest/overview.html#ambiguity-in-timezones>`_
    and `working with the system timezone <https://whenever.rtfd.io/en/latest/overview.html#the-system-timezone>`_.
    """

    __slots__ = ()

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        *,
        nanosecond: int = 0,
        disambiguate: Disambiguate = "compatible",
    ) -> None:
        self._py_dt = _resolve_system_ambiguity(
            _datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
                0,
            ),
            disambiguate,
        )
        if nanosecond < 0 or nanosecond >= 1_000_000_000:
            raise ValueError("nanosecond out of range")
        self._nanos = nanosecond

    @classmethod
    def now(cls) -> SystemDateTime:
        """Create an instance from the current time in the system timezone."""
        secs, nanos = divmod(time_ns(), 1_000_000_000)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _UTC).astimezone(None), nanos
        )

    format_common_iso = OffsetDateTime.format_common_iso
    """Convert to the popular ISO format ``YYYY-MM-DDTHH:MM:SS±HH:MM``

    The inverse of the ``parse_common_iso()`` method.

    Important
    ---------
    Information about the system timezone name is *not* included in the output.
    """

    @classmethod
    def parse_common_iso(cls, s: str, /) -> SystemDateTime:
        """Parse from the popular ISO format ``YYYY-MM-DDTHH:MM:SS±HH:MM``

        Important
        ---------
        The offset isn't adjusted to the current system timezone.
        See `the docs <https://whenever.rtfd.io/en/latest/overview.html#the-system-timezone>`_
        for more information.
        """
        return cls._from_py_unchecked(*_offset_dt_from_iso(s))

    @classmethod
    def from_timestamp(cls, i: int | float, /) -> SystemDateTime:
        """Create an instance from a UNIX timestamp (in seconds).

        The inverse of the ``timestamp()`` method.
        """
        secs, fract = divmod(i, 1)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _UTC).astimezone(), int(fract * 1_000_000_000)
        )

    @classmethod
    def from_timestamp_millis(cls, i: int, /) -> SystemDateTime:
        """Create an instance from a UNIX timestamp (in milliseconds).

        The inverse of the ``timestamp_millis()`` method.
        """
        if not isinstance(i, int):
            raise TypeError("method requires an integer")
        secs, millis = divmod(i, 1_000)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _UTC).astimezone(), millis * 1_000_000
        )

    @classmethod
    def from_timestamp_nanos(cls, i: int, /) -> SystemDateTime:
        """Create an instance from a UNIX timestamp (in nanoseconds).

        The inverse of the ``timestamp_nanos()`` method.
        """
        if not isinstance(i, int):
            raise TypeError("method requires an integer")
        secs, nanos = divmod(i, 1_000_000_000)
        return cls._from_py_unchecked(
            _fromtimestamp(secs, _UTC).astimezone(), nanos
        )

    @classmethod
    def from_py_datetime(cls, d: _datetime, /) -> SystemDateTime:
        """Create an instance from a standard library ``datetime`` object.
        The datetime must be aware.

        The inverse of the ``py_datetime()`` method.
        """
        odt = OffsetDateTime.from_py_datetime(d)
        return cls._from_py_unchecked(odt._py_dt, odt._nanos)

    def __repr__(self) -> str:
        return f"SystemDateTime({str(self).replace('T', ' ')})"

    # FUTURE: expose the tzname?

    def replace_date(
        self, date: Date, /, disambiguate: Disambiguate | None = None
    ) -> SystemDateTime:
        """Construct a new instance with the date replaced.

        See the ``replace()`` method for more information.
        """
        return self._from_py_unchecked(
            _resolve_system_ambiguity(
                _datetime.combine(date._py_date, self._py_dt.time()),
                # mypy doesn't know that offset is never None here
                disambiguate or self._py_dt.utcoffset(),  # type: ignore[arg-type]
            ),
            self._nanos,
        )

    def replace_time(
        self, time: Time, /, disambiguate: Disambiguate | None = None
    ) -> SystemDateTime:
        """Construct a new instance with the time replaced.

        See the ``replace()`` method for more information.
        """
        return self._from_py_unchecked(
            _resolve_system_ambiguity(
                _datetime.combine(self._py_dt, time._py_time),
                # mypy doesn't know that offset is never None here
                disambiguate or self._py_dt.utcoffset(),  # type: ignore[arg-type]
            ),
            time._nanos,
        )

    def replace(
        self, /, disambiguate: Disambiguate | None = None, **kwargs: Any
    ) -> SystemDateTime:
        """Construct a new instance with the given fields replaced.

        Important
        ---------
        Replacing fields of a SystemDateTime may result in an ambiguous time
        (e.g. during a DST transition). Therefore, it's recommended to
        specify how to handle such a situation using the ``disambiguate`` argument.

        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#ambiguity-in-timezones>`_
        for more information.
        """
        _check_invalid_replace_kwargs(kwargs)
        nanos = _pop_nanos_kwarg(kwargs, self._nanos)
        return self._from_py_unchecked(
            _resolve_system_ambiguity(
                self._py_dt.replace(tzinfo=None, **kwargs),
                # mypy doesn't know that offset is never None here
                disambiguate or self._py_dt.utcoffset(),  # type: ignore[arg-type]
            ),
            nanos,
        )

    def __hash__(self) -> int:
        return hash((self._py_dt, self._nanos))

    def __add__(self, delta: TimeDelta) -> SystemDateTime:
        """Add an amount of time, accounting for timezone changes (e.g. DST).

        See `the docs <https://whenever.rtfd.io/en/latest/overview.html#arithmetic>`_
        for more information.
        """
        if isinstance(delta, TimeDelta):
            py_dt = self._py_dt
            delta_secs, nanos = divmod(
                delta._time_part._total_ns + self._nanos, 1_000_000_000
            )
            return self._from_py_unchecked(
                (py_dt + _timedelta(seconds=delta_secs)).astimezone(), nanos
            )
        elif isinstance(delta, DateDelta):
            return self.replace_date(self.date() + delta)
        elif isinstance(delta, DateTimeDelta):
            return (
                self.replace_date(self.date() + delta._date_part)
                + delta._time_part
            )
        return NotImplemented

    @overload
    def __sub__(self, other: _ExactTime) -> TimeDelta: ...

    @overload
    def __sub__(self, other: TimeDelta) -> SystemDateTime: ...

    def __sub__(self, other: TimeDelta | _ExactTime) -> _ExactTime | Delta:
        """Subtract another datetime or duration

        See `the docs <https://whenever.rtfd.io/en/latest/overview.html#arithmetic>`_
        for more information.
        """
        if isinstance(other, _ExactTime):
            return super().__sub__(other)  # type: ignore[misc, no-any-return]
        elif isinstance(other, (TimeDelta, DateDelta, DateTimeDelta)):
            return self + -other
        return NotImplemented

    @no_type_check
    def add(self, *args, **kwargs) -> SystemDateTime:
        """Add a time amount to this datetime.

        Important
        ---------
        Shifting a ``SystemDateTime`` with **calendar units** (e.g. months, weeks)
        may result in an ambiguous time (e.g. during a DST transition).
        Therefore, when adding calendar units, it's recommended to
        specify how to handle such a situation using the ``disambiguate`` argument.

        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#arithmetic>`_
        for more information.
        """
        return self._shift(1, *args, **kwargs)

    @no_type_check
    def subtract(self, *args, **kwargs) -> SystemDateTime:
        """Subtract a time amount from this datetime.

        Important
        ---------
        Shifting a ``SystemDateTime`` with **calendar units** (e.g. months, weeks)
        may result in an ambiguous time (e.g. during a DST transition).
        Therefore, when adding calendar units, it's recommended to
        specify how to handle such a situation using the ``disambiguate`` argument.

        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#arithmetic>`_
        for more information.
        """
        return self._shift(-1, *args, **kwargs)

    @no_type_check
    def _shift(
        self,
        sign: int,
        delta: Delta | _UNSET = _UNSET,
        /,
        *,
        disambiguate: Disambiguate | None = None,
        **kwargs,
    ) -> SystemDateTime:
        if kwargs:
            if delta is _UNSET:
                return self._shift_kwargs(
                    sign, disambiguate=disambiguate, **kwargs
                )
            raise TypeError("Cannot mix positional and keyword arguments")

        elif delta is not _UNSET:
            return self._shift_kwargs(
                sign,
                months=delta._date_part._months,
                days=delta._date_part._days,
                nanoseconds=delta._time_part._total_ns,
                disambiguate=disambiguate,
            )
        else:
            return self

    def _shift_kwargs(
        self,
        sign: int,
        *,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
        disambiguate: Disambiguate | None,
    ) -> SystemDateTime:
        months_total = sign * (years * 12 + months)
        days_total = sign * (weeks * 7 + days)
        if months_total or days_total:
            self = self.replace_date(
                self.date()._add_months(months_total)._add_days(days_total),
                disambiguate=disambiguate,
            )
        return self + sign * TimeDelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
            nanoseconds=nanoseconds,
        )

    def is_ambiguous(self) -> bool:
        """Whether the date and time-of-day is ambiguous, e.g. due to a DST transition.

        Example
        -------
        >>> # with system configured in Europe/Paris
        >>> SystemDateTime(2020, 8, 15, 23).is_ambiguous()
        False
        >>> SystemDateTime(2023, 10, 29, 2, 15).is_ambiguous()
        True

        Note
        ----
        This method may give a different result after a change to the system timezone.
        """
        naive = self._py_dt.replace(tzinfo=None)
        return naive.astimezone(_UTC) != naive.replace(fold=1).astimezone(_UTC)

    def day_length(self) -> TimeDelta:
        """The duration between the start of the current day and the next.
        This is usually 24 hours, but may be different due to timezone transitions.

        Example
        -------
        >>> # with system configured in Europe/Paris
        >>> SystemDateTime(2020, 8, 15).day_length()
        TimeDelta(24:00:00)
        >>> SystemDateTime(2023, 10, 29).day_length()
        TimeDelta(25:00:00)

        Note
        ----
        This method may give a different result after a change to the system timezone.
        """
        midnight = _datetime.combine(self._py_dt.date(), _time())
        next_midnight = midnight + _timedelta(days=1)
        return TimeDelta.from_py_timedelta(
            _resolve_system_ambiguity(next_midnight, "compatible")
            - _resolve_system_ambiguity(midnight, "compatible")
        )

    def start_of_day(self) -> SystemDateTime:
        """The start of the current calendar day.

        This is almost always at midnight the same day, but may be different
        for timezones which transition at—and thus skip over—midnight.

        Note
        ----
        This method may give a different result after a change to the system timezone.
        """
        midnight = _datetime.combine(self._py_dt.date(), _time())
        return self._from_py_unchecked(
            _resolve_system_ambiguity(midnight, "compatible"), 0
        )

    def round(
        self,
        unit: Literal[
            "day",
            "hour",
            "minute",
            "second",
            "millisecond",
            "microsecond",
            "nanosecond",
        ] = "second",
        increment: int = 1,
        mode: Literal[
            "ceil", "floor", "half_ceil", "half_floor", "half_even"
        ] = "half_even",
    ) -> SystemDateTime:
        """Round the datetime to the specified unit and increment.
        Different rounding modes are available.

        Examples
        --------
        >>> d = SystemDateTime(2020, 8, 15, 23, 24, 18)
        >>> d.round("day")
        SystemDateTime(2020-08-16 00:00:00+02:00)
        >>> d.round("minute", increment=15, mode="floor")
        SystemDateTime(2020-08-15 23:15:00+02:00)

        Notes
        -----
        * In the rare case that rounding results in an ambiguous time,
          the offset is preserved if possible.
          Otherwise, the time is resolved according to the "compatible" strategy.
        * Rounding in "day" mode may be affected by DST transitions.
          i.e. on 23-hour days, 11:31 AM is rounded up.
        * This method has similar behavior to the ``round()`` method of
          Temporal objects in JavaScript.
        * The result of this method may change if the system timezone changes.
        """
        increment_ns = increment_to_ns(unit, increment, any_hour_ok=False)
        if unit == "day":
            increment_ns = day_ns = self.day_length()._total_ns
        else:
            day_ns = 86_400_000_000_000

        rounded_local = self.to_plain()._round_unchecked(
            increment_ns, mode, day_ns
        )
        return self._from_py_unchecked(
            _resolve_system_ambiguity_using_prev_offset(
                rounded_local._py_dt,
                self._py_dt.utcoffset(),  # type: ignore[arg-type]
            ),
            rounded_local._nanos,
        )

    # a custom pickle implementation with a smaller payload
    def __reduce__(self) -> tuple[object, ...]:
        return (
            _unpkl_system,
            (
                pack(
                    "<HBBBBBil",
                    *self._py_dt.timetuple()[:6],
                    self._nanos,
                    int(self._py_dt.utcoffset().total_seconds()),  # type: ignore[union-attr]
                ),
            ),
        )


# A separate function is needed for unpickling, because the
# constructor doesn't accept positional fold arguments as
# required by __reduce__.
# Also, it allows backwards-compatible changes to the pickling format.
def _unpkl_system(data: bytes) -> SystemDateTime:
    *args, nanos, offset_secs = unpack("<HBBBBBil", data)
    args += (0, _timezone(_timedelta(seconds=offset_secs)))
    return SystemDateTime._from_py_unchecked(_datetime(*args), nanos)


@final
class PlainDateTime(_LocalTime):
    """A combination of date and time-of-day, without a timezone.

    Can be used to represent local time, i.e. how time appears to people
    on a wall clock.

    It can't be mixed with exact time types (e.g. ``Instant``, ``ZonedDateTime``)
    Conversion to exact time types can only be done by
    explicitly assuming a timezone or offset.

    Examples of when to use this type:

    - You need to express a date and time as it would be observed locally
      on the "wall clock" or calendar.
    - You receive a date and time without any timezone information,
      and you need a type to represent this lack of information.
    - In the rare case you truly don't need to account for timezones,
      or Daylight Saving Time transitions. For example, when modeling
      time in a simulation game.
    """

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        *,
        nanosecond: int = 0,
    ) -> None:
        self._py_dt = _datetime(year, month, day, hour, minute, second)
        self._nanos = nanosecond

    def format_common_iso(self) -> str:
        """Convert to the popular ISO format ``YYYY-MM-DDTHH:MM:SS``

        The inverse of the ``parse_common_iso()`` method.
        """
        return (
            (self._py_dt.isoformat() + f".{self._nanos:09d}").rstrip("0")
            if self._nanos
            else self._py_dt.isoformat()
        )

    @classmethod
    def parse_common_iso(cls, s: str, /) -> PlainDateTime:
        """Parse the popular ISO format ``YYYY-MM-DDTHH:MM:SS``

        The inverse of the ``format_common_iso()`` method.

        Example
        -------
        >>> PlainDateTime.parse_common_iso("2020-08-15T23:12:00")
        PlainDateTime(2020-08-15 23:12:00)
        """
        return cls._from_py_unchecked(*_datetime_from_iso(s))

    @classmethod
    def from_py_datetime(cls, d: _datetime, /) -> PlainDateTime:
        """Create an instance from a "naive" standard library ``datetime`` object"""
        if d.tzinfo is not None:
            raise ValueError(
                "Can only create PlainDateTime from a naive datetime, "
                f"got datetime with tzinfo={d.tzinfo!r}"
            )
        return cls._from_py_unchecked(
            _strip_subclasses(d.replace(microsecond=0)), d.microsecond * 1_000
        )

    def replace(self, /, **kwargs: Any) -> PlainDateTime:
        """Construct a new instance with the given fields replaced."""
        if not _no_tzinfo_fold_or_ms(kwargs):
            raise TypeError(
                "tzinfo, fold, or microsecond are not allowed arguments"
            )
        nanos = _pop_nanos_kwarg(kwargs, self._nanos)
        return self._from_py_unchecked(self._py_dt.replace(**kwargs), nanos)

    def replace_date(self, d: Date, /) -> PlainDateTime:
        """Construct a new instance with the date replaced."""
        return self._from_py_unchecked(
            _datetime.combine(d._py_date, self._py_dt.time()), self._nanos
        )

    def replace_time(self, t: Time, /) -> PlainDateTime:
        """Construct a new instance with the time replaced."""
        return self._from_py_unchecked(
            _datetime.combine(self._py_dt.date(), t._py_time), t._nanos
        )

    def __hash__(self) -> int:
        return hash((self._py_dt, self._nanos))

    def __eq__(self, other: object) -> bool:
        """Compare objects for equality.
        Only ever equal to other :class:`PlainDateTime` instances with the
        same values.

        Warning
        -------
        To comply with the Python data model, this method can't
        raise a :exc:`TypeError` when comparing with other types.
        Although it seems to be the sensible response, it would result in
        `surprising behavior <https://stackoverflow.com/a/33417512>`_
        when using values as dictionary keys.

        Use mypy's ``--strict-equality`` flag to detect and prevent this.

        Example
        -------
        >>> PlainDateTime(2020, 8, 15, 23) == PlainDateTime(2020, 8, 15, 23)
        True
        >>> PlainDateTime(2020, 8, 15, 23, 1) == PlainDateTime(2020, 8, 15, 23)
        False
        >>> PlainDateTime(2020, 8, 15) == Instant.from_utc(2020, 8, 15)
        False  # Use mypy's --strict-equality flag to detect this.
        """
        if not isinstance(other, PlainDateTime):
            return NotImplemented
        return (self._py_dt, self._nanos) == (other._py_dt, other._nanos)

    MIN: ClassVar[PlainDateTime]
    """The minimum representable value of this type."""
    MAX: ClassVar[PlainDateTime]
    """The maximum representable value of this type."""

    def __lt__(self, other: PlainDateTime) -> bool:
        if not isinstance(other, PlainDateTime):
            return NotImplemented
        return (self._py_dt, self._nanos) < (other._py_dt, other._nanos)

    def __le__(self, other: PlainDateTime) -> bool:
        if not isinstance(other, PlainDateTime):
            return NotImplemented
        return (self._py_dt, self._nanos) <= (other._py_dt, other._nanos)

    def __gt__(self, other: PlainDateTime) -> bool:
        if not isinstance(other, PlainDateTime):
            return NotImplemented
        return (self._py_dt, self._nanos) > (other._py_dt, other._nanos)

    def __ge__(self, other: PlainDateTime) -> bool:
        if not isinstance(other, PlainDateTime):
            return NotImplemented
        return (self._py_dt, self._nanos) >= (other._py_dt, other._nanos)

    def __add__(self, delta: DateDelta) -> PlainDateTime:
        """Add a delta to this datetime.

        See :ref:`the docs on arithmetic <arithmetic>` for more information.
        """
        if isinstance(delta, DateDelta):
            return self._from_py_unchecked(
                _datetime.combine(
                    (self.date() + delta._date_part)._py_date,
                    self._py_dt.time(),
                ),
                self._nanos,
            )
        elif isinstance(delta, (TimeDelta, DateTimeDelta)):
            raise ImplicitlyIgnoringDST(SHIFT_LOCAL_MSG)
        return NotImplemented

    def __sub__(self, other: DateDelta) -> PlainDateTime:
        """Subtract another datetime or delta

        See :ref:`the docs on arithmetic <arithmetic>` for more information.
        """
        # Handling these extra types allows for descriptive error messages
        if isinstance(other, (DateDelta, TimeDelta, DateTimeDelta)):
            return self + -other
        elif isinstance(other, PlainDateTime):
            raise ImplicitlyIgnoringDST(DIFF_OPERATOR_LOCAL_MSG)
        return NotImplemented

    def difference(
        self, other: PlainDateTime, /, *, ignore_dst: bool = False
    ) -> TimeDelta:
        """Calculate the difference between two times without a timezone.

        Important
        ---------
        The difference between two datetimes without a timezone implicitly ignores
        DST transitions and other timezone changes.
        To perform DST-safe operations, convert to a ``ZonedDateTime`` first.
        Or, if you don't know the timezone and accept potentially incorrect results
        during DST transitions, pass ``ignore_dst=True``.
        For more information,
        see `the docs <https://whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic>`_.
        """
        if ignore_dst is not True:
            raise ImplicitlyIgnoringDST(DIFF_LOCAL_MSG)

        py_delta = self._py_dt - other._py_dt
        return TimeDelta(
            seconds=py_delta.days * 86_400 + py_delta.seconds,
            nanoseconds=self._nanos - other._nanos,
        )

    @no_type_check
    def add(self, *args, **kwargs) -> PlainDateTime:
        """Add a time amount to this datetime.

        Important
        ---------
        Shifting a ``PlainDateTime`` with **exact units** (e.g. hours, seconds)
        implicitly ignores DST transitions and other timezone changes.
        If you need to account for these, convert to a ``ZonedDateTime`` first.
        Or, if you don't know the timezone and accept potentially incorrect results
        during DST transitions, pass ``ignore_dst=True``.

        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic>`_
        for more information.
        """
        return self._shift(1, *args, **kwargs)

    @no_type_check
    def subtract(self, *args, **kwargs) -> PlainDateTime:
        """Subtract a time amount from this datetime.

        Important
        ---------
        Shifting a ``PlainDateTime`` with **exact units** (e.g. hours, seconds)
        implicitly ignores DST transitions and other timezone changes.
        If you need to account for these, convert to a ``ZonedDateTime`` first.
        Or, if you don't know the timezone and accept potentially incorrect results
        during DST transitions, pass ``ignore_dst=True``.

        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic>`_
        for more information.
        """
        return self._shift(-1, *args, **kwargs)

    @no_type_check
    def _shift(
        self,
        sign: int,
        arg: Delta | _UNSET = _UNSET,
        /,
        *,
        ignore_dst: bool = False,
        **kwargs,
    ) -> PlainDateTime:
        if kwargs:
            if arg is _UNSET:
                return self._shift_kwargs(sign, ignore_dst, **kwargs)
            raise TypeError("Cannot mix positional and keyword arguments")

        elif arg is not _UNSET:
            return self._shift_kwargs(
                sign,
                ignore_dst,
                months=arg._date_part._months,
                days=arg._date_part._days,
                nanoseconds=arg._time_part._total_ns,
            )
        else:
            return self

    def _shift_kwargs(
        self,
        sign: int,
        ignore_dst: bool,
        *,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
    ) -> PlainDateTime:
        py_dt_with_new_date = self.replace_date(
            self.date()
            ._add_months(sign * (years * 12 + months))
            ._add_days(sign * (weeks * 7 + days)),
        )._py_dt

        tdelta = sign * TimeDelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
            nanoseconds=nanoseconds,
        )
        if tdelta and ignore_dst is not True:
            raise ImplicitlyIgnoringDST(ADJUST_LOCAL_DATETIME_MSG)

        delta_secs, nanos = divmod(
            tdelta._total_ns + self._nanos, 1_000_000_000
        )
        return self._from_py_unchecked(
            (py_dt_with_new_date + _timedelta(seconds=delta_secs)),
            nanos,
        )

    @classmethod
    def parse_strptime(cls, s: str, /, *, format: str) -> PlainDateTime:
        """Parse a plain datetime using the standard library ``strptime()`` method.

        Example
        -------
        >>> PlainDateTime.parse_strptime("2020-08-15", format="%d/%m/%Y_%H:%M")
        PlainDateTime(2020-08-15 00:00:00)

        Note
        ----
        This method defers to the standard library ``strptime()`` method,
        which may behave differently in different Python versions.
        It also only supports up to microsecond precision.

        Important
        ---------
        There may not be an offset in the format string.
        This means you CANNOT use the directives ``%z``, ``%Z``, or ``%:z``.
        Use ``OffsetDateTime`` to parse datetimes with an offset.
        """
        parsed = _datetime.strptime(s, format)
        if parsed.tzinfo is not None:
            raise ValueError(
                "Parsed datetime can't have an offset. "
                "Do not use %z, %Z, or %:z in the format string"
            )
        return cls._from_py_unchecked(
            parsed.replace(microsecond=0), parsed.microsecond * 1_000
        )

    def assume_utc(self) -> Instant:
        """Assume the datetime is in UTC, creating an ``Instant``.

        Example
        -------
        >>> PlainDateTime(2020, 8, 15, 23, 12).assume_utc()
        Instant(2020-08-15 23:12:00Z)
        """
        return Instant._from_py_unchecked(
            self._py_dt.replace(tzinfo=_UTC), self._nanos
        )

    def assume_fixed_offset(
        self, offset: int | TimeDelta, /
    ) -> OffsetDateTime:
        """Assume the datetime has the given offset, creating an ``OffsetDateTime``.

        Example
        -------
        >>> PlainDateTime(2020, 8, 15, 23, 12).assume_fixed_offset(+2)
        OffsetDateTime(2020-08-15 23:12:00+02:00)
        """
        return OffsetDateTime._from_py_unchecked(
            self._py_dt.replace(tzinfo=_load_offset(offset)), self._nanos
        )

    def assume_tz(
        self, tz: str, /, disambiguate: Disambiguate = "compatible"
    ) -> ZonedDateTime:
        """Assume the datetime is in the given timezone,
        creating a ``ZonedDateTime``.

        Note
        ----
        The local time may be ambiguous in the given timezone
        (e.g. during a DST transition). You can explicitly
        specify how to handle such a situation using the ``disambiguate`` argument.
        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#ambiguity-in-timezones>`_
        for more information.

        Example
        -------
        >>> d = PlainDateTime(2020, 8, 15, 23, 12)
        >>> d.assume_tz("Europe/Amsterdam", disambiguate="raise")
        ZonedDateTime(2020-08-15 23:12:00+02:00[Europe/Amsterdam])
        """
        return ZonedDateTime._from_py_unchecked(
            _resolve_ambiguity(
                self._py_dt.replace(tzinfo=(zone := _get_tz(tz))),
                zone,
                disambiguate,
            ),
            self._nanos,
        )

    def assume_system_tz(
        self, disambiguate: Disambiguate = "compatible"
    ) -> SystemDateTime:
        """Assume the datetime is in the system timezone,
        creating a ``SystemDateTime``.

        Note
        ----
        The local time may be ambiguous in the system timezone
        (e.g. during a DST transition). You can explicitly
        specify how to handle such a situation using the ``disambiguate`` argument.
        See `the documentation <https://whenever.rtfd.io/en/latest/overview.html#ambiguity-in-timezones>`_
        for more information.

        Example
        -------
        >>> d = PlainDateTime(2020, 8, 15, 23, 12)
        >>> # assuming system timezone is America/New_York
        >>> d.assume_system_tz(disambiguate="raise")
        SystemDateTime(2020-08-15 23:12:00-04:00)
        """
        return SystemDateTime._from_py_unchecked(
            _resolve_system_ambiguity(self._py_dt, disambiguate),
            self._nanos,
        )

    def round(
        self,
        unit: Literal[
            "day",
            "hour",
            "minute",
            "second",
            "millisecond",
            "microsecond",
            "nanosecond",
        ] = "second",
        increment: int = 1,
        mode: Literal[
            "ceil", "floor", "half_ceil", "half_floor", "half_even"
        ] = "half_even",
    ) -> PlainDateTime:
        """Round the datetime to the specified unit and increment.
        Different rounding modes are available.

        Examples
        --------
        >>> d = PlainDateTime(2020, 8, 15, 23, 24, 18)
        >>> d.round("day")
        PlainDateTime(2020-08-16 00:00:00)
        >>> d.round("minute", increment=15, mode="floor")
        PlainDateTime(2020-08-15 23:15:00)

        Note
        ----
        This method has similar behavior to the ``round()`` method of
        Temporal objects in JavaScript.
        """
        return self._round_unchecked(
            increment_to_ns(unit, increment, any_hour_ok=False),
            mode,
            86_400_000_000_000,
        )

    def _round_unchecked(
        self, increment_ns: int, mode: str, day_ns: int
    ) -> PlainDateTime:
        rounded_time, next_day = self.time()._round_unchecked(
            increment_ns, mode, day_ns
        )
        return self.date()._add_days(next_day).at(rounded_time)

    def __repr__(self) -> str:
        return f"PlainDateTime({str(self).replace('T', ' ')})"

    # a custom pickle implementation with a smaller payload
    def __reduce__(self) -> tuple[object, ...]:
        return (
            _unpkl_local,
            (pack("<HBBBBBi", *self._py_dt.timetuple()[:6], self._nanos),),
        )


# A separate unpickling function allows us to make backwards-compatible changes
# to the pickling format in the future
@no_type_check
def _unpkl_local(data: bytes) -> PlainDateTime:
    *args, nanos = unpack("<HBBBBBi", data)
    return PlainDateTime._from_py_unchecked(_datetime(*args), nanos)


class RepeatedTime(ValueError):
    """A datetime is repeated in a timezone, e.g. because of DST"""

    @classmethod
    def _for_tz(cls, d: _datetime, tz: ZoneInfo) -> RepeatedTime:
        return cls(
            f"{d.replace(tzinfo=None)} is repeated " f"in timezone {tz.key!r}"
        )

    @classmethod
    def _for_system_tz(cls, d: _datetime) -> RepeatedTime:
        return cls(
            f"{d.replace(tzinfo=None)} is repeated in the system timezone"
        )


class SkippedTime(ValueError):
    """A datetime is skipped in a timezone, e.g. because of DST"""

    @classmethod
    def _for_tz(cls, d: _datetime, tz: ZoneInfo) -> SkippedTime:
        return cls(
            f"{d.replace(tzinfo=None)} is skipped " f"in timezone {tz.key!r}"
        )

    @classmethod
    def _for_system_tz(cls, d: _datetime) -> SkippedTime:
        return cls(
            f"{d.replace(tzinfo=None)} is skipped in the system timezone"
        )


class InvalidOffsetError(ValueError):
    """A string has an invalid offset for the given zone"""


class ImplicitlyIgnoringDST(TypeError):
    """A calculation was performed that implicitly ignored DST"""


class TimeZoneNotFoundError(ValueError):
    """A timezone with the given ID was not found"""

    @classmethod
    def for_key(cls, key: str) -> TimeZoneNotFoundError:
        return cls(f"No time zone found for key: {key!r}")


_IGNORE_DST_SUGGESTION = (
    "To perform DST-safe operations, convert to a ZonedDateTime first. "
    "Or, if you don't know the timezone and accept potentially incorrect results "
    "during DST transitions, pass `ignore_dst=True`. For more information, see "
    "whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic"
)


SHIFT_LOCAL_MSG = (
    "Adding or subtracting a (date)time delta to a datetime without timezone "
    "implicitly ignores DST transitions and other timezone "
    "changes. Use the `add` or `subtract` method instead."
)

DIFF_OPERATOR_LOCAL_MSG = (
    "The difference between two datetimes without timezone implicitly ignores "
    "DST transitions and other timezone changes. "
    "Use the `difference` method instead."
)

DIFF_LOCAL_MSG = (
    "The difference between two datetimes without timezone implicitly ignores "
    "DST transitions and other timezone changes. " + _IGNORE_DST_SUGGESTION
)


TIMESTAMP_DST_MSG = (
    "Converting from a timestamp with a fixed offset implicitly ignores DST "
    "and other timezone changes. To perform a DST-safe conversion, use "
    "ZonedDateTime.from_timestamp() instead. "
    "Or, if you don't know the timezone and accept potentially incorrect results "
    "during DST transitions, pass `ignore_dst=True`. For more information, see "
    "whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic"
)


OFFSET_NOW_DST_MSG = (
    "Getting the current time with a fixed offset implicitly ignores DST "
    "and other timezone changes. Instead, use `Instant.now()` or "
    "`ZonedDateTime.now(<tz name>)` if you know the timezone. "
    "Or, if you want to ignore DST and accept potentially incorrect offsets, "
    "pass `ignore_dst=True` to this method. For more information, see "
    "whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic"
)

OFFSET_ROUNDING_DST_MSG = (
    "Rounding a fixed offset datetime may (in rare cases) result in a datetime "
    "for which the offset is incorrect. This is because the offset may change "
    "during DST transitions. To perform DST-safe rounding, convert to a "
    "ZonedDateTime first. Or, if you don't know the timezone and accept "
    "potentially incorrect results during DST transitions, pass `ignore_dst=True`. "
    "For more information, see whenever.rtfd.io/en/latest/overview.html#dst-safe-arithmetic"
)

ADJUST_OFFSET_DATETIME_MSG = (
    "Adjusting a fixed offset datetime implicitly ignores DST and other timezone changes. "
    + _IGNORE_DST_SUGGESTION
)

ADJUST_LOCAL_DATETIME_MSG = (
    "Adjusting a datetime without timezone by time units (e.g. hours and minutess) ignores "
    "DST and other timezone changes. " + _IGNORE_DST_SUGGESTION
)

CANNOT_ROUND_DAY_MSG = (
    "Cannot round to day, because days do not have a fixed length. "
    "Due to daylight saving time, some days have 23 or 25 hours."
    "If you wish to round to exaxtly 24 hours, use `round('hour', increment=24)`."
)

ZONEINFO_NO_KEY_MSG = """\
The 'key' attribute of the datetime's ZoneInfo object is None.

A ZonedDateTime requires a full IANA timezone ID (e.g., 'Europe/Paris') \
to be created. This error typically means the ZoneInfo object was loaded from \
a file without its 'key' parameter being specified.
To fix this, provide the correct IANA ID when you create the ZoneInfo object. \
If the ID is truly unknown, you can use OffsetDateTime.from_py_datetime() as \
an alternative, but be aware this is a lossy conversion that only preserves \
the current UTC offset and discards future daylight saving rules. \
Please note that a timezone abbreviation like 'CEST' from tzinfo.tzname() \
is not a valid IANA ID and cannot be used here."""


def _resolve_ambiguity(
    dt: _datetime, zone: ZoneInfo, disambiguate: Disambiguate | _timedelta
) -> _datetime:
    if isinstance(disambiguate, _timedelta):
        return _resolve_ambiguity_using_prev_offset(dt, disambiguate)
    dt = dt.replace(fold=_as_fold(disambiguate))
    dt_utc = dt.astimezone(_UTC)
    # Non-existent times: they don't survive a UTC roundtrip
    if dt_utc.astimezone(zone) != dt:
        if disambiguate == "raise":
            raise SkippedTime._for_tz(dt, zone)
        elif disambiguate != "compatible":  # i.e. "earlier" or "later"
            # In gaps, the relationship between
            # fold and earlier/later is reversed
            dt = dt.replace(fold=not dt.fold)
        # Perform the normalisation, shifting away from non-existent times
        dt = dt.astimezone(_UTC).astimezone(zone)
    # Ambiguous times: they're never equal to other timezones
    elif disambiguate == "raise" and dt_utc != dt:
        raise RepeatedTime._for_tz(dt, zone)
    return dt


def _resolve_ambiguity_using_prev_offset(
    dt: _datetime,
    prev_offset: _timedelta,
) -> _datetime:
    if prev_offset == dt.utcoffset():
        pass
    elif prev_offset == dt.replace(fold=not dt.fold).utcoffset():
        dt = dt.replace(fold=not dt.fold)
    else:
        # No offset match. Setting fold=0 adopts the 'compatible' strategy
        dt = dt.replace(fold=0)

    # This roundtrip ensures skipped times are shifted
    return dt.astimezone(_UTC).astimezone(dt.tzinfo)


# Whether the fold of a system time needs to be flipped in a gap
# was changed (fixed) in Python 3.12. See cpython/issues/83861
_requires_flip: Callable[[Disambiguate], bool] = (
    "compatible".__ne__ if _PY312 else "compatible".__eq__
)


# FUTURE: document that this isn't threadsafe (system tz may change)
def _resolve_system_ambiguity(
    dt: _datetime, disambiguate: Disambiguate | _timedelta
) -> _datetime:
    assert dt.tzinfo is None
    if isinstance(disambiguate, _timedelta):
        return _resolve_system_ambiguity_using_prev_offset(dt, disambiguate)
    dt = dt.replace(fold=_as_fold(disambiguate))
    norm = dt.astimezone(_UTC).astimezone()  # going through UTC resolves gaps
    # Non-existent times: they don't survive a UTC roundtrip
    if norm.replace(tzinfo=None) != dt:
        if disambiguate == "raise":
            raise SkippedTime._for_system_tz(dt)
        elif _requires_flip(disambiguate):
            dt = dt.replace(fold=not dt.fold)
        # perform the normalisation, shifting away from non-existent times
        norm = dt.astimezone(_UTC).astimezone()
    # Ambiguous times: their UTC depends on the fold
    elif disambiguate == "raise" and norm != dt.replace(fold=1).astimezone(
        _UTC
    ):
        raise RepeatedTime._for_system_tz(dt)
    return norm


def _resolve_system_ambiguity_using_prev_offset(
    dt: _datetime, prev_offset: _timedelta
) -> _datetime:
    if dt.astimezone(_UTC).astimezone().utcoffset() == prev_offset:
        pass
    elif (
        dt.replace(fold=not dt.fold).astimezone(_UTC).astimezone().utcoffset()
        == prev_offset
    ):
        dt = dt.replace(fold=not dt.fold)
    else:  # rare: no offset match.
        # We account for this CPython bug: cpython/issues/83861
        if (
            not _PY312
            # i.e. it's in a gap
            and dt.astimezone(_UTC).astimezone().replace(tzinfo=None) != dt
        ):  # pragma: no cover
            dt = dt.replace(fold=not dt.fold)
        else:
            dt = dt.replace(fold=0)
    return dt.astimezone(_UTC).astimezone()


def _load_offset(offset: int | TimeDelta, /) -> _timezone:
    if isinstance(offset, int):
        return _timezone(_timedelta(hours=offset))
    elif isinstance(offset, TimeDelta):
        if offset._total_ns % 1_000_000_000:
            raise ValueError("Offset must be a whole number of seconds")
        return _timezone(offset.py_timedelta())
    else:
        raise TypeError(
            "offset must be an int or TimeDelta, e.g. `hours(2.5)`"
        )


# Helpers that pre-compute/lookup as much as possible
_no_tzinfo_fold_or_ms = {"tzinfo", "fold", "microsecond"}.isdisjoint
_fromtimestamp = _datetime.fromtimestamp


def _parse_err(s: str) -> NoReturn:
    raise ValueError(f"Invalid format: {s!r}") from None


def _parse_nanos(s: str) -> _Nanos:
    if len(s) > 9 or not s.isdigit() or not s.isascii():
        raise ValueError("Invalid decimals")
    return int(s.ljust(9, "0"))


def _split_nextchar(
    s: str, chars: str, start: int = 0, end: int = -1
) -> tuple[str, str | None, str]:
    for c in chars:
        if (idx := s.find(c, start, end)) != -1:
            return (s[:idx], c, s[idx + 1 :])
    return (s, None, "")


_is_sep = " Tt".__contains__


def _offset_from_iso(s: str) -> _timedelta:
    if len(s) == 5 and s[2] == ":" and s[3] < "6":  # most common: HH:MM
        return _timedelta(hours=int(s[:2]), minutes=int(s[3:]))
    elif len(s) == 4 and s[2] < "6":  # HHMM
        return _timedelta(hours=int(s[:2]), minutes=int(s[2:]))
    elif len(s) == 2:  # HH
        return _timedelta(hours=int(s))
    elif (
        len(s) == 8
        and s[2] == ":"
        and s[5] == ":"
        and s[3] < "6"
        and s[6] < "6"
    ):  # HH:MM:SS
        return _timedelta(
            hours=int(s[:2]), minutes=int(s[3:5]), seconds=int(s[6:])
        )
    elif len(s) == 6:  # HHMMSS
        return _timedelta(
            hours=int(s[:2]), minutes=int(s[2:4]), seconds=int(s[4:])
        )
    else:
        raise ValueError("Invalid offset format")


def _datetime_from_iso(s: str) -> tuple[_datetime, _Nanos]:
    if len(s) < 11 or "W" in s or not s.isascii():
        _parse_err(s)

    # OPTIMIZE: the happy path can be faster
    try:
        if _is_sep(s[10]):  # date in extended format
            rest, date = s[11:], _date.fromisoformat(s[:10])
        elif _is_sep(s[8]):  # date in basic format
            rest, date = s[9:], __date_from_iso_basic(s[:8])
        else:
            _parse_err(s)
        time, nanos = _time_from_iso(rest)
    except ValueError:
        _parse_err(s)

    return _datetime.combine(date, time), nanos


def _offset_dt_from_iso(s: str) -> tuple[_datetime, _Nanos]:
    if len(s) < 11 or "W" in s[:11] or not s.isascii():
        _parse_err(s)

    try:
        if _is_sep(s[10]):  # date in extended format
            rest, date = s[11:], _date.fromisoformat(s[:10])
        elif _is_sep(s[8]):  # date in basic format
            rest, date = s[9:], __date_from_iso_basic(s[:8])
        else:
            _parse_err(s)
        time, nanos, offset, _ = _time_offset_tz_from_iso(rest)
        if offset is None:
            raise ValueError("Missing offset")
        elif offset == "Z":
            tzinfo = _UTC
        else:
            assert isinstance(offset, _timedelta)
            tzinfo = _timezone(offset)

        return (
            _check_utc_bounds(_datetime.combine(date, time, tzinfo)),
            nanos,
        )
    except ValueError:
        _parse_err(s)


def _zdt_from_iso(s: str) -> tuple[_datetime, _Nanos]:
    if len(s) < 11 or "W" in s[:11] or not s.isascii():
        _parse_err(s)

    try:
        if _is_sep(s[10]):  # date in extended format
            rest, date = s[11:], _date.fromisoformat(s[:10])
        elif _is_sep(s[8]):  # date in basic format
            rest, date = s[9:], __date_from_iso_basic(s[:8])
        else:
            _parse_err(s)
        time, nanos, offset, tzid = _time_offset_tz_from_iso(rest)
    except ValueError:
        _parse_err(s)

    if tzid is None:
        _parse_err(s)

    tz = _get_tz(tzid)

    if offset is None:
        dt = _resolve_ambiguity(
            _datetime.combine(date, time, tz),
            tz,
            "compatible",
        )
    elif offset == "Z":
        dt = _datetime.combine(date, time, _UTC).astimezone(tz)
    else:
        assert isinstance(offset, _timedelta)
        try:
            _timezone(offset)  # check if offset is <24 hours
        except ValueError:
            _parse_err(s)
        dt = _datetime.combine(date, time, tz)
        # detect a gap
        dt_norm = dt.astimezone(_UTC).astimezone(tz)
        if dt_norm != dt:
            raise InvalidOffsetError()
        elif dt.utcoffset() != offset:
            dt = dt.replace(fold=1)
            if dt.utcoffset() != offset:
                raise InvalidOffsetError()

    return (dt, nanos)


def _time_from_iso(s_orig: str) -> tuple[_time, _Nanos]:
    s, sep, nanos_raw = _split_nextchar(s_orig, ".,", 6, 9)

    try:
        return (
            __time_from_iso_nofrac(s),
            _parse_nanos(nanos_raw) if sep else 0,
        )
    except ValueError:
        _parse_err(s_orig)


# Parse the time, UTC offset, and timezone ID
def _time_offset_tz_from_iso(
    s: str,
) -> tuple[_time, _Nanos, _timedelta | Literal["Z"] | None, _BenignKey | None]:
    # ditch the bracketted timezone (if present)
    if s.endswith("]"):
        # NOTE: sorry for the unicode escape sequences. Literal brackets
        # break my LSP's indentation detection. \x5b is open bracket ']'
        s, tz_raw = s[:-1].rsplit("\x5b", 1)
        tz = _validate_key(tz_raw)
    else:
        tz = None

    # determine the offset
    offset: Literal["Z"] | _timedelta | None
    if s.endswith(("Z", "z")):
        s_time = s[:-1]
        offset = "Z"
    else:
        s_time, sign, s_offset = _split_nextchar(s, "+-")
        if sign is None:
            offset = None
        else:
            offset = _offset_from_iso(s_offset)
            if sign == "-":
                offset = -offset

    time, nanos = _time_from_iso(s_time)
    return (time, nanos, offset, tz)


def _yearmonth_from_iso(s: str) -> _date:
    if not s.isascii():
        _parse_err(s)
    try:
        if len(s) == 7 and s[4] == "-":
            year, month = int(s[:4]), int(s[5:])
        elif len(s) == 6:
            year, month = int(s[:4]), int(s[4:])
        else:
            _parse_err(s)
        return _date(year, month, 1)
    except ValueError:
        _parse_err(s)


def _monthday_from_iso(s: str) -> _date:
    if not (s.startswith("--") and s.isascii()):
        _parse_err(s)
    try:
        if len(s) == 7 and s[4] == "-":
            month, day = int(s[2:4]), int(s[5:])
        elif len(s) == 6:
            month, day = int(s[2:4]), int(s[4:])
        else:
            _parse_err(s)
        return _date(_DUMMY_LEAP_YEAR, month, day)
    except ValueError:
        _parse_err(s)


# The ISO parsing functions were improved in Python 3.11,
# so we use them if available.
if _PY311:

    __date_from_iso_basic = _date.fromisoformat

    def __time_from_iso_nofrac(s: str) -> _time:
        # Compensate for a bug in CPython where times like "12:34:56:78" are
        # accepted as valid times. This is only fixed in Python 3.14+
        if s.count(":") > 2:
            raise ValueError()
        if all(map("0123456789:".__contains__, s)):
            return _time.fromisoformat(s)
        raise ValueError()

    def _date_from_iso(s: str) -> _date:
        # prevent isoformat from parsing stuff we don't want it to
        if "W" in s or not s.isascii():
            _parse_err(s)
        try:
            return _date.fromisoformat(s)
        except ValueError:
            _parse_err(s)

else:  # pragma: no cover

    def __date_from_iso_basic(s: str, /) -> _date:
        return _date.fromisoformat(s[:4] + "-" + s[4:6] + "-" + s[6:8])

    def __time_from_iso_nofrac(s: str) -> _time:
        # Compensate for the fact that Python's isoformat
        # doesn't support basic ISO 8601 formats
        if len(s) == 4:
            s = s[:2] + ":" + s[2:]
        elif len(s) == 6:
            s = s[:2] + ":" + s[2:4] + ":" + s[4:]
        if all(map("0123456789:".__contains__, s)):
            return _time.fromisoformat(s)
        raise ValueError()

    def _date_from_iso(s: str) -> _date:
        if not s.isascii():
            _parse_err(s)
        try:
            if len(s) == 8:
                return __date_from_iso_basic(s)
            return _date.fromisoformat(s)
        except ValueError:
            _parse_err(s)


_RFC2822_WEEKDAY_TO_ISO = {
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
    "sun": 7,
}

_WEEKDAY_TO_RFC2822 = [s.title() for s in _RFC2822_WEEKDAY_TO_ISO]

_RFC2822_MONTH_NAMES = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

_MONTH_TO_RFC2822 = [s.title() for s in _RFC2822_MONTH_NAMES]
_MONTH_TO_RFC2822.insert(0, "")  # 1-indexed

_RFC2822_ZONES = {
    "EST": -5,
    "EDT": -4,
    "CST": -6,
    "CDT": -5,
    "MST": -7,
    "MDT": -6,
    "PST": -8,
    "PDT": -7,
    "UT": 0,
    "GMT": 0,
}


def _parse_rfc2822(s: str) -> _datetime:
    # Technically, only tab, space and CRLF are allowed in RFC2822,
    # but we allow any ASCII whitespace
    if not s.isascii():
        _parse_err(s)

    # Parse the weekday
    try:
        first, second, *parts = s.split()
        if first.isdigit():
            iso_weekday = None
            parts = [first, second, *parts]
        else:
            # Case: Mon, 23 Jan
            if len(first) == 4 and first[3] == ",":
                weekday_raw = first[:3]
                parts = [second, *parts]
            # Case: Mon , 23 Jan
            elif len(first) == 3 and second == ",":
                weekday_raw = first
            # Case: Mon ,23 Jan
            elif len(first) == 3 and second.startswith(","):
                weekday_raw = first
                parts = [second[1:], *parts]
            # Case: Mon,23 Jan
            elif len(first) > 4 and first[3] == ",":
                weekday_raw = first[:3]
                parts = [first[4:], second, *parts]
            else:
                _parse_err(s)

            iso_weekday = _RFC2822_WEEKDAY_TO_ISO[weekday_raw.lower()]
    except (ValueError, KeyError):
        _parse_err(s)

    # Parse the date
    try:
        day_raw, month_raw, year_raw, *parts = parts
        if len(day_raw) > 2:
            _parse_err(s)
        day = int(day_raw)
        month = _RFC2822_MONTH_NAMES[month_raw.lower()]
        if len(year_raw) == 4:
            year = int(year_raw)
        elif len(year_raw) == 2:
            year = int(year_raw)
            if year < 50:
                year += 2000
            else:
                year += 1900
        elif len(year_raw) == 3:
            year = int(year_raw) + 1900
        else:
            _parse_err(s)
        date = _date(year, month, day)
    except (ValueError, KeyError):
        _parse_err(s)

    if iso_weekday and iso_weekday != date.isoweekday():
        _parse_err(s)

    # Parse the time
    try:
        # time components may be separated by whitespace
        *time_parts, offset_raw = parts
        time_raw = "".join(time_parts)
        if len(time_raw) == 5 and time_raw[2] == ":":
            time = _time(int(time_raw[:2]), int(time_raw[3:]))
        elif len(time_raw) == 8 and time_raw[2] == ":" and time_raw[5] == ":":
            time = _time(
                int(time_raw[:2]), int(time_raw[3:5]), int(time_raw[6:])
            )
        else:
            _parse_err(s)
    except ValueError:
        _parse_err(s)

    # Parse the offset
    try:
        if offset_raw.startswith(("+", "-")) and len(offset_raw) == 5:
            sign = 1 if offset_raw[0] == "+" else -1
            offset = (
                _timedelta(
                    hours=int(offset_raw[1:3]), minutes=int(offset_raw[3:5])
                )
                * sign
            )
        elif offset_raw.isalpha():
            # According to the spec, unknown timezones should
            # just be treated at -0000 (UTC with unknown offset)
            offset = _timedelta(
                hours=_RFC2822_ZONES.get(offset_raw.upper(), 0)
            )
        else:
            _parse_err(s)
        tzinfo = _timezone(offset)
    except ValueError:
        _parse_err(s)

    return _check_utc_bounds(_datetime.combine(date, time, tzinfo=tzinfo))


def _check_utc_bounds(dt: _datetime) -> _datetime:
    try:
        dt.astimezone(_UTC)
    except (OverflowError, ValueError):
        raise ValueError("Instant out of range")
    return dt


def _check_invalid_replace_kwargs(kwargs: Any) -> None:
    if not _no_tzinfo_fold_or_ms(kwargs):
        raise TypeError(
            "tzinfo, fold, or microsecond are not allowed arguments"
        )


def _pop_nanos_kwarg(kwargs: Any, default: int) -> int:
    nanos = kwargs.pop("nanosecond", default)
    if type(nanos) is not int:
        raise TypeError("nanosecond must be an int")
    elif not 0 <= nanos < 1_000_000_000:
        raise ValueError("Invalid nanosecond value")
    return nanos


def _isleap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


# 1-indexed days per month
_monthdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _days_in_month(year: int, month: int) -> int:
    return _monthdays[month] + (month == 2 and _isleap(year))


# Use this to strip any incoming datetime classes down to instances
# of the datetime.datetime class exactly.
def _strip_subclasses(dt: _datetime) -> _datetime:
    if type(dt) is _datetime:
        return dt
    else:
        return _datetime(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            dt.tzinfo,
            fold=dt.fold,
        )


Instant.MIN = Instant._from_py_unchecked(
    _datetime.min.replace(tzinfo=_UTC),
    0,
)
Instant.MAX = Instant._from_py_unchecked(
    _datetime.max.replace(tzinfo=_UTC, microsecond=0),
    999_999_999,
)
PlainDateTime.MIN = PlainDateTime._from_py_unchecked(_datetime.min, 0)
PlainDateTime.MAX = PlainDateTime._from_py_unchecked(
    _datetime.max.replace(microsecond=0), 999_999_999
)
Disambiguate = Literal["compatible", "earlier", "later", "raise"]
Fold = Literal[0, 1]
_disambiguate_to_fold: Mapping[str, Fold] = {
    "compatible": 0,
    "earlier": 0,
    "later": 1,
    "raise": 0,
}


def _adjust_fold_to_offset(dt: _datetime, offset: _timedelta) -> _datetime:
    if offset != dt.utcoffset():  # offset/zone mismatch: try other fold
        dt = dt.replace(fold=1)
        if dt.utcoffset() != offset:  # pragma: no cover (#39)
            raise InvalidOffsetError()
    return dt


def _as_fold(s: str) -> Fold:
    try:
        return _disambiguate_to_fold[s]
    except KeyError:
        raise ValueError(f"Invalid disambiguate setting: {s!r}")


def years(i: int, /) -> DateDelta:
    """Create a :class:`~DateDelta` with the given number of years.
    ``years(1) == DateDelta(years=1)``
    """
    return DateDelta(years=i)


def months(i: int, /) -> DateDelta:
    """Create a :class:`~DateDelta` with the given number of months.
    ``months(1) == DateDelta(months=1)``
    """
    return DateDelta(months=i)


def weeks(i: int, /) -> DateDelta:
    """Create a :class:`~DateDelta` with the given number of weeks.
    ``weeks(1) == DateDelta(weeks=1)``
    """
    return DateDelta(weeks=i)


def days(i: int, /) -> DateDelta:
    """Create a :class:`~DateDelta` with the given number of days.
    ``days(1) == DateDelta(days=1)``
    """
    return DateDelta(days=i)


def hours(i: float, /) -> TimeDelta:
    """Create a :class:`~TimeDelta` with the given number of hours.
    ``hours(1) == TimeDelta(hours=1)``
    """
    return TimeDelta(hours=i)


def minutes(i: float, /) -> TimeDelta:
    """Create a :class:`TimeDelta` with the given number of minutes.
    ``minutes(1) == TimeDelta(minutes=1)``
    """
    return TimeDelta(minutes=i)


def seconds(i: float, /) -> TimeDelta:
    """Create a :class:`TimeDelta` with the given number of seconds.
    ``seconds(1) == TimeDelta(seconds=1)``
    """
    return TimeDelta(seconds=i)


def milliseconds(i: int, /) -> TimeDelta:
    """Create a :class:`TimeDelta` with the given number of milliseconds.
    ``milliseconds(1) == TimeDelta(milliseconds=1)``
    """
    return TimeDelta(milliseconds=i)


def microseconds(i: float, /) -> TimeDelta:
    """Create a :class:`TimeDelta` with the given number of microseconds.
    ``microseconds(1) == TimeDelta(microseconds=1)``
    """
    return TimeDelta(microseconds=i)


def nanoseconds(i: int, /) -> TimeDelta:
    """Create a :class:`TimeDelta` with the given number of nanoseconds.
    ``nanoseconds(1) == TimeDelta(nanoseconds=1)``
    """
    return TimeDelta(nanoseconds=i)


# We expose the public members in the root of the module.
# For clarity, we remove the "_pywhenever" part from the names,
# since this is an implementation detail.
for name in __all__ + "_LocalTime _ExactTime _ExactAndLocalTime".split():
    member = locals()[name]
    if getattr(member, "__module__", None) == __name__:  # pragma: no branch
        member.__module__ = "whenever"

# clear up loop variables so they don't leak into the namespace
del name
del member

for _unpkl in (
    _unpkl_date,
    _unpkl_ym,
    _unpkl_md,
    _unpkl_time,
    _unpkl_tdelta,
    _unpkl_dtdelta,
    _unpkl_ddelta,
    _unpkl_utc,
    _unpkl_offset,
    _unpkl_zoned,
    _unpkl_system,
    _unpkl_local,
):
    _unpkl.__module__ = "whenever"


# disable further subclassing
final(_ImmutableBase)
final(_ExactTime)
final(_LocalTime)
final(_ExactAndLocalTime)
final(_BasicConversions)


def _patch_time_frozen(inst: Instant) -> None:
    global time_ns

    def time_ns() -> int:
        return inst.timestamp_nanos()


def _patch_time_keep_ticking(inst: Instant) -> None:
    global time_ns

    _patched_at = time_ns()
    _time_ns = time_ns

    def time_ns() -> int:
        return inst.timestamp_nanos() + _time_ns() - _patched_at


def _unpatch_time() -> None:
    global time_ns

    from time import time_ns


_TZPATH: tuple[str, ...] = ()

# Our cache for loaded tz files. The design is based off zoneinfo.
# Why roll our own? To ensure it works independently of zoneinfo,
# and thus works identically to the Rust extension.
_TZCACHE_LRU_SIZE = 8
_tzcache_lru: OrderedDict[str, ZoneInfo] = OrderedDict()
_tzcache_lookup: WeakValueDictionary[str, ZoneInfo] = WeakValueDictionary()


def _set_tzpath(to: tuple[str, ...]) -> None:
    global _TZPATH
    _TZPATH = to


def _clear_tz_cache() -> None:
    _tzcache_lru.clear()
    _tzcache_lookup.clear()


def _clear_tz_cache_by_keys(keys: tuple[str, ...]) -> None:
    for k in keys:
        _tzcache_lookup.pop(k, None)
        _tzcache_lru.pop(k, None)


def _get_tz(key: str) -> ZoneInfo:
    try:
        zinfo = _tzcache_lookup[key]
    except KeyError:
        zinfo = _tzcache_lookup[key] = _load_tz(_validate_key(key))
    # Update the LRU
    _tzcache_lru[key] = _tzcache_lru.pop(key, zinfo)
    if len(_tzcache_lru) > _TZCACHE_LRU_SIZE:
        _tzcache_lru.popitem(last=False)
    return zinfo


def _validate_key(key: str) -> _BenignKey:
    """Checks for invalid characters and path traversal in the key."""
    if (
        key.isascii()
        # There's no standard limit on IANA tz IDs, but we have to draw
        # the line somewhere to prevent abuse.
        and 0 < len(key) < 100
        and all(b.isalnum() or b in "-_+/." for b in key)
        # specific sequences not allowed
        and ".." not in key
        and "//" not in key
        and "/./" not in key
        # specic restrictions on the first and list characters
        and key[0] not in "-+/"
        and key[-1] != "/"
    ):
        return _BenignKey(key)
    else:
        raise TimeZoneNotFoundError.for_key(key)


# Alias for a TZ key that has been confirmed not to be a path traversal
# or contain other "bad" characters.
_BenignKey = NewType("_BenignKey", str)


def _try_tzif_from_path(key: _BenignKey) -> bytes | None:
    for search_path in _TZPATH:
        target = os.path.join(search_path, key)
        if os.path.isfile(target):
            with open(target, "rb") as f:
                return f.read()
    return None


def _tzif_from_tzdata(key: _BenignKey) -> bytes:
    try:
        tzdata_path = __import__("tzdata.zoneinfo").zoneinfo.__path__[0]
        # We check before we read, since the resulting exceptions vary
        # on different platforms
        if os.path.isfile(
            relpath := os.path.join(tzdata_path, *key.split("/"))
        ):
            with open(relpath, "rb") as f:
                return f.read()
        else:
            raise FileNotFoundError()
    # Several exceptions amount to "can't find the key"
    except (
        ImportError,
        FileNotFoundError,
        UnicodeEncodeError,
    ):
        raise TimeZoneNotFoundError.for_key(key)


def _load_tz(key: _BenignKey) -> ZoneInfo:
    from zoneinfo import ZoneInfo

    # Reminder: we load manually from files to ensure we operate
    # independently of zoneinfo's own caching mechanism
    tzif = _try_tzif_from_path(key) or _tzif_from_tzdata(key)
    if not tzif.startswith(b"TZif"):
        # We've found a file, but doesn't look like a TZif file.
        # Stop here instead of getting a cryptic error later.
        raise TimeZoneNotFoundError.for_key(key)

    return ZoneInfo.from_file(BytesIO(tzif), key)
