import enum
from abc import ABC
from contextlib import _GeneratorContextManager
from datetime import (
    date as _date,
    datetime as _datetime,
    time as _time,
    timedelta as _timedelta,
)
from os import PathLike
from typing import (
    ClassVar,
    Final,
    Iterable,
    Literal,
    TypeAlias,
    final,
    overload,
    type_check_only,
)

from typing_extensions import Self, override

__all__ = [
    "Date",
    "Time",
    "Instant",
    "OffsetDateTime",
    "ZonedDateTime",
    "SystemDateTime",
    "PlainDateTime",
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
    "microseconds",
    "SkippedTime",
    "RepeatedTime",
    "InvalidOffsetError",
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
]

_EXTENSION_LOADED: bool
__version__: str

@type_check_only
class _CommonISOMixin:
    @classmethod
    def parse_common_iso(cls, s: str, /) -> Self: ...
    def format_common_iso(self) -> str: ...

@type_check_only
class _OrderMixin:
    MIN: ClassVar[Self]
    MAX: ClassVar[Self]
    def __lt__(self, other: Self, /) -> bool: ...
    def __le__(self, other: Self, /) -> bool: ...
    def __gt__(self, other: Self, /) -> bool: ...
    def __ge__(self, other: Self, /) -> bool: ...

@type_check_only
class _DateOrTimeMixin(_CommonISOMixin, _OrderMixin): ...

@final
class Date(_DateOrTimeMixin):
    def __init__(self, year: int, month: int, day: int) -> None: ...
    @staticmethod
    def today_in_system_tz() -> Date: ...
    @property
    def year(self) -> int: ...
    @property
    def month(self) -> int: ...
    @property
    def day(self) -> int: ...
    def year_month(self) -> YearMonth: ...
    def month_day(self) -> MonthDay: ...
    def day_of_week(self) -> Weekday: ...
    def at(self, t: Time, /) -> PlainDateTime: ...
    def py_date(self) -> _date: ...
    @classmethod
    def from_py_date(cls, d: _date, /) -> Self: ...
    def replace(
        self, *, year: int = ..., month: int = ..., day: int = ...
    ) -> Self: ...
    @overload
    def add(
        self, *, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0
    ) -> Self: ...
    @overload
    def add(self, delta: DateDelta, /) -> Self: ...
    @overload
    def subtract(
        self, *, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0
    ) -> Self: ...
    @overload
    def subtract(self, delta: DateDelta, /) -> Self: ...
    def days_since(self, other: Self, /) -> int: ...
    def days_until(self, other: Self, /) -> int: ...
    def __add__(self, p: DateDelta, /) -> Self: ...
    @overload
    def __sub__(self, d: DateDelta, /) -> Self: ...
    @overload
    def __sub__(self, d: Self, /) -> DateDelta: ...

@final
class YearMonth(_DateOrTimeMixin):
    def __init__(self, year: int, month: int) -> None: ...
    @property
    def year(self) -> int: ...
    @property
    def month(self) -> int: ...
    def replace(self, /, *, year: int = ..., month: int = ...) -> Self: ...
    def on_day(self, day: int, /) -> Date: ...

@final
class MonthDay(_DateOrTimeMixin):
    def __init__(self, month: int, day: int) -> None: ...
    @property
    def month(self) -> int: ...
    @property
    def day(self) -> int: ...
    def replace(self, *, month: int = ..., day: int = ...) -> Self: ...
    def in_year(self, year: int, /) -> Date: ...
    def is_leap(self) -> bool: ...

@final
class Time(_DateOrTimeMixin):
    def __init__(
        self,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        *,
        nanosecond: int = 0,
    ) -> None: ...
    MIDNIGHT: ClassVar[Self]
    NOON: ClassVar[Self]
    @property
    def hour(self) -> int: ...
    @property
    def minute(self) -> int: ...
    @property
    def second(self) -> int: ...
    @property
    def nanosecond(self) -> int: ...
    def on(self, d: Date, /) -> PlainDateTime: ...
    def py_time(self) -> _time: ...
    @classmethod
    def from_py_time(cls, t: _time, /) -> Self: ...
    def replace(
        self,
        *,
        hour: int = ...,
        minute: int = ...,
        second: int = ...,
        nanosecond: int = ...,
    ) -> Self: ...
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
    ) -> Self: ...

