"""Preconfigured converters for pyyaml."""
from datetime import date, datetime
from typing import Any, Type, TypeVar, Union

from yaml import safe_dump, safe_load

from cattrs._compat import FrozenSetSubscriptable

from ..converters import BaseConverter, Converter
from ..strategies import configure_union_passthrough
from . import validate_datetime

T = TypeVar("T")


def validate_date(v, _):
    if not isinstance(v, date):
        raise ValueError(f"Expected date, got {v}")
    return v


class PyyamlConverter(Converter):
    def dumps(self, obj: Any, unstructure_as: Any = None, **kwargs: Any) -> str:
        return safe_dump(self.unstructure(obj, unstructure_as=unstructure_as), **kwargs)

    def loads(self, data: str, cl: Type[T]) -> T:
        return self.structure(safe_load(data), cl)


def configure_converter(converter: BaseConverter):
    """
    Configure the converter for use with the pyyaml library.

    * frozensets are serialized as lists
    * string enums are converted into strings explicitly
    * datetimes and dates are validated
    """
    converter.register_unstructure_hook(
        str, lambda v: v if v.__class__ is str else v.value
    )

    # datetime inherits from date, so identity unstructure hook used
    # here to prevent the date unstructure hook running.
    converter.register_unstructure_hook(datetime, lambda v: v)
    converter.register_structure_hook(datetime, validate_datetime)
    converter.register_structure_hook(date, validate_date)
    configure_union_passthrough(
        Union[str, bool, int, float, None, bytes, datetime, date], converter
    )


def make_converter(*args: Any, **kwargs: Any) -> PyyamlConverter:
    kwargs["unstruct_collection_overrides"] = {
        FrozenSetSubscriptable: list,
        **kwargs.get("unstruct_collection_overrides", {}),
    }
    res = PyyamlConverter(*args, **kwargs)
    configure_converter(res)

    return res
