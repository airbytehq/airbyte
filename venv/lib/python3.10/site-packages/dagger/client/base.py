from __future__ import annotations

import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._core import Context


class Scalar(str):
    """Custom scalar."""

    __slots__ = ()


class Enum(str, enum.Enum):
    """Custom enumeration."""

    __slots__ = ()

    def __str__(self) -> str:
        """The string representation of the enum value."""
        return str(self.value)


class Object:
    """Base for object types."""

    __slots__ = ()

    @classmethod
    def _graphql_name(cls) -> str:
        return cls.__name__


class Input(Object):
    """Input object type."""

    __slots__ = ()


class Type(Object):
    """Object type."""

    __slots__ = ("_ctx",)

    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def _select(self, *args, **kwargs):
        return self._ctx.select(self._graphql_name(), *args, **kwargs)

    def _select_multiple(self, **kwargs):
        return self._ctx.select_multiple(self._graphql_name(), **kwargs)
