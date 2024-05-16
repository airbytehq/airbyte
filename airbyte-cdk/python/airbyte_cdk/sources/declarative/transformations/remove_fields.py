#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional

import dpath.exceptions
import dpath.util
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, FieldPointer, StreamSlice, StreamState


@dataclass
class RemoveFields(RecordTransformation):
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
    parameters: InitVar[Mapping[str, Any]]
    condition: str = ""

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._filter_interpolator = InterpolatedBoolean(condition=self.condition, parameters=parameters)

    def transform(
        self,
        record: Mapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Mapping[str, Any]:
        """
        :param record: The record to be transformed
        :return: the input record with the requested fields removed
        """
        for pointer in self.field_pointers:
            # the dpath library by default doesn't delete fields from arrays
            try:
                dpath.util.delete(
                    record,
                    pointer,
                    afilter=(lambda x: self._filter_interpolator.eval(config or {}, property=x)) if self.condition else None,
                )
            except dpath.exceptions.PathNotFound:
                # if the (potentially nested) property does not exist, silently skip
                pass

        return record
