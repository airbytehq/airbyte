#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping

import dpath.exceptions
import dpath.util
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import FieldPointer, Record
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class RemoveFields(RecordTransformation, JsonSchemaMixin):
    """
    A transformation which removes fields from a record. The fields removed are designated using FieldPointers.
    During transformation, if a field or any of its parents does not exist in the record, no error is thrown.

    If an input field pointer references an item in a list (e.g: ["k", 0] in the object {"k": ["a", "b", "c"]}) then
    the object at that index is set to None rather than being not entirely removed from the list. TODO change this behavior.

    It's possible to remove objects nested in lists e.g: removing [".", 0, "k"] from {".": [{"k": "V"}]} results in {".": [{}]}

    Usage syntax:

    ```yaml
        my_stream:
            <other parameters..>
            transformations:
                - type: RemoveFields
                  field_pointers:
                    - ["path", "to", "field1"]
                    - ["path2"]
    ```

    Attributes:
        field_pointers (List[FieldPointer]): pointers to the fields that should be removed
    """

    field_pointers: List[FieldPointer]
    options: InitVar[Mapping[str, Any]]

    def transform(self, record: Record, **kwargs) -> Record:
        """
        :param record: The record to be transformed
        :return: the input record with the requested fields removed
        """
        for pointer in self.field_pointers:
            # the dpath library by default doesn't delete fields from arrays
            try:
                dpath.util.delete(record, pointer)
            except dpath.exceptions.PathNotFound:
                # if the (potentially nested) property does not exist, silently skip
                pass

        return record
