from typing_extensions import Doc


from ._arguments import Arg as Arg
from ._module import Module as Module

_default_mod = Module()

object_type = _default_mod.object_type
function = _default_mod.function
field = _default_mod.field


def default_module() -> Module:
    """Return the default Module builder instance."""
    return _default_mod


__all__ = [
    "Arg",
    "Doc",  # Only re-exported because it's in `typing_extensions`.
    "field",
    "function",
    "object_type",
]
