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
from typing import Any, Iterable, List, Mapping, MutableMapping


class Transformer:
    """
    Transform class was implemented according to issue #4841
    Shopify API returns price fields as a string and it should be converted to the number
    Some records fields contain objects and arrays, which contain price fields.
    Those price fields should be transformed too.
    This solution designed to convert string into number, but in future can be modified for general purpose
    Correct types placed in schemes
    Transformer iterates over records, compare values type with schema type and transform if it's needed

    Methods
    -------
    _transform_array(self, array: List[Any], item_properties: Mapping[str, Any])
        Some fields type is array. Items inside array contain price fields, which should be transformed
        This method iterate over items in array, compare schema types and convert if necessary
    """

    def __init__(self, schema: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self._schema = schema

    @staticmethod
    def _get_json_types(value_type) -> List[str]:
        json_types = {
            str: ["string"],
            int: ["integer", "number"],
            float: ["number"],
            dict: ["object"],
            list: ["array"],
            bool: ["boolean"],
            type(None): [
                "null",
            ],
        }
        return json_types.get(value_type)

    @staticmethod
    def _types_from_schema(properties: Mapping[str, Any]) -> str:
        schema_types = properties.get("type", [])
        if not isinstance(schema_types, list):
            schema_types = [
                schema_types,
            ]
        return schema_types

    @staticmethod
    def _first_non_null_type(schema_types: List[str]) -> str:
        not_null_types = schema_types.copy()
        if "null" in not_null_types:
            not_null_types.remove("null")
        return not_null_types[0]

    @staticmethod
    def _transform_number(value: Any):
        return Decimal(value)

    def _transform_array(self, array: List[Any], item_properties: Mapping[str, Any]):
        # iterate over items in array, compare schema types and convert if necessary.
        item_types = self._types_from_schema(item_properties)
        if item_types:
            schema_type = self._first_non_null_type(item_types)
            nested_properties = item_properties.get("properties", {})
            item_properties = item_properties.get("items", {})
            for item in array:
                if schema_type == "object":
                    self._transform_object(item, nested_properties)
                if schema_type == "array":
                    self._transform_array(item, item_properties)

    def _transform_object(self, transform_object: MutableMapping[str, Any], properties: Mapping[str, Any]):
        # compare schema types and convert if necessary.
        for object_property, value in transform_object.items():
            if value is None:
                continue
            if object_property in properties:
                object_properties = properties.get(object_property)
                schema_types = self._types_from_schema(object_properties)
                if not schema_types:
                    continue
                value_json_types = self._get_json_types(type(value))
                schema_type = self._first_non_null_type(schema_types)
                if not any(value_json_type in schema_types for value_json_type in value_json_types):
                    if schema_type == "number":
                        transform_object[object_property] = self._transform_number(value)
                if schema_type == "object":
                    nested_properties = object_properties.get("properties", {})
                    self._transform_object(value, nested_properties)
                if schema_type == "array":
                    item_properties = object_properties.get("items", {})
                    self._transform_array(value, item_properties)

    def transform(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping]:
        # Shopify API returns array of objects
        # It's need to compare records values with schemas
        properties = self._schema.get("properties", {})
        self._transform_object(record, properties)
        return record
