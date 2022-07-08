#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping

import dpath.exceptions
import dpath.util
from airbyte_cdk.sources.declarative.transformations.transformer import RecordTransformation
from airbyte_cdk.sources.declarative.types import FieldPointer


class RemoveFields(RecordTransformation):
    """
    A transformation which removes fields from a record. The fields removed are designated using FieldPointers.
    During transformation, if a field or any of its parents does not exist in the record, no error is thrown.
    """

    def __init__(self, field_pointers: List[FieldPointer]):
        """
        :param field_pointers: pointers to the fields that should be removed
        """
        self._field_pointers = field_pointers

    def transform(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        :param record: The record to be transformed
        :return: the input record with the requested fields removed
        """
        for pointer in self._field_pointers:
            try:
                dpath.util.delete(record, pointer)
            except dpath.exceptions.PathNotFound:
                # if the (potentially nested) property does not exist, silently skip
                pass

        return record
