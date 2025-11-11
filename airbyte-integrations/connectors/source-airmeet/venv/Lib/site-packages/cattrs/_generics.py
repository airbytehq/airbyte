from collections.abc import Mapping
from typing import Any, get_args

from attrs import NOTHING
from typing_extensions import Self

from ._compat import copy_with, is_annotated, is_generic


def deep_copy_with(t, mapping: Mapping[str, Any], self_is=NOTHING):
    args = get_args(t)
    rest = ()
    if is_annotated(t) and args:
        # If we're dealing with `Annotated`, we only map the first type parameter
        rest = tuple(args[1:])
        args = (args[0],)
    new_args = (
        tuple(
            (
                self_is
                if a is Self and self_is is not NOTHING
                else (
                    mapping[a.__name__]
                    if hasattr(a, "__name__") and a.__name__ in mapping
                    else (deep_copy_with(a, mapping, self_is) if is_generic(a) else a)
                )
            )
            for a in args
        )
        + rest
    )
    return copy_with(t, new_args) if new_args != args else t
