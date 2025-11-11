"""Preconfigured converters for bson."""

from base64 import b85decode, b85encode
from collections.abc import Set
from datetime import date, datetime
from typing import Any, TypeVar, Union

from bson import DEFAULT_CODEC_OPTIONS, CodecOptions, Int64, ObjectId, decode, encode

from .._compat import is_mapping, is_subclass
from ..cols import mapping_structure_factory
from ..converters import BaseConverter, Converter
from ..dispatch import StructureHook
from ..fns import identity
from ..literals import is_literal_containing_enums
from ..strategies import configure_union_passthrough
from . import (
    is_primitive_enum,
    literals_with_enums_unstructure_factory,
    validate_datetime,
    wrap,
)

T = TypeVar("T")


class Base85Bytes(bytes):
    """A subclass to help with binary key encoding/decoding."""


class BsonConverter(Converter):
    def dumps(
        self,
        obj: Any,
        unstructure_as: Any = None,
        check_keys: bool = False,
        codec_options: CodecOptions = DEFAULT_CODEC_OPTIONS,
    ) -> bytes:
        return encode(
            self.unstructure(obj, unstructure_as=unstructure_as),
            check_keys=check_keys,
            codec_options=codec_options,
        )

    def loads(
        self,
        data: bytes,
        cl: type[T],
        codec_options: CodecOptions = DEFAULT_CODEC_OPTIONS,
    ) -> T:
        return self.structure(decode(data, codec_options=codec_options), cl)


def configure_converter(converter: BaseConverter):
    """
    Configure the converter for use with the bson library.

    * sets are serialized as lists
    * byte mapping keys are base85-encoded into strings when unstructuring, and reverse
    * non-string, non-byte mapping keys are coerced into strings when unstructuring
    * a deserialization hook is registered for bson.ObjectId by default
    * string and int enums are passed through when unstructuring

    .. versionchanged:: 24.2.0
        Enums are left to the library to unstructure, speeding them up.
    """

    def gen_unstructure_mapping(cl: Any, unstructure_to=None):
        key_handler = str
        args = getattr(cl, "__args__", None)
        if args:
            if is_subclass(args[0], str):
                key_handler = None
            elif is_subclass(args[0], bytes):

                def key_handler(k):
                    return b85encode(k).decode("utf8")

        return converter.gen_unstructure_mapping(
            cl, unstructure_to=unstructure_to, key_handler=key_handler
        )

    def gen_structure_mapping(cl: Any) -> StructureHook:
        args = getattr(cl, "__args__", None)
        if args and is_subclass(args[0], bytes):
            h = mapping_structure_factory(cl, converter, key_type=Base85Bytes)
        else:
            h = mapping_structure_factory(cl, converter)
        return h

    converter.register_structure_hook(Base85Bytes, lambda v, _: b85decode(v))
    converter.register_unstructure_hook_factory(is_mapping, gen_unstructure_mapping)
    converter.register_structure_hook_factory(is_mapping, gen_structure_mapping)

    converter.register_structure_hook(ObjectId, lambda v, _: ObjectId(v))
    configure_union_passthrough(
        Union[str, bool, int, float, None, bytes, datetime, ObjectId, Int64], converter
    )

    # datetime inherits from date, so identity unstructure hook used
    # here to prevent the date unstructure hook running.
    converter.register_unstructure_hook(datetime, lambda v: v)
    converter.register_structure_hook(datetime, validate_datetime)
    converter.register_unstructure_hook(date, lambda v: v.isoformat())
    converter.register_structure_hook(date, lambda v, _: date.fromisoformat(v))
    converter.register_unstructure_hook_func(is_primitive_enum, identity)
    converter.register_unstructure_hook_factory(
        is_literal_containing_enums, literals_with_enums_unstructure_factory
    )


@wrap(BsonConverter)
def make_converter(*args: Any, **kwargs: Any) -> BsonConverter:
    kwargs["unstruct_collection_overrides"] = {
        Set: list,
        **kwargs.get("unstruct_collection_overrides", {}),
    }
    res = BsonConverter(*args, **kwargs)
    configure_converter(res)

    return res
