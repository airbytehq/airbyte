from enum import Enum
from typing import Any

from ._compat import is_literal

__all__ = ["is_literal", "is_literal_containing_enums"]


def is_literal_containing_enums(type: Any) -> bool:
    """Is this a literal containing at least one Enum?"""
    return is_literal(type) and any(isinstance(val, Enum) for val in type.__args__)
