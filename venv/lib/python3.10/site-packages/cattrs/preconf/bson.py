"""Preconfigured converters for bson."""
from base64 import b85decode, b85encode
from datetime import date, datetime
from typing import Any, Type, TypeVar, Union

from bson import DEFAULT_CODEC_OPTIONS, CodecOptions, Int64, ObjectId, decode, encode

from cattrs._compat import AbstractSet, is_mapping
from cattrs.gen import make_mapping_structure_fn

from ..converters import BaseConverter, Converter
from ..strategies import configure_union_passthrough
from . import validate_datetime

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
        cl: Type[T],
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
    """

    def gen_unstructure_mapping(cl: Any, unstructure_to=None):
        key_handler = str
        args = getattr(cl, "__args__", None)
        if args:
            if issubclass(args[0], str):
                key_handler = None
            elif issubclass(args[0], bytes):

                def key_handler(k):
                    return b85encode(k).decode("utf8")

        return converter.gen_unstructure_mapping(
            cl, unstructure_to=unstructure_to, key_handler=key_handler
        )

    def gen_structure_mapping(cl: Any):
        args = getattr(cl, "__args__", None)
        if args and issubclass(args[0], bytes):
            h = make_mapping_structure_fn(cl, converter, key_type=Base85Bytes)
        else:
            h = make_mapping_structure_fn(cl, converter)
        return h

    converter.register_structure_hook(Base85Bytes, lambda v, _: b85decode(v))
    converter._unstructure_func.register_func_list(
        [(is_mapping, gen_unstructure_mapping, True)]
    )
    converter._structure_func.register_func_list(
        [(is_mapping, gen_structure_mapping, True)]
    )

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


def make_converter(*args: Any, **kwargs: Any) -> BsonConverter:
    kwargs["unstruct_collection_overrides"] = {
        AbstractSet: list,
        **kwargs.get("unstruct_collection_overrides", {}),
    }
    res = BsonConverter(*args, **kwargs)
    configure_converter(res)

    return res
