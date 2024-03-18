# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass, InitVar
from typing import Any, List, Mapping, MutableMapping, Optional

import pendulum

from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter


@dataclass
class NotionUserTransformation(RecordTransformation):
    """
    # TODO: Flesh out docstring
    Custom transformation that conditionally moves the data in owner.{owner_type} 
    to a new owner.info field when the record contains data for a "bot" type user.
    """

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        owner = record.get("bot", {}).get("owner")
        if owner:
            owner_type = owner.get("type")
            owner_info = owner.get(owner_type)
            if owner_type and owner_info:
                record["bot"]["owner"]["info"] = owner_info
                del record["bot"]["owner"][owner_type]
        return record


@dataclass
class NotionPropertiesTransformation(RecordTransformation):
    """
    # TODO: Flesh out docstring
    Custom transformation that normalizes nested 'properties' object by moving
    unique named entities into 'name', 'value' mappings
    """

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        properties = record.get("properties", {})
        transformed_properties = [
            {"name": name, "value": value} for name, value in properties.items()
        ]
        record["properties"] = transformed_properties
        return record


@dataclass
class NotionSemiIncrementalFilter(RecordFilter):
    """
    Custom filter to implement semi-incremental syncing for the Comments endpoints, which does not support sorting or filtering.
    This filter emulates incremental behavior by filtering out records based on the comparison of the cursor value with current value in state,
    ensuring only records updated after the cutoff timestamp are synced.
    """

    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.parameters = parameters

    def filter_records(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        **kwargs
    ) -> List[Mapping[str, Any]]:
      """
      Filters a list of records, returning only those with a cursor_value greater than the current value in state.
      """
      current_state = [state_value for state_value in stream_state.get(
            "states", []) if state_value["partition"]["id"] == stream_slice.partition["id"]]
      cursor_value = self.get_filter_date(
            self.config.get("start_date"), current_state)
      if cursor_value:
            return [record for record in records if record["last_edited_time"] > cursor_value]
      return records

    def get_filter_date(self, start_date: str, state_value: list) -> str:
        """
        Calculates the filter date to pass in the request parameters by comparing the start_date with the value of state obtained from the stream_slice.
        If only the start_date exists, use it by default.
        """

        start_date_parsed = pendulum.parse(
            start_date).to_iso8601_string() if start_date else None
        state_date_parsed = (
            pendulum.parse(state_value[0]["cursor"]["last_edited_time"]).to_iso8601_string(
            ) if state_value else None
        )

        if state_date_parsed:
            return max(filter(None, [start_date_parsed, state_date_parsed]), default=start_date_parsed)
        return start_date_parsed
