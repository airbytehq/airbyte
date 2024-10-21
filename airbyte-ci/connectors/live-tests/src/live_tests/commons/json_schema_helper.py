#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from enum import Enum
from functools import reduce, total_ordering
from typing import Any, Dict, List, Mapping, Optional, Set, Text, Union

import dpath.util
import pendulum
from jsonref import JsonRef


class CatalogField:
    """Field class to represent cursor/pk fields.
    It eases the read of values from records according to schema definition.
    """

    def __init__(self, schema: Mapping[str, Any], path: List[str]):
        self.schema = schema
        self.path = path
        self.formats = self._detect_formats()

    def _detect_formats(self) -> Set[str]:
        """Extract set of formats/types for this field"""
        format_ = []
        try:
            format_ = self.schema.get("format", self.schema["type"])
            if not isinstance(format_, List):
                format_ = [format_]
        except KeyError:
            pass
        return set(format_)

    def _parse_value(self, value: Any) -> Any:
        """Do actual parsing of the serialized value"""
        if self.formats.intersection({"datetime", "date-time", "date"}):
            if value is None and "null" not in self.formats:
                raise ValueError(f"Invalid field format. Value: {value}. Format: {self.formats}")
            # handle beautiful MySQL datetime, i.e. NULL datetime
            if value.startswith("0000-00-00"):
                value = value.replace("0000-00-00", "0001-01-01")
            return pendulum.parse(value)
        return value

    def parse(self, record: Mapping[str, Any], path: Optional[List[Union[int, str]]] = None) -> Any:
        """Extract field value from the record and cast it to native type"""
        path = path or self.path
        value = reduce(lambda data, key: data[key], path, record)
        return self._parse_value(value)


@total_ordering
class ComparableType(Enum):
    NULL = 0
    BOOLEAN = 1
    INTEGER = 2
    NUMBER = 3
    STRING = 4
    OBJECT = 5

    def __lt__(self, other: Any) -> bool:
        if self.__class__ is other.__class__:
            return self.value < other.value  # type: ignore
        else:
            return NotImplemented


class JsonSchemaHelper:
    """Helper class to simplify schema validation and read of records according to their schema."""

    def __init__(self, schema):
        self._schema = schema

    def get_ref(self, path: str) -> Any:
        """Resolve reference

        :param path: reference (#/definitions/SomeClass, etc)
        :return: part of schema that is definition of the reference
        :raises KeyError: in case path can't be followed
        """
        node = self._schema
        for segment in path.split("/")[1:]:
            node = node[segment]
        return node

    def get_property(self, path: List[str]) -> Mapping[str, Any]:
        """Get any part of schema according to provided path, resolves $refs if necessary

        schema = {
                "properties": {
                    "field1": {
                        "properties": {
                            "nested_field": {
                                <inner_object>
                            }
                        }
                    },
                    "field2": ...
                }
            }

        helper = JsonSchemaHelper(schema)
        helper.get_property(["field1", "nested_field"]) == <inner_object>

        :param path: list of fields in the order of navigation
        :return: discovered part of schema
        :raises KeyError: in case path can't be followed
        """
        node = self._schema
        for segment in path:
            if "$ref" in node:
                node = self.get_ref(node["$ref"])
            node = node["properties"][segment]
        return node

    def field(self, path: List[str]) -> CatalogField:
        """Get schema property and wrap it into CatalogField.

        CatalogField is a helper to ease the read of values from records according to schema definition.

        :param path: list of fields in the order of navigation
        :return: discovered part of schema wrapped in CatalogField
        :raises KeyError: in case path can't be followed
        """
        return CatalogField(schema=self.get_property(path), path=path)

    def get_node(self, path: List[Union[str, int]]) -> Any:
        """Return part of schema by specified path

        :param path: list of fields in the order of navigation
        """

        node = self._schema
        for segment in path:
            if "$ref" in node:
                node = self.get_ref(node["$ref"])
            node = node[segment]
        return node

    def get_parent_path(self, path: str, separator="/") -> Any:
        """
        Returns the parent path of the supplied path
        """
        absolute_path = f"{separator}{path}" if not path.startswith(separator) else path
        parent_path, _ = absolute_path.rsplit(sep=separator, maxsplit=1)
        return parent_path

    def get_parent(self, path: str, separator="/") -> Any:
        """
        Returns the parent dict of a given path within the `obj` dict
        """
        parent_path = self.get_parent_path(path, separator=separator)
        if parent_path == "":
            return self._schema
        return dpath.util.get(self._schema, parent_path, separator=separator)

    def find_nodes(self, keys: List[str]) -> List[List[Union[str, int]]]:
        """Find all paths that lead to nodes with the specified keys.

        :param keys: list of keys
        :return: list of json object paths
        """
        variant_paths = []

        def traverse_schema(_schema: Union[Dict[Text, Any], List], path=None):
            path = path or []
            if path and path[-1] in keys:
                variant_paths.append(path)
            if isinstance(_schema, dict):
                for item in _schema:
                    traverse_schema(_schema[item], [*path, item])
            elif isinstance(_schema, list):
                for i, item in enumerate(_schema):
                    traverse_schema(_schema[i], [*path, i])

        traverse_schema(self._schema)
        return variant_paths