@type_check_only
class _DeltaMixin(_CommonISOMixin):
    ZERO: ClassVar[Self]
    def __bool__(self) -> bool: ...
    def __neg__(self) -> Self: ...
    def __pos__(self) -> Self: ...
    def __abs__(self) -> Self: ...
    def __mul__(self, other: int, /) -> Self: ...
    def __rmul__(self, other: int, /) -> Self: ...

@final
class TimeDelta(_DeltaMixin, _OrderMixin):
    def __init__(
        self,
        *,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
    ) -> None: ...
    def in_days_of_24h(self) -> float: ...
    def in_hours(self) -> float: ...
    def in_minutes(self) -> float: ...
    def in_seconds(self) -> float: ...
    def in_milliseconds(self) -> float: ...
    def in_microseconds(self) -> float: ...
    def in_nanoseconds(self) -> int: ...
    def in_hrs_mins_secs_nanos(self) -> tuple[int, int, int, int]: ...
    def py_timedelta(self) -> _timedelta: ...
    @classmethod
    def from_py_timedelta(cls, td: _timedelta, /) -> Self: ...
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
    ) -> Self: ...
    def __add__(self, other: Self, /) -> Self: ...
    def __sub__(self, other: Self, /) -> Self: ...
    @override
    def __mul__(self, other: float, /) -> Self: ...
    @override
    def __rmul__(self, other: float, /) -> Self: ...
    @overload
    def __truediv__(self, other: float, /) -> Self: ...
    @overload
    def __truediv__(self, other: Self, /) -> float: ...
    def __floordiv__(self, other: Self, /) -> int: ...
    def __mod__(self, other: Self, /) -> Self: ...

@final
class DateDelta(_DeltaMixin):
    def __init__(
        self, *, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0
    ) -> None: ...
    def in_months_days(self) -> tuple[int, int]: ...
    def in_years_months_days(self) -> tuple[int, int, int]: ...
    @overload
    def __add__(self, other: Self, /) -> Self: ...
    @overload
    def __add__(self, other: TimeDelta, /) -> DateTimeDelta: ...
    def __radd__(self, other: TimeDelta, /) -> DateTimeDelta: ...
    @overload
    def __sub__(self, other: Self, /) -> Self: ...
    @overload
    def __sub__(self, other: TimeDelta, /) -> DateTimeDelta: ...
    def __rsub__(self, other: TimeDelta, /) -> DateTimeDelta: ...

@final
class DateTimeDelta(_DeltaMixin):
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
    ) -> None: ...
    def date_part(self) -> DateDelta: ...
    def time_part(self) -> TimeDelta: ...
    def in_months_days_secs_nanos(self) -> tuple[int, int, int, int]: ...
    def __add__(self, other: Delta, /) -> Self: ...
    def __radd__(self, other: TimeDelta | DateDelta, /) -> Self: ...
    def __sub__(self, other: Delta, /) -> Self: ...
    def __rsub__(self, other: TimeDelta | DateDelta, /) -> Self: ...

Delta: TypeAlias = DateTimeDelta | TimeDelta | DateDelta

class _LocalTime(ABC):
    @property
    def year(self) -> int: ...
    @property
    def month(self) -> int: ...
    @property
    def day(self) -> int: ...
    @property
    def hour(self) -> int: ...
    @property
    def minute(self) -> int: ...
    @property
    def second(self) -> int: ...
    @property
    def nanosecond(self) -> int: ...
    def date(self) -> Date: ...
    def time(self) -> Time: ...

class _ExactTime(ABC):
    def timestamp(self) -> int: ...
    def timestamp_millis(self) -> int: ...
    def timestamp_nanos(self) -> int: ...
    @overload
    def to_fixed_offset(self, /) -> OffsetDateTime: ...
    @overload
    def to_fixed_offset(
        self, offset: int | TimeDelta, /
    ) -> OffsetDateTime: ...
    def to_tz(self, tz: str, /) -> ZonedDateTime: ...
    def to_system_tz(self) -> SystemDateTime: ...
    def difference(self, other: _ExactTime, /) -> TimeDelta: ...
    def __lt__(self, other: _ExactTime, /) -> bool: ...
    def __le__(self, other: _ExactTime, /) -> bool: ...
    def __gt__(self, other: _ExactTime, /) -> bool: ...
    def __ge__(self, other: _ExactTime, /) -> bool: ...
    def exact_eq(self, other: Self, /) -> bool: ...

