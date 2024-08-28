#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Optional, Type

from airbyte_cdk.sources.utils.schema_helpers import expand_refs
from pydantic.v1 import BaseModel, Extra
from pydantic.v1.main import ModelMetaclass
from pydantic.v1.typing import resolve_annotations


class AllOptional(ModelMetaclass):
    """
    Metaclass for marking all Pydantic model fields as Optional
    Here is example of declaring model using this metaclass like:
    '''
            class MyModel(BaseModel, metaclass=AllOptional):
                a: str
                b: str
    '''
    it is an equivalent of:
    '''
            class MyModel(BaseModel):
                a: Optional[str]
                b: Optional[str]
    '''
    It would make code more clear and eliminate a lot of manual work.
    """

    def __new__(mcs, name, bases, namespaces, **kwargs):  # type: ignore[no-untyped-def] # super().__new__ is also untyped
        """
        Iterate through fields and wrap then with typing.Optional type.
        """
        annotations = resolve_annotations(namespaces.get("__annotations__", {}), namespaces.get("__module__", None))
        for base in bases:
            annotations = {**annotations, **getattr(base, "__annotations__", {})}
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]  # type: ignore[assignment]
        namespaces["__annotations__"] = annotations
        return super().__new__(mcs, name, bases, namespaces, **kwargs)


class BaseSchemaModel(BaseModel):
    """
    Base class for all schema models. It has some extra schema postprocessing.
    Can be used in combination with AllOptional metaclass
    """

    class Config:
        extra = Extra.allow

        @classmethod
        def schema_extra(cls, schema: Dict[str, Any], model: Type[BaseModel]) -> None:
            """Modify generated jsonschema, remove "title", "description" and "required" fields.

            Pydantic doesn't treat Union[None, Any] type correctly when generate jsonschema,
            so we can't set field as nullable (i.e. field that can have either null and non-null values),
            We generate this jsonschema value manually.

            :param schema: generated jsonschema
            :param model:
            """
            schema.pop("title", None)
            schema.pop("description", None)
            schema.pop("required", None)
            for name, prop in schema.get("properties", {}).items():
                prop.pop("title", None)
                prop.pop("description", None)
                allow_none = model.__fields__[name].allow_none
                if allow_none:
                    if "type" in prop:
                        prop["type"] = ["null", prop["type"]]
                    elif "$ref" in prop:
                        ref = prop.pop("$ref")
                        prop["oneOf"] = [{"type": "null"}, {"$ref": ref}]

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """We're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema(*args, **kwargs)
        expand_refs(schema)
        return schema  # type: ignore[no-any-return]
