#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from enum import Enum
from functools import total_ordering
from typing import Any, Dict, List, Literal, Mapping, Union

from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, SchemaInferenceError

type_widths = {str: 0}

JsonSchemaSupportedType = Union[List, Literal["string"], str]
SchemaType = Dict[str, Dict[str, JsonSchemaSupportedType]]


@total_ordering
class ComparableType(Enum):
    NULL = 0
    BOOLEAN = 1
    INTEGER = 2
    NUMBER = 3
    STRING = 4
    OBJECT = 5

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        else:
            return NotImplemented


def get_comparable_type(value: Any) -> ComparableType:
    if value == "null":
        return ComparableType.NULL
    if value == "boolean":
        return ComparableType.BOOLEAN
    if value == "integer":
        return ComparableType.INTEGER
    if value == "number":
        return ComparableType.NUMBER
    if value == "string":
        return ComparableType.STRING
    if value == "object":
        return ComparableType.OBJECT


def get_inferred_type(value: Any) -> ComparableType:
    if value is None:
        return ComparableType.NULL
    if isinstance(value, bool):
        return ComparableType.BOOLEAN
    if isinstance(value, int):
        return ComparableType.INTEGER
    if isinstance(value, float):
        return ComparableType.NUMBER
    if isinstance(value, str):
        return ComparableType.STRING
    if isinstance(value, dict):
        return ComparableType.OBJECT


def merge_schemas(schema1: SchemaType, schema2: SchemaType) -> SchemaType:
    """
    Returns a new dictionary that contains schema1 and schema2.

    Schemas are merged as follows
    - If a key is in one schema but not the other, add it to the base schema with its existing type.
    - If a key is in both schemas but with different types, use the wider type.
    - If the type is a list in one schema but a different type of element in the other schema, raise an exception.
    - If the type is an object in both schemas but the objects are different raise an exception.
    - If the type is an object in one schema but not in the other schema, raise an exception.

    In other words, we support merging
    - any atomic type with any other atomic type (choose the wider of the two)
    - list with list (union)
    and nothing else.
    """
    for k, t in list(schema1.items()) + list(schema2.items()):
        if not isinstance(t, dict) or not _is_valid_type(t.get("type")):
            raise SchemaInferenceError(FileBasedSourceError.UNRECOGNIZED_TYPE, key=k, type=t)

    merged_schema = deepcopy(schema1)
    for k2, t2 in schema2.items():
        t1 = merged_schema.get(k2)
        if t1 is None:
            merged_schema[k2] = t2
        elif t1 == t2:
            continue
        else:
            merged_schema[k2] = _choose_wider_type(k2, t1, t2)

    return merged_schema


def _is_valid_type(t: JsonSchemaSupportedType) -> bool:
    return t == "array" or get_comparable_type(t) is not None


def _choose_wider_type(key: str, t1: Dict[str, Any], t2: Dict[str, Any]) -> Dict[str, Any]:
    if (t1["type"] == "array" or t2["type"] == "array") and t1 != t2:
        raise SchemaInferenceError(
            FileBasedSourceError.SCHEMA_INFERENCE_ERROR,
            details="Cannot merge schema for unequal array types.",
            key=key,
            detected_types=f"{t1},{t2}",
        )
    elif (t1["type"] == "object" or t2["type"] == "object") and t1 != t2:
        raise SchemaInferenceError(
            FileBasedSourceError.SCHEMA_INFERENCE_ERROR,
            details="Cannot merge schema for unequal object types.",
            key=key,
            detected_types=f"{t1},{t2}",
        )
    else:
        comparable_t1 = get_comparable_type(t1["type"])
        comparable_t2 = get_comparable_type(t2["type"])
        if not comparable_t1 and comparable_t2:
            raise SchemaInferenceError(FileBasedSourceError.UNRECOGNIZED_TYPE, key=key, detected_types=f"{t1},{t2}")
        return max([t1, t2], key=lambda x: ComparableType(get_comparable_type(x["type"])))


def is_equal_or_narrower_type(value: Any, expected_type: str):
    if isinstance(value, list):
        # We do not compare lists directly; the individual items are compared.
        # If we hit this condition, it means that the expected type is not
        # compatible with the inferred type.
        return False

    inferred_type = ComparableType(get_inferred_type(value))

    if inferred_type is None:
        return False

    return ComparableType(inferred_type) <= ComparableType(get_comparable_type(expected_type))


def conforms_to_schema(record: Mapping[str, Any], schema: Mapping[str, str]) -> bool:
    """
    Return true iff the record conforms to the supplied schema.

    The record conforms to the supplied schema iff:
    - All columns in the record are in the schema.
    - For every column in the record, that column's type is equal to or narrower than the same column's
      type in the schema.
    """
    schema_columns = set(schema.get("properties", {}).keys())
    record_columns = set(record.keys())

    if not record_columns.issubset(schema_columns):
        return False

    for column, definition in schema.get("properties", {}).items():
        expected_type = definition.get("type")
        value = record.get(column)

        if value is not None:
            if expected_type == "object":
                return isinstance(value, dict)
            elif expected_type == "array":
                if not isinstance(value, list):
                    return False
                array_type = definition.get("items", {}).get("type")
                if not all(is_equal_or_narrower_type(v, array_type) for v in value):
                    return False
            elif not is_equal_or_narrower_type(value, expected_type):
                return False

    return True


def type_mapping_to_jsonschema(type_mapping: Mapping[str, Any]) -> Mapping[str, str]:
    """
    Return the user input schema (type mapping), transformed to JSON Schema format.
    """
    ...