def get_object_structure(obj: dict) -> List[str]:
    """
    Traverse through object structure and compose a list of property keys including nested one.
    This list reflects object's structure with list of all obj property key
    paths. In case if object is nested inside array we assume that it has same
    structure as first element.
    :param obj: data object to get its structure
    :returns list of object property keys paths
    """
    paths = []

    def _traverse_obj_and_get_path(obj, path=""):
        if path:
            paths.append(path)
        if isinstance(obj, dict):
            return {k: _traverse_obj_and_get_path(v, path + "/" + k) for k, v in obj.items()}
        elif isinstance(obj, list) and len(obj) > 0:
            return [_traverse_obj_and_get_path(obj[0], path + "/[]")]

    _traverse_obj_and_get_path(obj)

    return paths


def get_expected_schema_structure(schema: dict, annotate_one_of: bool = False) -> List[str]:
    """
    Traverse through json schema and compose list of property keys that object expected to have.
    :param annotate_one_of: Generate one_of index in path
    :param schema: jsonschema to get expected paths
    :returns list of object property keys paths
    """
    paths = []
    if "$ref" in schema:
        """
        JsonRef doesnt work correctly with schemas that has refenreces in root e.g.
        {
            "$ref": "#/definitions/ref"
            "definitions": {
                "ref": ...
            }
        }
        Considering this schema already processed by resolver so it should
        contain only references to definitions section, replace root reference
        manually before processing it with JsonRef library.
        """
        ref = schema["$ref"].split("/")[-1]
        schema.update(schema["definitions"][ref])
        schema.pop("$ref")
    # Resolve all references to simplify schema processing.
    schema = JsonRef.replace_refs(schema)

    def _scan_schema(subschema, path=""):
        if "oneOf" in subschema or "anyOf" in subschema:
            if annotate_one_of:
                return [
                    _scan_schema({"type": "object", **s}, path + f"({num})")
                    for num, s in enumerate(subschema.get("oneOf") or subschema.get("anyOf"))
                ]
            return [_scan_schema({"type": "object", **s}, path) for s in subschema.get("oneOf") or subschema.get("anyOf")]
        schema_type = subschema.get("type", ["object", "null"])
        if not isinstance(schema_type, list):
            schema_type = [schema_type]
        if "object" in schema_type:
            props = subschema.get("properties")
            if not props:
                # Handle objects with arbitrary properties:
                # {"type": "object", "additionalProperties": {"type": "string"}}
                if path:
                    paths.append(path)
                return
            return {k: _scan_schema(v, path + "/" + k) for k, v in props.items()}
        elif "array" in schema_type:
            items = subschema.get("items", {})
            return [_scan_schema(items, path + "/[]")]
        paths.append(path)

    _scan_schema(schema)
    return paths


def flatten_tuples(to_flatten):
    """Flatten a tuple of tuples into a single tuple."""
    types = set()

    if not isinstance(to_flatten, tuple):
        to_flatten = (to_flatten,)
    for thing in to_flatten:
        if isinstance(thing, tuple):
            types.update(flatten_tuples(thing))
        else:
            types.add(thing)
    return tuple(types)


def get_paths_in_connector_config(schema: dict) -> List[str]:
    """
    Traverse through the provided schema's values and extract the path_in_connector_config paths
    :param properties: jsonschema containing values which may have path_in_connector_config attributes
    :returns list of path_in_connector_config paths
    """
    return ["/" + "/".join(value["path_in_connector_config"]) for value in schema.values()]


def conforms_to_schema(record: Mapping[str, Any], schema: Mapping[str, Any]) -> bool:
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
            if isinstance(expected_type, list):
                return any(_is_equal_or_narrower_type(value, e) for e in expected_type)
            elif expected_type == "object":
                return isinstance(value, dict)
            elif expected_type == "array":
                if not isinstance(value, list):
                    return False
                array_type = definition.get("items", {}).get("type")
                if not all(_is_equal_or_narrower_type(v, array_type) for v in value):
                    return False
            elif not _is_equal_or_narrower_type(value, expected_type):
                return False

    return True


def _is_equal_or_narrower_type(value: Any, expected_type: str) -> bool:
    if isinstance(value, list):
        # We do not compare lists directly; the individual items are compared.
        # If we hit this condition, it means that the expected type is not
        # compatible with the inferred type.
        return False

    inferred_type = ComparableType(_get_inferred_type(value))

    if inferred_type is None:
        return False

    return ComparableType(inferred_type) <= ComparableType(_get_comparable_type(expected_type))


def _get_inferred_type(value: Any) -> Optional[ComparableType]:
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
    else:
        return None


def _get_comparable_type(value: Any) -> Optional[ComparableType]:
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
    else:
        return None