class _ExactAndLocalTime(_ExactTime, _LocalTime, ABC):
    def to_instant(self) -> Instant: ...
    def to_plain(self) -> PlainDateTime: ...
    @property
    def offset(self) -> TimeDelta: ...

@type_check_only
class _PyDateTimeMixin(_CommonISOMixin):
    @classmethod
    def from_py_datetime(cls, d: _datetime, /) -> Self: ...
    def py_datetime(self) -> _datetime: ...

@final
class Instant(_PyDateTimeMixin, _ExactTime):
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
    ) -> Self: ...
    MIN: ClassVar[Self]
    MAX: ClassVar[Self]
    @classmethod
    def now(cls) -> Self: ...
    @classmethod
    def from_timestamp(cls, i: int | float, /) -> Self: ...
    @classmethod
    def from_timestamp_millis(cls, i: int, /) -> Self: ...
    @classmethod
    def from_timestamp_nanos(cls, i: int, /) -> Self: ...
    def format_rfc2822(self) -> str: ...
    @classmethod
    def parse_rfc2822(cls, s: str, /) -> Self: ...
    def add(
        self,
        *,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
    ) -> Self: ...
    def subtract(
        self,
        *,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        milliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: int = 0,
    ) -> Self: ...
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
    ) -> Self: ...
    def __add__(self, delta: TimeDelta, /) -> Self: ...
    @overload
    def __sub__(self, other: _ExactTime) -> TimeDelta: ...
    @overload
    def __sub__(self, other: TimeDelta, /) -> Self: ...

@final
class OffsetDateTime(_PyDateTimeMixin, _ExactAndLocalTime):
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
    ) -> None: ...
    @classmethod
    def now(
        cls, offset: int | TimeDelta, /, *, ignore_dst: Literal[True]
    ) -> Self: ...
    @classmethod
    def from_timestamp(
        cls,
        i: int | float,
        /,
        *,
        offset: int | TimeDelta,
        ignore_dst: Literal[True],
    ) -> Self: ...
    @classmethod
    def from_timestamp_millis(
        cls, i: int, /, *, offset: int | TimeDelta, ignore_dst: Literal[True]
    ) -> Self: ...
    @classmethod
    def from_timestamp_nanos(
        cls, i: int, /, *, offset: int | TimeDelta, ignore_dst: Literal[True]
    ) -> Self: ...
    @classmethod
    def parse_strptime(cls, s: str, /, *, format: str) -> Self: ...
    def format_rfc2822(self) -> str: ...
    @classmethod
    def parse_rfc2822(cls, s: str, /) -> Self: ...
    def replace(
        self,
        *,
        year: int = ...,
        month: int = ...,
        day: int = ...,
        hour: int = ...,
        minute: int = ...,
        second: int = ...,
        nanosecond: int = ...,
        offset: int | TimeDelta = ...,
        ignore_dst: Literal[True],
    ) -> Self: ...
    def replace_date(
        self, d: Date, /, *, ignore_dst: Literal[True]
    ) -> Self: ...
    def replace_time(
        self, t: Time, /, *, ignore_dst: Literal[True]
    ) -> Self: ...
    @overload
    def add(
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
        ignore_dst: Literal[True],
    ) -> Self: ...
    @overload
    def add(self, d: Delta, /, ignore_dst: Literal[True]) -> Self: ...
    @overload
    def subtract(
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
        ignore_dst: Literal[True],
    ) -> Self: ...
    @overload
    def subtract(self, d: Delta, /, ignore_dst: Literal[True]) -> Self: ...
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
        ignore_dst: Literal[True],
    ) -> Self: ...
    def __sub__(self, other: _ExactTime, /) -> TimeDelta: ...

