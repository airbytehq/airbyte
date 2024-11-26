from __future__ import annotations

from typing import TypeVar

from .._compat import get_args, get_origin, is_generic


def generate_mapping(cl: type, old_mapping: dict[str, type] = {}) -> dict[str, type]:
    mapping = {}

    origin = get_origin(cl)

    if origin is not None:
        # To handle the cases where classes in the typing module are using
        # the GenericAlias structure but aren't a Generic and hence
        # end up in this function but do not have an `__parameters__`
        # attribute. These classes are interface types, for example
        # `typing.Hashable`.
        parameters = getattr(get_origin(cl), "__parameters__", None)
        if parameters is None:
            return dict(old_mapping)

        for p, t in zip(parameters, get_args(cl)):
            if isinstance(t, TypeVar):
                continue
            mapping[p.__name__] = t

        if not mapping:
            return dict(old_mapping)
    elif is_generic(cl):
        # Origin is None, so this may be a subclass of a generic class.
        orig_bases = cl.__orig_bases__
        for base in orig_bases:
            if not hasattr(base, "__args__"):
                continue
            base_args = base.__args__
            if not hasattr(base.__origin__, "__parameters__"):
                continue
            base_params = base.__origin__.__parameters__
            for param, arg in zip(base_params, base_args):
                mapping[param.__name__] = arg

    return mapping
