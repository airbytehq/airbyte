#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import dataclasses
import inspect
from dataclasses import dataclass, fields, make_dataclass
from typing import Union, get_args, get_origin, get_type_hints

from airbyte_cdk.sources.declarative.cdk_jsonschema import DEFAULT_SCHEMA_TYPE, JsonDict, JsonSchemaMixin, SchemaType

_FIELDS = "__dataclass_fields__"


def get_constructor_params(cls):
    parameters = inspect.signature(cls.__init__).parameters
    print(f"parameters: {parameters}")
    params = {}
    for parameter_name, param_type in parameters.items():
        print(f"param: {parameter_name}")
        type_hints = get_type_hints(cls.__init__, parameter_name)
        interface = type_hints.get(parameter_name)
        while True:
            origin = get_origin(interface)
            if origin:
                # Unnest types until we reach the raw type
                # List[T] -> T
                # Optional[List[T]] -> T
                args = get_args(interface)
                interface = args[0]
            else:
                break
        params[parameter_name] = interface
    return params


@dataclass
class Interface(JsonSchemaMixin):
    """This is an interface"""


class InterfaceNotDataClass(JsonSchemaMixin):
    pass


class ChildA(InterfaceNotDataClass):
    def __init__(self, i: int = 15):
        self._i = i


class ChildB(InterfaceNotDataClass):
    def __init__(self, a: str):
        self._a = a


class WrapperClass(JsonSchemaMixin):
    def __init__(self, interface: InterfaceNotDataClass):
        self._interface = interface


count = 0


@dataclass
class ChildInterfaceString(Interface, JsonSchemaMixin):
    """ConcreteType1"""

    child_field: str


@dataclass
class ChildInt(Interface):
    """ConcreteType2"""

    int_field: int


#
#    @classmethod
#    def json_schema(
#            cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
#    ) -> JsonDict:
#        return JsonSchemaMixin.json_schema(cls)


InterfaceTypeHint = Union[tuple(Interface.__subclasses__())]


@dataclass
class ConcreteClass(JsonSchemaMixin):
    def __init__(self, number: int = 15):
        self._n = number


@dataclass
class SomeOtherClassWithFields(JsonSchemaMixin):
    """Outerobject containing interface"""

    def __init__(self):

        f: int

    g: ConcreteClass
    h: Interface


@dataclass
class SomeOtherClass:
    """Outerobject containing interface"""

    # f: int

    # g: ConcreteClass
    # h: Interface
    # _f: int

    def __init__(self, f: int, g: ConcreteClass, h: Interface):
        pass

    @classmethod
    def _json_schema(
        cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
    ) -> JsonDict:
        # Copy class so we don't modify the fields directly
        # copy_cls = type('CopyOfB', cls.__bases__, dict(cls.__dict__))
        copy_mixin = type("Copymixin", cls.__bases__, dict(cls.__dict__))

        class_fields = fields(cls)
        print(cls.__dict__)

        for field in class_fields:
            t = field.type
            if "__subclasses__" in t.__dict__:
                subsclasses = t.__subclasses__()
                if subsclasses and not t.__module__ == "builtins":
                    field.type = Union[tuple(subsclasses)]
                    copy_mixin["__annotations__"][field.name] = Union[tuple(subsclasses)]
        # setattr(copy_mixin, "__dataclass_fields__", cls.__dict__["__dataclass_fields__"])

        copy_mixin.__name__ = cls.__name__
        copy_mixin.__doc__ = cls.__doc__

        # setattr(copy_mixin, "json_schema", InterfaceMixin.json_schema)

        schema = copy_mixin.json_schema(embeddable=True)
        return schema


#    h: InterfaceTypeHint


def test_json_schema():
    import inspect

    # copy the top level class
    copy_cls = type("Copymixin", SomeOtherClass.__bases__, dict(SomeOtherClass.__dict__))

    class_fields = fields(copy_cls)
    # iterate over the fields

    parameters = inspect.signature(SomeOtherClass.__init__).parameters
    print(f"cls_copy: {copy_cls.__dict__}")

    fields_from_constructor = []
    for name, param in parameters.items():
        if name == "self":
            continue
        print(f"param: {param}")
        type_hint = get_type_hints(SomeOtherClass.__init__)[name]
        print(f"type_hint: {type_hint}")
        subclasses = type_hint.__subclasses__()
        print(f"subclasses for {name}: {subclasses}")
        f = dataclasses.field()
        f.name = name
        f.type = type_hint
        copy_cls.__dict__[_FIELDS].clear()
        copy_cls.__dict__[_FIELDS][name] = f
        # copy_cls.__dict__["__annotations__"][field.name] = type_hint
        fields_from_constructor.append((name, type_hint))
        # if subclasses and type_hint.__module__ != "builtins":
        # replace the type with union of subclasses
        # field.type = Union[tuple(subsclasses)]
        # copy_cls.__dict__["__annotations__"][field.name] = Union[tuple(subsclasses)]
    print(f"cls_copy: {copy_cls.__dict__}")
    print(f"withfields: {SomeOtherClassWithFields.__dict__}")

    print(f"class_fields: {fields_from_constructor}")

    made_dataclass = make_dataclass(
        cls_name="SomeOtherClassCopy",
        fields=fields_from_constructor,
        bases=(JsonSchemaMixin,),
    )
    print(made_dataclass.__dict__)

    for field in class_fields:
        t = field.type
        subsclasses = t.__subclasses__()
        # Only replace the type if there are subclasses and t is not in builtins
        if subsclasses and t.__module__ != "builtins":
            print(f"subclasses for {field.name}: {subsclasses}")
            # replace the type with union of subclasses
            field.type = Union[tuple(subsclasses)]
            copy_cls.__dict__["__annotations__"][field.name] = Union[tuple(subsclasses)]

    json_schema = made_dataclass.json_schema()
    # json_schema = get_json_schema(SomeOtherClass)
    import pprint

    print("schema:")
    pprint.pprint(json_schema)
    # definitions = json_schema["definitions"]
    # for c, v in definitions.items():
    #    print(f"c: {c}")
    #    properties = v["properties"]
    #    print(f"v: {v}")
    #    if not properties:
    #        all_json_schemas = Interface.all_json_schemas()
    #        print(f"all_json_schemas for {c}: {all_json_schemas}")
    # print(json_schema)
    # pprint.pprint(Interface.all_json_schemas())

    # print()
    # print()
    # json_schema = PydanticSomeOtherClass.schema_json()
    # pprint.pprint(json_schema)

    c = ConcreteClass(number=20)
    print(f"c._number: {c._n}")
    assert False