@final
class ZonedDateTime(_PyDateTimeMixin, _ExactAndLocalTime):
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
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> None: ...
    @property
    def tz(self) -> str: ...
    @classmethod
    def now(cls, tz: str, /) -> Self: ...
    @classmethod
    def from_timestamp(cls, i: int | float, /, *, tz: str) -> Self: ...
    @classmethod
    def from_timestamp_millis(cls, i: int, /, *, tz: str) -> Self: ...
    @classmethod
    def from_timestamp_nanos(cls, i: int, /, *, tz: str) -> Self: ...
    def replace(
        self,
        *,
        year: int = ...,
        month: int = ...,
        day: int = ...,
        hour: int = ...,
        minute: int = ...,
        second: int = ...,
        nanosecond: int = ...,
        tz: str = ...,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    def replace_date(
        self,
        d: Date,
        /,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    def replace_time(
        self,
        t: Time,
        /,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    @overload
    def add(
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
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    # FUTURE: include this in strict stubs version
    # @overload
    # def add(
    #     self,
    #     *,
    #     hours: float = 0,
    #     minutes: float = 0,
    #     seconds: float = 0,
    #     milliseconds: float = 0,
    #     microseconds: float = 0,
    #     nanoseconds: int = 0,
    # ) -> Self: ...
    @overload
    def add(self, d: TimeDelta, /) -> Self: ...
    @overload
    def add(
        self,
        d: DateDelta | DateTimeDelta,
        /,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    @overload
    def subtract(
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
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    # FUTURE: include this in strict stubs version
    # @overload
    # def subtract(
    #     self,
    #     *,
    #     hours: float = 0,
    #     minutes: float = 0,
    #     seconds: float = 0,
    #     milliseconds: float = 0,
    #     microseconds: float = 0,
    #     nanoseconds: int = 0,
    # ) -> Self: ...
    @overload
    def subtract(self, d: TimeDelta, /) -> Self: ...
    @overload
    def subtract(
        self,
        d: DateDelta | DateTimeDelta,
        /,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    def is_ambiguous(self) -> bool: ...
    def day_length(self) -> TimeDelta: ...
    def start_of_day(self) -> Self: ...
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
    ) -> Self: ...
    # FUTURE: disable date components in strict stubs version
    def __add__(self, delta: Delta, /) -> Self: ...
    @overload
    def __sub__(self, other: _ExactTime) -> TimeDelta: ...
    @overload
    def __sub__(self, other: Delta, /) -> Self: ...

@final
class SystemDateTime(_PyDateTimeMixin, _ExactAndLocalTime):
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
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> None: ...
    @classmethod
    def now(cls) -> Self: ...
    @classmethod
    def from_timestamp(cls, i: int | float, /) -> Self: ...
    @classmethod
    def from_timestamp_millis(cls, i: int, /) -> Self: ...
    @classmethod
    def from_timestamp_nanos(cls, i: int, /) -> Self: ...
    def replace(
        self,
        *,
        year: int = ...,
        month: int = ...,
        day: int = ...,
        hour: int = ...,
        minute: int = ...,
        second: int = ...,
        nanosecond: int = ...,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    def replace_date(
        self,
        d: Date,
        /,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    def replace_time(
        self,
        t: Time,
        /,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    @overload
    def add(
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
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    # FUTURE: include this in strict stubs version
    # @overload
    # def add(
    #     self,
    #     *,
    #     hours: float = 0,
    #     minutes: float = 0,
    #     seconds: float = 0,
    #     milliseconds: float = 0,
    #     microseconds: float = 0,
    #     nanoseconds: int = 0,
    # ) -> Self: ...
    @overload
    def add(self, d: TimeDelta, /) -> Self: ...
    @overload
    def add(
        self,
        d: DateDelta | DateTimeDelta,
        /,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    @overload
    def subtract(
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
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    # FUTURE: include this in strict stubs version
    # @overload
    # def subtract(
    #     self,
    #     *,
    #     hours: float = 0,
    #     minutes: float = 0,
    #     seconds: float = 0,
    #     milliseconds: float = 0,
    #     microseconds: float = 0,
    #     nanoseconds: int = 0,
    # ) -> Self: ...
    @overload
    def subtract(self, d: TimeDelta, /) -> Self: ...
    @overload
    def subtract(
        self,
        d: DateDelta | DateTimeDelta,
        /,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> Self: ...
    def is_ambiguous(self) -> bool: ...
    def day_length(self) -> TimeDelta: ...
    def start_of_day(self) -> SystemDateTime: ...
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
    ) -> Self: ...
    # FUTURE: disable date components in strict stubs version
    def __add__(self, delta: Delta, /) -> Self: ...
    @overload
    def __sub__(self, other: _ExactTime, /) -> TimeDelta: ...
    @overload
    def __sub__(self, other: Delta, /) -> Self: ...

@final
class PlainDateTime(_PyDateTimeMixin, _DateOrTimeMixin, _LocalTime):
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
    ) -> None: ...
    def assume_utc(self) -> Instant: ...
    def assume_fixed_offset(
        self, offset: int | TimeDelta, /
    ) -> OffsetDateTime: ...
    def assume_tz(
        self,
        tz: str,
        /,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> ZonedDateTime: ...
    def assume_system_tz(
        self,
        *,
        disambiguate: Literal["compatible", "raise", "earlier", "later"] = ...,
    ) -> SystemDateTime: ...
    @classmethod
    def parse_strptime(cls, s: str, /, *, format: str) -> Self: ...
    def replace(
        self,
        *,
        year: int = ...,
        month: int = ...,
        day: int = ...,
        hour: int = ...,
        minute: int = ...,
        second: int = ...,
        nanosecond: int = ...,
    ) -> Self: ...
    def replace_date(self, d: Date, /) -> Self: ...
    def replace_time(self, t: Time, /) -> Self: ...
    @overload
    def add(
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
        ignore_dst: Literal[True],
    ) -> Self: ...
    @overload
    def add(
        self, *, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0
    ) -> Self: ...
    @overload
    def add(self, d: DateDelta, /) -> Self: ...
    @overload
    def add(
        self, d: TimeDelta | DateTimeDelta, /, *, ignore_dst: Literal[True]
    ) -> Self: ...
    @overload
    def subtract(
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
        ignore_dst: Literal[True],
    ) -> Self: ...
    @overload
    def subtract(
        self, *, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0
    ) -> Self: ...
    @overload
    def subtract(self, d: DateDelta, /) -> Self: ...
    @overload
    def subtract(
        self, d: TimeDelta | DateTimeDelta, /, *, ignore_dst: Literal[True]
    ) -> Self: ...
    def difference(
        self, other: Self, /, *, ignore_dst: Literal[True]
    ) -> TimeDelta: ...
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
    ) -> Self: ...
    def __add__(self, delta: DateDelta, /) -> Self: ...
    def __sub__(self, other: DateDelta, /) -> Self: ...

@final
class RepeatedTime(ValueError): ...

@final
class SkippedTime(ValueError): ...

@final
class InvalidOffsetError(ValueError): ...

@final
class ImplicitlyIgnoringDST(TypeError): ...

# Why not a subclass of KeyError? Because:
# - It's a better fit. The user doesn't care that it's a lookup, they just care
#   about it being valid or not (ValueError).
# - It can be raised during parsing. Keeping this a ValueError means that
#   the user can catch all parsing exceptions consistently.
@final
class TimeZoneNotFoundError(ValueError): ...

class Weekday(enum.Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

MONDAY = Weekday.MONDAY
TUESDAY = Weekday.TUESDAY
WEDNESDAY = Weekday.WEDNESDAY
THURSDAY = Weekday.THURSDAY
FRIDAY = Weekday.FRIDAY
SATURDAY = Weekday.SATURDAY
SUNDAY = Weekday.SUNDAY

def years(i: int, /) -> DateDelta: ...
def months(i: int, /) -> DateDelta: ...
def weeks(i: int, /) -> DateDelta: ...
def days(i: int, /) -> DateDelta: ...
def hours(i: float, /) -> TimeDelta: ...
def minutes(i: float, /) -> TimeDelta: ...
def seconds(i: float, /) -> TimeDelta: ...
def milliseconds(i: float, /) -> TimeDelta: ...
def microseconds(i: float, /) -> TimeDelta: ...
def nanoseconds(i: int, /) -> TimeDelta: ...

class _TimePatch:
    def shift(self, *args: object, **kwargs: object) -> None: ...

def patch_current_time(
    i: _ExactTime, /, *, keep_ticking: bool
) -> _GeneratorContextManager[_TimePatch]: ...

TZPATH: tuple[str, ...]

def reset_tzpath(
    to: Iterable[str | PathLike[str]] | None = None, /
) -> None: ...
def clear_tzcache(*, only_keys: Iterable[str] | None = None) -> None: ...
def available_timezones() -> set[str]: ...
