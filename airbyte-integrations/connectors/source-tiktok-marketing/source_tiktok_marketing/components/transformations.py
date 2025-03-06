# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, FieldPointer, StreamSlice, StreamState


@dataclass
class TransformEmptyMetrics(RecordTransformation):
    empty_value = "-"

    def transform(
        self,
        record: Mapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Mapping[str, Any]:
        for metric_key, metric_value in record.get("metrics", {}).items():
            if metric_value == self.empty_value:
                record["metrics"][metric_key] = None

        return record
