from typing import Awaitable, TypeVar, Union

__all__ = ["AwaitableOrValue"]


T = TypeVar("T")

AwaitableOrValue = Union[Awaitable[T], T]
