"""Unit classes that deals with rate, item & duration
"""
from enum import Enum
from typing import Union


class Duration(Enum):
    """Interval helper class"""

    SECOND = 1000
    MINUTE = 1000 * 60
    HOUR = 1000 * 60 * 60
    DAY = 1000 * 60 * 60 * 24
    WEEK = 1000 * 60 * 60 * 24 * 7

    def __mul__(self, mutiplier: float) -> int:
        return int(self.value * mutiplier)

    def __rmul__(self, multiplier: float) -> int:
        return self.__mul__(multiplier)

    def __add__(self, another_duration: Union["Duration", int]) -> int:
        return self.value + int(another_duration)

    def __radd__(self, another_duration: Union["Duration", int]) -> int:
        return self.__add__(another_duration)

    def __int__(self) -> int:
        return self.value

    def __eq__(self, duration: object) -> bool:
        if not isinstance(duration, (Duration, int)):
            return NotImplemented

        return self.value == int(duration)

    @staticmethod
    def readable(value: int) -> str:
        notes = [
            (Duration.WEEK, "w"),
            (Duration.DAY, "d"),
            (Duration.HOUR, "h"),
            (Duration.MINUTE, "m"),
            (Duration.SECOND, "s"),
        ]

        for note, shorten in notes:
            if value >= note.value:
                decimal_value = value / note.value
                return f"{decimal_value:0.1f}{shorten}"

        return f"{value}ms"


class RateItem:
    """RateItem is a wrapper for bucket to work with"""

    name: str
    weight: int
    timestamp: int

    def __init__(self, name: str, timestamp: int, weight: int = 1):
        self.name = name
        self.timestamp = timestamp
        self.weight = weight

    def __str__(self) -> str:
        return f"RateItem(name={self.name}, weight={self.weight}, timestamp={self.timestamp})"


class Rate:
    """Rate definition.

    Args:
        limit: Number of requests allowed within ``interval``
        interval: Time interval, in miliseconds
    """

    limit: int
    interval: int

    def __init__(
        self,
        limit: int,
        interval: Union[int, Duration],
    ):
        self.limit = limit
        self.interval = int(interval)
        assert self.interval
        assert self.limit

    def __str__(self) -> str:
        return f"limit={self.limit}/{Duration.readable(self.interval)}"

    def __repr__(self) -> str:
        return f"limit={self.limit}/{self.interval}"
