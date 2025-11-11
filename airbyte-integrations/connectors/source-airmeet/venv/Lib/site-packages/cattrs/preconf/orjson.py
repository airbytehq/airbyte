"""Preconfigured converters for orjson."""

from base64 import b85decode, b85encode
from collections.abc import Set
from datetime import date, datetime
from enum import Enum
from functools import partial
from typing import Any, TypeVar, Union

from orjson import dumps, loads

from .._compat import is_subclass
from ..cols import is_mapping, is_namedtuple, namedtuple_unstructure_factory
from ..converters import Converter
from ..fns import identity
from ..literals import is_literal_containing_enums
from ..strategies import configure_union_passthrough
from . import is_primitive_enum, literals_with_enums_unstructure_factory, wrap

__all__ = ["OrjsonConverter", "configure_converter", "make_converter"]

T = TypeVar("T")


class OrjsonConverter(Converter):
    def dumps(self, obj: Any, unstructure_as: Any = None, **kwargs: Any) -> bytes:
        return dumps(self.unstructure(obj, unstructure_as=unstructure_as), **kwargs)

    def loads(self, data: Union[bytes, bytearray, memoryview, str], cl: type[T]) -> T:
        return self.structure(loads(data), cl)


def configure_converter(converter: Converter) -> None:
    """
    Configure the converter for use with the orjson library.

    * bytes are serialized as base85 strings
    * datetimes and dates are passed through to be serialized as RFC 3339 by orjson
    * typed namedtuples are serialized as lists
    * sets are serialized as lists
    * string enum mapping keys have special handling
    * mapping keys are coerced into strings when unstructuring
    * bare, string and int enums are passed through when unstructuring

    .. versionchanged:: 24.1.0
        Add support for typed namedtuples.
    .. versionchanged:: 24.2.0
        Enums are left to the library to unstructure, speeding them up.
    """
    converter.register_unstructure_hook(
        bytes, lambda v: (b85encode(v) if v else b"").decode("utf8")
    )
    converter.register_structure_hook(bytes, lambda v, _: b85decode(v))

    converter.register_structure_hook(datetime, lambda v, _: datetime.fromisoformat(v))
    converter.register_structure_hook(date, lambda v, _: date.fromisoformat(v))

    def unstructure_mapping_factory(cl: Any, unstructure_to=None):
        key_handler = str
        args = getattr(cl, "__args__", None)
        if args:
            if is_subclass(args[0], str) and is_subclass(args[0], Enum):

                def key_handler(v):
                    return v.value

            else:
                # It's possible the handler for the key type has been overridden.
                # (For example base85 encoding for bytes.)
                # In that case, we want to use the override.

                kh = converter.get_unstructure_hook(args[0])
                if kh != identity:
                    key_handler = kh

        return converter.gen_unstructure_mapping(
            cl, unstructure_to=unstructure_to, key_handler=key_handler
        )

    converter._unstructure_func.register_func_list(
        [
            (is_mapping, unstructure_mapping_factory, True),
            (
                is_namedtuple,
                partial(namedtuple_unstructure_factory, unstructure_to=tuple),
                "extended",
            ),
        ]
    )
    converter.register_unstructure_hook_func(
        partial(is_primitive_enum, include_bare_enums=True), identity
    )
    converter.register_unstructure_hook_factory(
        is_literal_containing_enums, literals_with_enums_unstructure_factory
    )
    configure_union_passthrough(Union[str, bool, int, float, None], converter)


@wrap(OrjsonConverter)
def make_converter(*args: Any, **kwargs: Any) -> OrjsonConverter:
    kwargs["unstruct_collection_overrides"] = {
        Set: list,
        **kwargs.get("unstruct_collection_overrides", {}),
    }
    res = OrjsonConverter(*args, **kwargs)
    configure_converter(res)

    return res
