#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
"""Utilities to help with JSON Schema.

lazydocs: ignore
"""

import abc
from dataclasses import dataclass
from typing import Any, Dict, List


def resolve_reference(reference: str, references: Dict) -> Dict:
    return references[reference.split("/")[-1]]


def get_single_reference_item(property: Dict, references: Dict) -> Dict:
    # Ref can either be directly in the properties or the first element of allOf
    reference = property.get("$ref")
    if reference is None:
        reference = property["allOf"][0]["$ref"]
    return resolve_reference(reference, references)


def get_union_references(property: Dict, references: Dict) -> List[Dict]:
    # Ref can either be directly in the properties or the first element of allOf
    union_references = property.get("anyOf")
    resolved_references: List[Dict] = []
    for reference in union_references:  # type: ignore
        resolved_references.append(resolve_reference(reference["$ref"], references))
    return resolved_references


class Field(abc.ABC):
    @property
    @abc.abstractmethod
    def type_name(
        self,
    ):  # pragma: no cover
        pass

    def __init__(self, name, property, references, required_properties) -> None:
        self.name = name
        self.required = self.name in required_properties
        self.property = property
        self.references = references
        self.description = property.get("description")
        self.examples = property.get("examples")
        self.default = property.get("default")

    def as_dict(self):
        return {
            "type": self.type_name,
            "required": self.required,
            "examples": self.examples,
            "description": self.description,
            "default": self.default,
        }


class SingleString(Field):
    type_name = "string"

    @staticmethod
    def identity(property, references):
        return property.get("type") == "string"


class Boolean(Field):
    type_name = "boolean"

    @staticmethod
    def identity(property, references):
        return property.get("type") == "boolean"


class Integer(Field):
    type_name = "integer"

    @staticmethod
    def identity(property, references):
        return property.get("type") == "integer"


class Number(Field):
    type_name = "number"

    @staticmethod
    def identity(property, references):
        return property.get("type") == "number"


class MultiEnum(Field):
    type_name = "array"

    @staticmethod
    def identity(property, references):
        if property.get("type") != "array":
            return False

        if property.get("uniqueItems") is not True:
            # Only relevant if it is a set or other datastructures with unique items
            return False

        try:
            # Uses literal
            _ = property["items"]["enum"]
            return True
        except Exception:
            pass

        try:
            # Uses enum
            resolve_reference(property["items"]["$ref"], references)["enum"]
            return True
        except Exception:
            return False


class SingleEnum(Field):
    @property
    def type_name(self):
        return "enum"

    @property
    def enum_values(self):
        return get_single_reference_item(self.property, self.references)["enum"]

    @staticmethod
    def identity(property, references):
        if property.get("enum"):
            return True
        try:
            get_single_reference_item(property, references)["enum"]
            return True
        except Exception:
            return False


class SingleDict(Field):
    type_name = "object"

    @staticmethod
    def identity(property, references):
        if property.get("type") != "object":
            return False
        return "additionalProperties" in property


class SingleReference(Field):
    type_name = "object"

    @staticmethod
    def identity(property, references):
        if property.get("type") is not None:
            return False
        return bool(property.get("$ref"))


class SingleObject(Field):
    type_name = "object"

    @staticmethod
    def identity(property, references):
        try:
            object_reference = get_single_reference_item(property, references)
            if object_reference["type"] != "object":
                return False
            return "properties" in object_reference
        except Exception:
            return False


class Union_(Field):
    type_name = "anyOf"

    @staticmethod
    def identity(property, references):
        if property.get("anyOf") is None:
            return False

        if len(property.get("anyOf")) == 0:  # type: ignore
            return False

        for reference in property.get("anyOf"):  # type: ignore
            if not SingleReference.identity(reference, None):
                return False

        return True


class List_(Field):
    type_name = "array"

    @staticmethod
    def identity(property, references):
        if property.get("type") != "array":
            return False

        if property.get("items") is None:
            return False

        try:
            return property["items"]["type"] in ["string", "number", "integer"]
        except Exception:
            return False


class ObjectList(Field):
    type_name = "array"

    @staticmethod
    def identity(property, references):
        if property.get("type") != "array":
            return False
        try:
            object_reference = resolve_reference(property["items"]["$ref"], references)
            if object_reference["type"] != "object":
                return False
            return "properties" in object_reference
        except Exception:
            return False


FIELDS_TYPES = [
    SingleString,
    Boolean,
    Integer,
    Number,
    MultiEnum,
    SingleEnum,
    SingleDict,
    SingleReference,
    SingleObject,
    Union_,
    List_,
    ObjectList,
]


def field_factory(name, property, references, required_properties):
    for field_type in FIELDS_TYPES:
        if field_type.identity(property, references):
            return field_type(name, property, references, required_properties)
    print(property)
    raise Exception("Unsupported property")
