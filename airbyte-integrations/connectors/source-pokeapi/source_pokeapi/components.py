from dataclasses import dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState


from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.types import Config, Record

class VeryCustomTransformation():
    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ):
        record["id"] = "Cristina is awesome!"
        return record
