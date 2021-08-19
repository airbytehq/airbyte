#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from decimal import Decimal
from typing import Any, Dict, Optional, Type

import pydantic
from pydantic import BaseModel
from pydantic.typing import resolve_annotations


class AllOptional(pydantic.main.ModelMetaclass):
    """
    Metaclass for marking all Pydantic model fields as Optional
    Here is exmaple of declaring model using this metaclasslike:
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
        Iterate through fields and wrap then with typing.Optional type.
        """
        annotations = resolve_annotations(namespaces.get("__annotations__", {}), namespaces.get("__module__", None))
        for base in bases:
            annotations = {**annotations, **getattr(base, "__annotations__", {})}
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


class CatalogModel(BaseModel, metaclass=AllOptional):
    class Config:
        arbitrary_types_allowed = True

        @classmethod
        def schema_extra(cls, schema: Dict[str, Any], model: Type["BaseModel"]) -> None:
            schema.pop("title", None)
            schema.pop("description", None)
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
