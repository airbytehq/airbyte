#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import dataclasses
import pprint
from dataclasses import dataclass, fields
from typing import Any, Mapping, Type, Union

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders import JsonDecoder
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.paginators import LimitPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import PageIncrement
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers import SingleSlice
from dataclasses_jsonschema import JsonSchemaMixin
from jsonschema.validators import validate


@dataclass
class Interface(JsonSchemaMixin):
    """This is an interface"""


count = 0


@dataclass
class ChildInterfaceString(Interface, JsonSchemaMixin):
    """ConcreteType1"""

    child_field: str


@dataclass
class ChildInt(Interface):
    """ConcreteType2"""

    int_field: int


@dataclass
class ConcreteClass(JsonSchemaMixin):
    number: int = 15


@dataclass
class SomeOtherClass(JsonSchemaMixin):
    """Outerobject containing interface"""

    f: int

    g: ConcreteClass
    h: Interface


def test_json_schema():
    # copy the top level class (probably DeclarativeSource?)
    copy_cls = type("Copymixin", SomeOtherClass.__bases__, dict(SomeOtherClass.__dict__))

    class_fields = fields(copy_cls)
    # iterate over the fields
    for field in class_fields:
        t = field.type
        subsclasses = t.__subclasses__()
        # Only replace the type if there are subclasses and t is not in builtins
        if subsclasses and t.__module__ != "builtins":
            # replace the type with union of subclasses
            field.type = Union[tuple(subsclasses)]
            copy_cls.__dict__["__annotations__"][field.name] = Union[tuple(subsclasses)]

    json_schema = copy_cls.json_schema()

    pprint.pprint(json_schema)
    assert "anyOf" in json_schema["properties"]["h"]


# make this a mixin
def test_pagination_strategy():
    # conc = LimitPaginator(
    #     page_size=100,
    #     limit_option=RequestOption
    # )
    # og_bases = LimitPaginator.__bases__
    # og_dict = dict(LimitPaginator.__dict__)
    # copy_name = LimitPaginator.__name__ + "Copy"
    # copy_cls = type(LimitPaginator.__name__, og_bases, og_dict)
    # class_fields = fields(copy_cls)
    # for field in class_fields:
    #     some_field = field.type
    #     module = some_field.__module__
    #     if module != "builtins" and module != "typing":
    #         subclasses = some_field.__subclasses__()
    #         if subclasses:
    #             copy_cls.__annotations__[field.name] = Union[tuple(subclasses)]
    #             print(subclasses)
    copy_cls = replace_unions(LimitPaginator, dict())

    schema = copy_cls.json_schema()
    print(schema)

    # Test validate

    paginator = LimitPaginator(
        page_size=100,
        limit_option=RequestOption(inject_into=RequestOptionType.request_parameter, field_name="from", options={}),
        page_token_option=RequestOption(inject_into=RequestOptionType.request_parameter, field_name="from", options={}),
        pagination_strategy=PageIncrement(50, {}),
        # pagination_strategy=MinMaxDatetime(datetime="0202020", options={}),
        decoder=JsonDecoder(
            tech_optional=SingleSlice({}),
            options={},
        ),
        config={},
        url_base="https://sample.api/v1/",
        options={},
    )

    validate(paginator.to_dict(), schema)

    print(DeclarativeStream.json_schema())


def test_full_schema_print():
    unexpanded_schema = DeclarativeStream.json_schema()

    unionized_class = replace_unions(DeclarativeStream, dict())
    unionized_schema = unionized_class.json_schema()

    print(unexpanded_schema)
    print(unionized_schema)


def test_bespoke():
    schema = DeclarativeStream.get_schema()
    print(schema)


def replace_unions(current_class: Type, visited: Mapping[Type, Any]) -> Type:
    if current_class in visited:
        return current_class
    visited[current_class] = True

    og_bases = current_class.__bases__
    og_dict = dict(current_class.__dict__)
    copy_cls = type(current_class.__name__, og_bases, og_dict)
    if not dataclasses.is_dataclass(copy_cls):
        return copy_cls
    class_fields = fields(copy_cls)
    for field in class_fields:
        some_field = field.type
        module = some_field.__module__
        if module != "builtins" and module != "typing":
            subclasses = some_field.__subclasses__()
            if subclasses:

                for subclass in subclasses:
                    replace_unions(subclass, visited)
                    print(subclasses)
                copy_cls.__annotations__[field.name] = Union[tuple(subclasses)]
    return copy_cls
