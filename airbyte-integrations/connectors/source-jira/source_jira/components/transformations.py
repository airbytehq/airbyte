# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, FieldPointer, StreamSlice, StreamState


@dataclass
class RemoveEmptyFields(RecordTransformation):
    field_pointers: FieldPointer
    parameters: InitVar[Mapping[str, Any]]

    def transform(
        self,
        record: Mapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Mapping[str, Any]:
        for pointer in self.field_pointers:
            if pointer in record:
                record[pointer] = {k: v for k, v in record[pointer].items() if v is not None}
        return record
