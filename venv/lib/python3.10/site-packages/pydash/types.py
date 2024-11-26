import typing as t

from typing_extensions import Protocol


if t.TYPE_CHECKING:
    # F401: imported but unused
    # py3.7 flake8 doesn't get it for type aliases
    from decimal import Decimal  # noqa: F401

IterateeObjT = t.Union[int, str, t.List, t.Tuple, t.Dict]
NumberT = t.Union[float, int, "Decimal"]
NumberNoDecimalT = t.Union[float, int]
PathT = t.Union[t.Hashable, t.List[t.Hashable]]


_T_co = t.TypeVar("_T_co", covariant=True)
_T_contra = t.TypeVar("_T_contra", contravariant=True)


class SupportsMul(Protocol[_T_contra, _T_co]):
    def __mul__(self, x: _T_contra) -> _T_co:
        ...


class SupportsRound(Protocol[_T_co]):
    def __round__(self) -> _T_co:
        ...
