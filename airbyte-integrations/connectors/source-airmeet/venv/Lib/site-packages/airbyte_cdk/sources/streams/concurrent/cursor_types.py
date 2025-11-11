from abc import abstractmethod
from typing import Protocol


class GapType(Protocol):
    """
    This is the representation of gaps between two cursor values. Examples:
    * if cursor values are datetimes, GapType is timedelta
    * if cursor values are integer, GapType will also be integer
    """

    pass


class CursorValueType(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __lt__(self: "CursorValueType", other: "CursorValueType") -> bool:
        pass

    @abstractmethod
    def __ge__(self: "CursorValueType", other: "CursorValueType") -> bool:
        pass

    @abstractmethod
    def __add__(self: "CursorValueType", other: GapType) -> "CursorValueType":
        pass

    @abstractmethod
    def __sub__(self: "CursorValueType", other: GapType) -> "CursorValueType":
        pass
