from abc import ABC
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

from airbyte_cdk.sources.streams.concurrent.cursor_types import CursorValueType


class ClampingStrategy(ABC):
    def clamp(self, value: CursorValueType) -> CursorValueType:
        raise NotImplementedError()


class NoClamping(ClampingStrategy):
    def clamp(self, value: CursorValueType) -> CursorValueType:
        return value


class ClampingEndProvider:
    def __init__(
        self,
        clamping_strategy: ClampingStrategy,
        end_provider: Callable[[], CursorValueType],
        granularity: timedelta,
    ) -> None:
        self._clamping_strategy = clamping_strategy
        self._end_provider = end_provider
        self._granularity = granularity

    def __call__(self) -> CursorValueType:
        return self._clamping_strategy.clamp(self._end_provider()) - self._granularity


class DayClampingStrategy(ClampingStrategy):
    def __init__(self, is_ceiling: bool = True) -> None:
        self._is_ceiling = is_ceiling

    def clamp(self, value: datetime) -> datetime:  # type: ignore  # datetime implements method from CursorValueType
        return_value = value.replace(hour=0, minute=0, second=0, microsecond=0)
        if self._is_ceiling:
            return return_value + timedelta(days=1)
        return return_value


class MonthClampingStrategy(ClampingStrategy):
    def __init__(self, is_ceiling: bool = True) -> None:
        self._is_ceiling = is_ceiling

    def clamp(self, value: datetime) -> datetime:  # type: ignore  # datetime implements method from CursorValueType
        return_value = value.replace(hour=0, minute=0, second=0, microsecond=0)
        needs_to_round = value.day != 1
        if not needs_to_round:
            return return_value

        return self._ceil(return_value) if self._is_ceiling else return_value.replace(day=1)

    def _ceil(self, value: datetime) -> datetime:
        return value.replace(
            year=value.year + 1 if value.month == 12 else value.year,
            month=(value.month % 12) + 1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )


class Weekday(Enum):
    """
    These integer values map to the same ones used by the Datetime.date.weekday() implementation
    """

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class WeekClampingStrategy(ClampingStrategy):
    def __init__(self, day_of_week: Weekday, is_ceiling: bool = True) -> None:
        self._day_of_week = day_of_week.value
        self._is_ceiling = is_ceiling

    def clamp(self, value: datetime) -> datetime:  # type: ignore  # datetime implements method from CursorValueType
        days_diff_to_ceiling = (
            7 - (value.weekday() - self._day_of_week)
            if value.weekday() > self._day_of_week
            else abs(value.weekday() - self._day_of_week)
        )
        delta = (
            timedelta(days_diff_to_ceiling)
            if self._is_ceiling
            else timedelta(days_diff_to_ceiling - 7)
        )
        return value.replace(hour=0, minute=0, second=0, microsecond=0) + delta
