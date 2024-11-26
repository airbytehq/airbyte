import contextlib
import functools
import inspect
import typing
from collections.abc import Callable, Coroutine, Sequence
from typing import Annotated, Any, ParamSpec, TypeGuard, TypeVar, overload

from beartype import beartype
from beartype.door import TypeHint
from beartype.roar import BeartypeCallHintViolation
from beartype.vale import Is, IsInstance, IsSubclass

from .base import Scalar, Type

IDScalar = Annotated[Scalar, Is[lambda obj: type(obj).__name__.endswith("ID")]]


@typing.runtime_checkable
class HasID(typing.Protocol):
    async def id(self) -> IDScalar:  # noqa: A003
        ...


IDTypeSubclass = Annotated[type[HasID], IsSubclass[Type]]
IDType = Annotated[HasID, IsInstance[Type]]
IDTypeSeq = Annotated[Sequence[IDType], ~IsInstance[str]]

IDTypeSubclassHint = TypeHint(IDTypeSubclass)
IDTypeHint = TypeHint(IDType)
IDTypeSeqHint = TypeHint(IDTypeSeq)


def is_id_type_subclass(v: type) -> TypeGuard[type[Type]]:
    return IDTypeSubclassHint.is_bearable(v)


def is_id_type(v: object) -> TypeGuard[IDType]:
    return IDTypeHint.is_bearable(v)


def is_id_type_sequence(v: object) -> TypeGuard[IDTypeSeq]:
    return IDTypeSeqHint.is_bearable(v)


_T = TypeVar("_T")
_P = ParamSpec("_P")


@overload
def typecheck(
    func: Callable[_P, Coroutine[Any, Any, _T]]
) -> Callable[_P, Coroutine[Any, Any, _T]]:
    ...


@overload
def typecheck(func: Callable[_P, _T]) -> Callable[_P, _T]:
    ...


def typecheck(
    func: Callable[_P, _T | Coroutine[Any, Any, _T]]
) -> Callable[_P, _T | Coroutine[Any, Any, _T]]:
    ...

    """
    Runtime type checking.

    Allows fast failure, before sending requests to the API,
    and with greater detail over the specific method and
    parameter with invalid type to help debug.

    This includes catching typos or forgetting to await a
    coroutine, but it's less forgiving in some instances.

    For example, an `args: Sequence[str]` parameter set as
    `args=["echo", 123]` was easily converting the int 123
    to a string by the dynamic query builder. Now it'll fail.
    """
    # Using beartype for the hard work, just tune the traceback a bit.
    # Hiding as **implementation detail** for now. The project is young
    # but very active and with good plans on making it very modular/pluggable.

    # Decorating here allows basic checks during definition time
    # so it'll be catched early, during development.
    bear = beartype(func)

    @contextlib.contextmanager
    def _handle_exception():
        try:
            yield
        except BeartypeCallHintViolation as e:
            # Tweak the error message a bit.
            msg = str(e).replace("@beartyped ", "")

            # Everything in `dagger.api.gen.` is exported under `dagger.`.
            msg = msg.replace("dagger.client.gen.", "dagger.")

            # No API methods accept a coroutine, add hint.
            if "<coroutine object" in msg:
                msg = f"{msg} Did you forget to await?"

            # The following `raise` line will show in traceback, keep
            # the noise down to minimum by instantiating outside of it.
            err = TypeError(msg).with_traceback(None)
            raise err from None

    if inspect.iscoroutinefunction(bear):

        @functools.wraps(func)
        async def async_wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            with _handle_exception():
                return await bear(*args, **kwargs)

        return async_wrapper

    if inspect.isfunction(bear):

        @functools.wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            with _handle_exception():
                return bear(*args, **kwargs)

        return wrapper

    return bear
