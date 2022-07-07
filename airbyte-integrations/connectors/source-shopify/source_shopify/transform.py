#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Any, Iterable, List, Mapping, MutableMapping


class DataTypeEnforcer:
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
    transform(self, field: Any, schema: Mapping[str, Any] = None)
        Accepts field of Any type and schema, compere type of field and type in schema, convert if necessary
    """

    def __init__(self, schema: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self._schema = schema

    @staticmethod
    def _get_json_types(value_type: Any) -> List[str]:
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

    @staticmethod
    def _transform_string(value: Any):
        return str(value)

    def _transform_array(self, array: List[Any], item_properties: Mapping[str, Any]):
        # iterate over items in array, compare schema types and convert if necessary.
        for index, record in enumerate(array):
            array[index] = self.transform(record, item_properties)
        return array

    def _transform_object(self, record: MutableMapping[str, Any], properties: Mapping[str, Any]):
        # compare schema types and convert if necessary.
        for object_property, value in record.items():
            if value is None:
                continue
            if object_property in properties:
                object_properties = properties.get(object_property) or {}
                record[object_property] = self.transform(value, object_properties)
        return record

    def transform(self, field: Any, schema: Mapping[str, Any] = None) -> Iterable[MutableMapping]:
        schema = schema if schema is not None else self._schema
        # get available types from schema
        schema_types = self._types_from_schema(schema)
        if schema_types and field is not None:
            # if types presented in schema and field is not None, get available JSON Schema types for field
            # and not null types from schema, check if field JSON Schema types presented in schema
            field_json_types = self._get_json_types(type(field))
            schema_type = self._first_non_null_type(schema_types)
            if not any(field_json_type in schema_types for field_json_type in field_json_types):
                if schema_type == "number":
                    return self._transform_number(field)
                if schema_type == "string":
                    return self._transform_string(field)
            if schema_type == "object":
                properties = schema.get("properties", {})
                return self._transform_object(field, properties)
            if schema_type == "array":
                properties = schema.get("items", {})
                return self._transform_array(field, properties)
        return field
