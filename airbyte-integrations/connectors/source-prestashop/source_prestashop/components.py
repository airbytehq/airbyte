#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Tuple

import pendulum
from pendulum.parsing.exceptions import ParserError

from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


@dataclass
class CustomFieldTransformation(RecordTransformation):
    """
    Remove all "empty" (e.g. '0000-00-00', '0000-00-00 00:00:00') 'date' and 'date-time' fields from record
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.name = parameters.get("name")
        self._schema = self._get_schema_root_properties()
        self._date_and_date_time_fields = self._get_fields_with_property_formats_from_schema(("date", "date-time"))

    def _get_schema_root_properties(self):
        schema_loader = JsonFileSchemaLoader(config=self.config, parameters={"name": self.name})
        schema = schema_loader.get_json_schema()
        return schema["properties"]

    def _get_fields_with_property_formats_from_schema(self, property_formats: Tuple[str, ...]) -> List[str]:
        """
        Get all properties from schema within property_formats
        """
        return [k for k, v in self._schema.items() if v.get("format") in property_formats]

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        for item in record:
            if item in self._date_and_date_time_fields and record.get(item):
                try:
                    pendulum.parse(record[item])
                except ParserError:
                    record[item] = None
        return record
