"""Typing for semver."""

from functools import partial
from typing import Union, Optional, Tuple, Dict, Iterable, Callable, TypeVar

VersionPart = Union[int, Optional[str]]
VersionTuple = Tuple[int, int, int, Optional[str], Optional[str]]
VersionDict = Dict[str, VersionPart]
VersionIterator = Iterable[VersionPart]
String = Union[str, bytes]
F = TypeVar("F", bound=Callable)
Decorator = Union[Callable[..., F], partial]
