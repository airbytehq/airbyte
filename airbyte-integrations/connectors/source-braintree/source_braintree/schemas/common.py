#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Any, Dict, Optional, Type, ClassVar

from pydantic import BaseModel, ConfigDict, create_model, field_serializer
from pydantic.fields import FieldInfo
from pydantic._internal._model_construction import ModelMetaclass

from airbyte_cdk.sources.utils.schema_helpers import expand_refs


class AllOptional(ModelMetaclass):
    """
    Metaclass for marking all Pydantic model fields as Optional
    Here is example of declaring model using this metaclass:
    '''
            class MyModel(BaseModel, metaclass=AllOptional):
                a: str
                b: str
    '''
    Its equivalent of:
    '''
            class MyModel(BaseModel):
                a: Optional[str]
                b: Optional[str]
    '''
    It would make code more clear and eliminate a lot of manual work.
    """

    def __new__(self, name, bases, namespaces, **kwargs):
        """
        Iterate through fields and wrap them with typing.Optional type.
        """
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations = {**annotations, **getattr(base, "__annotations__", {})}
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


def _schema_extra(schema: Dict[str, Any], model: Type["BaseModel"]) -> None:
    schema.pop("title", None)
    schema.pop("description", None)
    for name, prop in schema.get("properties", {}).items():
        prop.pop("title", None)
        prop.pop("description", None)
        field_info = model.model_fields.get(name)
        if field_info and not field_info.is_required:
            if "type" in prop:
                prop["type"] = ["null", prop["type"]]
            elif "$ref" in prop:
                ref = prop.pop("$ref")
                prop["oneOf"] = [{"type": "null"}, {"$ref": ref}]


class CatalogModel(BaseModel, metaclass=AllOptional):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra=lambda schema, model: _schema_extra(schema, model),
    )

    @classmethod
    def model_json_schema(cls, **kwargs) -> Dict[str, Any]:
        schema = super().model_json_schema(**kwargs)
        expand_refs(schema)
        return schema


class AddOn(CatalogModel):
    amount: Decimal
    current_billing_cycle: Optional[Decimal]
    description: str
    id: str
    kind: str
    name: str
    never_expires: bool
    number_of_billing_cycles: Optional[Decimal]
    quantity: Optional[Decimal]
