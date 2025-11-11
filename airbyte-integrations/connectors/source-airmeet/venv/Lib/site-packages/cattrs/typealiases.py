"""Utilities for type aliases."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from ._compat import is_generic
from ._generics import deep_copy_with
from .dispatch import StructureHook
from .gen._generics import generate_mapping

if TYPE_CHECKING:
    from .converters import BaseConverter

__all__ = ["get_type_alias_base", "is_type_alias", "type_alias_structure_factory"]

if sys.version_info >= (3, 12):
    from types import GenericAlias
    from typing import TypeAliasType

    def is_type_alias(type: Any) -> bool:
        """Is this a PEP 695 type alias?"""
        return isinstance(
            type.__origin__ if type.__class__ is GenericAlias else type, TypeAliasType
        )

else:

    def is_type_alias(type: Any) -> bool:
        """Is this a PEP 695 type alias?"""
        return False


def get_type_alias_base(type: Any) -> Any:
    """
    What is this a type alias of?

    Works only on 3.12+.
    """
    return type.__value__


def type_alias_structure_factory(type: Any, converter: BaseConverter) -> StructureHook:
    base = get_type_alias_base(type)
    if is_generic(type):
        mapping = generate_mapping(type)
        if base.__name__ in mapping:
            # Probably just type T = T
            base = mapping[base.__name__]
        else:
            base = deep_copy_with(base, mapping)
    res = converter.get_structure_hook(base)
    if res == converter._structure_call:
        # we need to replace the type arg of `structure_call`
        return lambda v, _, __base=base: __base(v)
    return lambda v, _, __base=base: res(v, __base)
