# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass, field
from typing import Any, List, Mapping, MutableMapping, Optional

import pendulum
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class NotionPropertiesTransformation(RecordTransformation):
    """
    Transforms the nested 'properties' object within a Notion Page/Database record into a more
    normalized form. In Notion's API response, 'properties' is a dictionary where each key
    represents the name of a property and its value contains various metadata and the property's
    actual value.

    The transformed 'properties' will consist of an array where each element is a dictionary
    with two keys: 'name', holding the original property name, and 'value', containing the
    property's content.
    """

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        properties = record.get("properties", {})
        transformed_properties = [{"name": name, "value": value} for name, value in properties.items()]
        record["properties"] = transformed_properties
        return record


@dataclass
class NotionSemiIncrementalFilter(RecordFilter):
    """
    Custom filter to implement semi-incremental syncing for the Comments endpoints, which does not support sorting or filtering.
    This filter emulates incremental behavior by filtering out records based on the comparison of the cursor value with current value in state,
    ensuring only records updated after the cutoff timestamp are synced.
    """

    def filter_records(
        self, records: List[Mapping[str, Any]], stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, **kwargs
    ) -> List[Mapping[str, Any]]:
        """
        Filters a list of records, returning only those with a cursor_value greater than the current value in state.
        """
        current_state = [
            state_value
            for state_value in stream_state.get("states", [])
            if state_value.get("partition", {}).get("id") == stream_slice.get("partition", {}).get("id")
        ]
        cursor_value = self.get_filter_date(self.config.get("start_date"), current_state)
        if cursor_value:
            return [record for record in records if record["last_edited_time"] > cursor_value]
        return records

    def get_filter_date(self, start_date: str, state_value: list) -> str:
        """
        Calculates the filter date to pass in the request parameters by comparing the start_date with the value of state obtained from the stream_slice.
        If only the start_date exists, use it by default.
        """

        start_date_parsed = pendulum.parse(start_date).to_iso8601_string() if start_date else None
        state_date_parsed = pendulum.parse(state_value[0]["cursor"]["last_edited_time"]).to_iso8601_string() if state_value else None

        if state_date_parsed:
            return max(filter(None, [start_date_parsed, state_date_parsed]), default=start_date_parsed)
        return start_date_parsed
