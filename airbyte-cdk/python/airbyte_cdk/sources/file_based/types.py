#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from functools import total_ordering
from typing import Any, Mapping, MutableMapping, List, Union, Optional, Tuple, Type

from airbyte_cdk.sources.file_based.remote_file import RemoteFile

StreamState = MutableMapping[str, Any]

class StreamSlice:

    def __init__(self, remote_files: List[RemoteFile]):
        self._remotes_files = remote_files
    def get_files(self) -> List[RemoteFile]:
        return self._remotes_files


from pydantic import BaseModel, Field

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


TYPE_PYTHON_MAPPING: Mapping[str, Tuple[str, Optional[Type[Any]]]] = {
    "null": ("null", None),
    "array": ("array", list),
    "boolean": ("boolean", bool),
    "float": ("number", float),
    "integer": ("integer", int),
    "number": ("number", float),
    "object": ("object", dict),
    "string": ("string", str),
}
PYTHON_TYPE_MAPPING = {t: k for k, (_, t) in TYPE_PYTHON_MAPPING.items()}


def get_comparable_type(value: Any) -> Optional[ComparableType]:
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


def get_inferred_type(value: Any) -> Optional[ComparableType]:
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

def _is_equal_or_narrower_type(value: Any, expected_type: str) -> bool:
    if isinstance(value, list):
        # We do not compare lists directly; the individual items are compared.
        # If we hit this condition, it means that the expected type is not
        # compatible with the inferred type.
        return False

    inferred_type = ComparableType(get_inferred_type(value))

    if inferred_type is None:
        return False

    return ComparableType(inferred_type) <= ComparableType(get_comparable_type(expected_type))

class FieldType(ABC):
    @abstractmethod
    def is_type_conform(self, value: Any) -> bool:
        ...

    @abstractmethod
    def get_type(self) -> str:
        """
        Return the non-null type of the object
        Maybe there should be another method to return the null type?
        Note: we know every primitive type should be nullable
        """
        ...


class PrimitiveFieldType(BaseModel, FieldType):
    type: Union[str, List[str]] = Field(..., hidden=True)

    def is_type_conform(self, value: Any) -> bool:
        return _is_equal_or_narrower_type(value, self.get_type())

    def get_type(self) -> str:
        if isinstance(self.type, list):
            return [t for t in self.type if t != "null"][0] # FIXME there should be some validation!
        return self.type

class ObjectFieldType(BaseModel, FieldType):
    type: str = Field(..., hidden=True)
    properties: Mapping[str, Union[PrimitiveFieldType, ArrayFieldType, ObjectFieldType]]

    def is_type_conform(self, value: Any) -> bool:
        return isinstance(value, dict) # FIXME this is probably not enough?

    def get_type(self) -> str:
        return self.type

class ArrayFieldType(BaseModel, FieldType):
    type: str = Field(..., hidden=True)
    items: Union[PrimitiveFieldType, ArrayFieldType, ObjectFieldType]

    def is_type_conform(self, value: Any) -> bool:
        if not isinstance(value, list):
            return False
        return all(_is_equal_or_narrower_type(value, self.items.get_type()) for v in value)

    def get_type(self) -> str:
        return self.type


class StreamSchema(BaseModel):
    type: str # Fixme should be hidden
    properties: Mapping[str, Union[PrimitiveFieldType, ArrayFieldType, ObjectFieldType]] # Fixme should be hidden / abstract the Union type


    def value_is_conform(self, record: Mapping[str, Any]) -> bool:
        schema_columns = set(self.properties.keys())
        record_columns = set(record.keys())
        if not record_columns.issubset(schema_columns):
            return False

        for column, definition in self.properties.items():
            value = record.get(column)
            if value is not None:
                if not definition.is_type_conform(value):
                    return False
        return True
