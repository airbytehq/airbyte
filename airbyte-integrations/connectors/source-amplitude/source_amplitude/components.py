#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, MutableMapping, Optional

import pendulum
import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


logger = logging.getLogger("airbyte")


class AverageSessionLengthRecordExtractor(RecordExtractor):
    """
    Create records from complex response structure
    Issue: https://github.com/airbytehq/airbyte/issues/23145
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_data = response.json().get("data", [])
        if response_data:
            # From the Amplitude documentation it follows that "series" is an array with one element which is itself
            # an array that contains the average session length for each day.
            # https://developers.amplitude.com/docs/dashboard-rest-api#returns-2
            series = response_data.get("series", [])
            if len(series) > 0:
                series = series[0]  # get the nested list
                return [{"date": date, "length": length} for date, length in zip(response_data["xValues"], series)]
        return []


class ActiveUsersRecordExtractor(RecordExtractor):
    """
    Create records from complex response structure
    Issue: https://github.com/airbytehq/airbyte/issues/23145
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_data = response.json().get("data", [])
        if response_data:
            series = list(zip(*response_data["series"]))
            if series:
                return [
                    {"date": date, "statistics": dict(zip(response_data["seriesLabels"], users))}
                    for date, users in zip(response_data["xValues"], series)
                ]
        return []


@dataclass
class TransformDatetimesToRFC3339(RecordTransformation):
    def __init__(self):
        self.name = "events"

    def _get_schema(self, config: Config):
        schema_loader = JsonFileSchemaLoader(config=config, parameters={"name": self.name})
        return schema_loader.get_json_schema()

    def _get_schema_root_properties(self, config: Config):
        schema = self._get_schema(config=config)
        return schema["properties"]

    def _get_date_time_items_from_schema(self, config: Config):
        """
        Get all properties from schema with format: 'date-time'
        """
        result = []
        schema = self._get_schema_root_properties(config=config)
        for key, value in schema.items():
            if value.get("format") == "date-time":
                result.append(key)
        return result

    def _date_time_to_rfc3339(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Transform 'date-time' items to RFC3339 format
        """
        for item in record:
            if item in self.date_time_fields and record[item]:
                record[item] = pendulum.parse(record[item]).to_rfc3339_string()
        return record

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        self.date_time_fields = self._get_date_time_items_from_schema(config)
        return self._date_time_to_rfc3339(record)
