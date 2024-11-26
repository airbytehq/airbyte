import builtins
import dataclasses
import functools
import inspect
import operator
import types
import typing
from collections.abc import Coroutine
from functools import partial
from typing import Any, TypeAlias, TypeGuard, TypeVar, cast

import anyio
import anyio.from_thread
import anyio.to_thread
import cattrs
import cattrs.v
import typing_extensions
from beartype.door import TypeHint, UnionTypeHint
from graphql.pyutils import snake_to_camel

from ._arguments import Arg
from ._types import ObjectDefinition

asyncify = anyio.to_thread.run_sync
syncify = anyio.from_thread.run

T = TypeVar("T")

AwaitableOrValue: TypeAlias = Coroutine[Any, Any, T] | T


async def await_maybe(value: AwaitableOrValue[T]) -> T:
    return await value if inspect.iscoroutine(value) else cast(T, value)


def transform_error(
    exc: Exception,
    msg: str = "",
    origin: Any | None = None,
    typ: type | None = None,
) -> str:
    """Transform a cattrs error into a list of error messages."""
    path = "$"

    if origin is not None:
        path = getattr(origin, "__qualname__", "")
        if hasattr(origin, "__module__"):
            path = f"{origin.__module__}.{path}"

    fn = partial(cattrs.transform_error, path=path)

    if typ is not None:
        fn = partial(
            fn, format_exception=lambda e, _: cattrs.v.format_exception(e, typ)
        )

    errors = "; ".join(error.removesuffix(" @ $") for error in fn(exc))
    return f"{msg}: {errors}" if msg else errors


def to_pascal_case(s: str) -> str:
    """Convert a string to PascalCase."""
    return snake_to_camel(s.replace("-", "_"))


def to_camel_case(s: str) -> str:
    """Convert a string to camelCase."""
    return snake_to_camel(s.replace("-", "_"), upper=False)


def get_doc(obj: Any) -> str | None:
    """Get the last Doc() in an annotated type or the docstring of an object."""
    if is_annotated(obj):
        return next(
            (
                arg.documentation
                for arg in reversed(typing.get_args(obj))
                if isinstance(arg, typing_extensions.Doc)
            ),
            None,
        )
    if inspect.getmodule(obj) != builtins and (
        inspect.isclass(obj) or inspect.isfunction(obj)
    ):
        doc = inspect.getdoc(obj)
        # By default, a dataclass's __doc__ will be the signature of the class,
        # not None.
        if (
            doc
            and dataclasses.is_dataclass(obj)
            and doc.startswith(f"{obj.__name__}(")
            and doc.endswith(")")
        ):
            doc = None
        return doc
    return None


def get_arg_name(annotation: type) -> str | None:
    """Get an alternative name in last Arg() of an annotated type."""
    if is_annotated(annotation):
        return next(
            (
                arg.name
                for arg in reversed(typing.get_args(annotation))
                if isinstance(arg, Arg)
            ),
            None,
        )
    return None


def is_union(th: TypeHint) -> bool:
    """Returns True if the unsubscripted part of a type is a Union."""
    return isinstance(th, UnionTypeHint)


def is_optional(th: TypeHint) -> bool:
    """Returns True if the annotation is SomeType | None.

    Does not support Annotated types. Use only on types that have been
    resolved with get_type_hints.
    """
    return th.is_bearable(None)


def non_optional(th: TypeHint) -> TypeHint:
    """Removes None from a union.

    Does not support Annotated types. Use only on types that have been
    resolved with get_type_hints.
    """
    if TypeHint(None) not in th:
        return th

    args = (x for x in th.args if x is not type(None))
    return TypeHint(functools.reduce(operator.or_, args))


_T = TypeVar("_T", bound=type)


def is_annotated(annotation: type) -> typing.TypeGuard[typing.Annotated]:
    """Check if the given type is an annotated type."""
    return typing.get_origin(annotation) in (
        typing.Annotated,
        typing_extensions.Annotated,
    )


def strip_annotations(t: _T) -> _T:
    """Strip the annotations from a given type."""
    return strip_annotations(typing.get_args(t)[0]) if is_annotated(t) else t


def is_mod_object_type(cls) -> TypeGuard[ObjectDefinition]:
    """Check if the given class was decorated with @object_type."""
    return isinstance(getattr(cls, "__dagger_type__", None), ObjectDefinition)


def get_alt_constructor(cls) -> types.MethodType | None:
    """Get classmethod named `create` from object type."""
    if inspect.isclass(cls) and is_mod_object_type(cls):
        fn = getattr(cls, "create", None)
        if inspect.ismethod(fn) and fn.__self__ is cls:
            return fn
    return None
