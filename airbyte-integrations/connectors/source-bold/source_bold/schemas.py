from datetime import datetime
from typing import Any, Dict, List, MutableMapping, Optional

from jsonschema import RefResolver
from pydantic import BaseModel, Extra


class BaseSchemaModel(BaseModel):
    class Config:
        extra = Extra.allow

        @staticmethod
        def schema_extra(schema: MutableMapping[str, Any], model) -> None:
            # Pydantic adds a title to each attribute, that is not needed, so we manually drop them.
            # Also pydantic does not add a "null" option to a field marked as optional,
            # so we add this functionality manually. Same for "$ref"
            schema.pop("title", None)
            for name, prop in schema.get("properties", {}).items():
                prop.pop("title", None)
                allow_none = model.__fields__[name].allow_none
                if allow_none:
                    if "type" in prop:
                        prop["type"] = ["null", prop["type"]]
                    elif "$ref" in prop:
                        ref = prop.pop("$ref")
                        prop["oneOf"] = [{"type": "null"}, {"$ref": ref}]

    @classmethod
    def _expand_refs(cls, schema: Any, ref_resolver: Optional[RefResolver] = None) -> None:
        """Iterate over schema and replace all occurrences of $ref with their definitions. Recursive.

        :param schema: schema that will be patched
        :param ref_resolver: resolver to get definition from $ref, if None pass it will be instantiated
        """
        ref_resolver = ref_resolver or RefResolver.from_schema(schema)

        if isinstance(schema, MutableMapping):
            if "$ref" in schema:
                ref_url = schema.pop("$ref")
                _, definition = ref_resolver.resolve(ref_url)
                cls._expand_refs(definition, ref_resolver=ref_resolver)  # expand refs in definitions as well
                schema.update(definition)
            else:
                for key, value in schema.items():
                    cls._expand_refs(value, ref_resolver=ref_resolver)
        elif isinstance(schema, List):
            for value in schema:
                cls._expand_refs(value, ref_resolver=ref_resolver)

    @classmethod
    def schema(cls, **kwargs) -> Dict[str, Any]:
        """We're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema(**kwargs)
        cls._expand_refs(schema)  # UI and destination doesn't support $ref's
        schema.pop("definitions", None)  # remove definitions created by $ref
        return schema

    object: str


class Address(BaseSchemaModel):
    first_name: str
    last_name: str
    bold_customer_id: int
    address_type: Optional[str]
    city: Optional[str]
    country: Optional[str]
    address_source: Optional[str]


class Customer(BaseSchemaModel):
    id: int
    first_name: str
    last_name: str
    email: str
    updated_at: datetime
    created_at: datetime
    platform_type: str
    list_type: str
    folder: Optional[str]
    address: Optional[list[Address]]


class Category(BaseSchemaModel):
    id: int
    name: str
    updated_at: datetime
    created_at: datetime

class Image(BaseSchemaModel):
    id: int
    src: str
    updated_at: datetime
    created_at: datetime


class Variant(BaseSchemaModel):
    id: int
    name: str
    sku: str
    weight_unit: str
    image_url: str
    updated_at: datetime
    created_at: datetime
    price: float
    cost: float


class Product(BaseSchemaModel):
    id: int
    name: str
    handle: str
    description: str
    type: str
    vendor: str
    updated_at: datetime
    created_at: datetime
    url: str
    tags: str
    categories: Optional[list[Category]]
    images: Optional[list[Image]]
    variants: Optional[list[Variant]]

