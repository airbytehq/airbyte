#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from functools import reduce
from typing import Any, List, Mapping, Optional, Set

import dpath.util
import pendulum
from jsonref import JsonRef


class CatalogField:
    """Field class to represent cursor/pk fields"""

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

    def parse(self, record: Mapping[str, Any], path: Optional[List[str]] = None) -> Any:
        """Extract field value from the record and cast it to native type"""
        path = path or self.path
        value = reduce(lambda data, key: data[key], path, record)
        return self._parse_value(value)


class JsonSchemaHelper:
    def __init__(self, schema):
        self._schema = schema

    def get_ref(self, path: List[str]):
        node = self._schema
        for segment in path.split("/")[1:]:
            node = node[segment]
        return node

    def get_property(self, path: List[str]) -> Mapping[str, Any]:
        node = self._schema
        for segment in path:
            if "$ref" in node:
                node = self.get_ref(node["$ref"])
            node = node["properties"][segment]
        return node

    def field(self, path: List[str]) -> CatalogField:
        return CatalogField(schema=self.get_property(path), path=path)

    def find_variant_paths(self) -> List[List[str]]:
        """
        return list of json object paths for oneOf or anyOf attributes
        """
        variant_paths = []

        def traverse_schema(_schema, path=[]):
            if path and path[-1] in ["oneOf", "anyOf"]:
                variant_paths.append(path)
            for item in _schema:
                next_obj = _schema[item] if isinstance(_schema, dict) else item
                if isinstance(next_obj, (list, dict)):
                    traverse_schema(next_obj, [*path, item])

        traverse_schema(self._schema)
        return variant_paths

    def validate_variant_paths(self, variant_paths: List[List[str]]):
        """
        Validate oneOf paths according to reference
        https://docs.airbyte.io/connector-development/connector-specification-reference
        """

        def get_top_level_item(variant_path: List[str]):
            # valid path should contain at least 3 items
            path_to_schema_obj = variant_path[:-1]
            return dpath.util.get(self._schema, "/".join(path_to_schema_obj))

        for variant_path in variant_paths:
            top_level_obj = get_top_level_item(variant_path)
            if "$ref" in top_level_obj:
                obj_def = top_level_obj["$ref"].split("/")[-1]
                top_level_obj = self._schema["definitions"][obj_def]
            """
            1. The top-level item containing the oneOf must have type: object
            """
            assert (
                top_level_obj.get("type") == "object"
            ), f"The top-level definition in a `oneOf` block should have type: object. misconfigured object: {top_level_obj}. See specification reference at https://docs.airbyte.io/connector-development/connector-specification-reference"
            """

            2. Each item in the oneOf array must be a property with type: object
            """
            variants = dpath.util.get(self._schema, "/".join(variant_path))
            for variant in variants:
                assert (
                    "properties" in variant
                ), "Each item in the oneOf array should be a property with type object. See specification reference at https://docs.airbyte.io/connector-development/connector-specification-reference"

            """
             3. One string field with the same property name must be
             consistently present throughout each object inside the oneOf
             array. It is required to add a const value unique to that oneOf
             option.
            """
            variant_props = [set(list(v["properties"].keys())) for v in variants]
            common_props = set.intersection(*variant_props)
            assert common_props, "There should be at least one common property for oneOf subobjects"
            assert any(
                [all(["const" in var["properties"][prop] for var in variants]) for prop in common_props]
            ), f"Any of {common_props} properties in {'.'.join(variant_path)} has no const keyword. See specification reference at https://docs.airbyte.io/connector-development/connector-specification-reference"


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
    Travers through json schema and compose list of property keys that object expected to have.
    :param annotate_one_of: Generate one_of index in path
    :param schema: jsonschema to get expected paths
    :returns list of object property keys paths
    """
    paths = []
    # Resolve all references to simplify schema processing.
    schema = JsonRef.replace_refs(schema)

    def _scan_schema(subschema, path=""):
        if "oneOf" in subschema or "anyOf" in subschema:
            if annotate_one_of:
                return [
                    _scan_schema({"type": "object", **s}, path + "(0)")
                    for num, s in enumerate(subschema.get("oneOf") or subschema.get("anyOf"))
                ]
            return [_scan_schema({"type": "object", **s}, path) for s in subschema.get("oneOf") or subschema.get("anyOf")]
        schema_type = subschema.get("type", ["null"])
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
