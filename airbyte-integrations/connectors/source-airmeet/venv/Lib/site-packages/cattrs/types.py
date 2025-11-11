from typing import Protocol, TypeVar

__all__ = ["SimpleStructureHook"]

In = TypeVar("In")
T = TypeVar("T")


class SimpleStructureHook(Protocol[In, T]):
    """A structure hook with an optional (ignored) second argument."""

    def __call__(self, _: In, /, cl=...) -> T: ...
