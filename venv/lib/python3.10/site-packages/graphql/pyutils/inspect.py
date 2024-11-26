from inspect import (
    isclass,
    ismethod,
    isfunction,
    isgeneratorfunction,
    isgenerator,
    iscoroutinefunction,
    iscoroutine,
    isasyncgenfunction,
    isasyncgen,
)
from typing import Any, List

from .undefined import Undefined

__all__ = ["inspect"]

max_recursive_depth = 2
max_str_size = 240
max_list_size = 10


def inspect(value: Any) -> str:
    """Inspect value and a return string representation for error messages.

    Used to print values in error messages. We do not use repr() in order to not
    leak too much of the inner Python representation of unknown objects, and we
    do not use json.dumps() because not all objects can be serialized as JSON and
    we want to output strings with single quotes like Python repr() does it.

    We also restrict the size of the representation by truncating strings and
    collections and allowing only a maximum recursion depth.
    """
    return inspect_recursive(value, [])


def inspect_recursive(value: Any, seen_values: List) -> str:
    if value is None or value is Undefined or isinstance(value, (bool, float, complex)):
        return repr(value)
    if isinstance(value, (int, str, bytes, bytearray)):
        return trunc_str(repr(value))
    if len(seen_values) < max_recursive_depth and value not in seen_values:
        # check if we have a custom inspect method
        inspect_method = getattr(value, "__inspect__", None)
        if inspect_method is not None and callable(inspect_method):
            s = inspect_method()
            if isinstance(s, str):
                return trunc_str(s)
            seen_values = [*seen_values, value]
            return inspect_recursive(s, seen_values)
        # recursively inspect collections
        if isinstance(value, (list, tuple, dict, set, frozenset)):
            if not value:
                return repr(value)
            seen_values = [*seen_values, value]
            if isinstance(value, list):
                items = value
            elif isinstance(value, dict):
                items = list(value.items())
            else:
                items = list(value)
            items = trunc_list(items)
            if isinstance(value, dict):
                s = ", ".join(
                    "..."
                    if v is ELLIPSIS
                    else inspect_recursive(v[0], seen_values)
                    + ": "
                    + inspect_recursive(v[1], seen_values)
                    for v in items
                )
            else:
                s = ", ".join(
                    "..." if v is ELLIPSIS else inspect_recursive(v, seen_values)
                    for v in items
                )
            if isinstance(value, tuple):
                if len(items) == 1:
                    return f"({s},)"
                return f"({s})"
            if isinstance(value, (dict, set)):
                return "{" + s + "}"
            if isinstance(value, frozenset):
                return f"frozenset({{{s}}})"
            return f"[{s}]"
    else:
        # handle collections that are nested too deep
        if isinstance(value, (list, tuple, dict, set, frozenset)):
            if not value:
                return repr(value)
            if isinstance(value, list):
                return "[...]"
            if isinstance(value, tuple):
                return "(...)"
            if isinstance(value, dict):
                return "{...}"
            if isinstance(value, set):
                return "set(...)"
            return "frozenset(...)"
    if isinstance(value, Exception):
        type_ = "exception"
        value = type(value)
    elif isclass(value):
        type_ = "exception class" if issubclass(value, Exception) else "class"
    elif ismethod(value):
        type_ = "method"
    elif iscoroutinefunction(value):
        type_ = "coroutine function"
    elif isasyncgenfunction(value):
        type_ = "async generator function"
    elif isgeneratorfunction(value):
        type_ = "generator function"
    elif isfunction(value):
        type_ = "function"
    elif iscoroutine(value):
        type_ = "coroutine"
    elif isasyncgen(value):
        type_ = "async generator"
    elif isgenerator(value):
        type_ = "generator"
    else:
        # stringify (only) the well-known GraphQL types
        from ..type import (
            GraphQLDirective,
            GraphQLNamedType,
            GraphQLScalarType,
            GraphQLWrappingType,
        )

        if isinstance(
            value,
            (
                GraphQLDirective,
                GraphQLNamedType,
                GraphQLScalarType,
                GraphQLWrappingType,
            ),
        ):
            return str(value)
        try:
            name = type(value).__name__
            if not name or "<" in name or ">" in name:
                raise AttributeError
        except AttributeError:
            return "<object>"
        else:
            return f"<{name} instance>"
    try:
        name = value.__name__
        if not name or "<" in name or ">" in name:
            raise AttributeError
    except AttributeError:
        return f"<{type_}>"
    else:
        return f"<{type_} {name}>"


def trunc_str(s: str) -> str:
    """Truncate strings to maximum length."""
    if len(s) > max_str_size:
        i = max(0, (max_str_size - 3) // 2)
        j = max(0, max_str_size - 3 - i)
        s = s[:i] + "..." + s[-j:]
    return s


def trunc_list(s: List) -> List:
    """Truncate lists to maximum length."""
    if len(s) > max_list_size:
        i = max_list_size // 2
        j = i - 1
        s = s[:i] + [ELLIPSIS] + s[-j:]
    return s


class InspectEllipsisType:
    """Singleton class for indicating ellipses in iterables."""


ELLIPSIS = InspectEllipsisType()
