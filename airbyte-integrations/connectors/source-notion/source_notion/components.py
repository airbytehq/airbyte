# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, List, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class NotionUserTransformation(RecordTransformation):
    """
    Custom transformation that conditionally transforms Notion User records of type "bot",
    only when the record contains additional nested "owner" info.
    This transformation moves the data in the `owner.{owner_type}` field into a new `owner.info` field for clarity.
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
class NotionDataFeedFilter(RecordFilter):
    """
    Custom filter to implement functioning incremental sync for Data Feed endpoints.
    The Data Feed incremental logic doesn't seem to play nice with Notion's cursor-based pagination,
    and if the current state is not far enough in the future, at least one page will be queried,
    causing any records in that page to be read despite not passing the state threshold. Setting the
    page_size to a lower value can help mitigate this issue, but it's not a perfect solution, and the more
    granular the page size, the greater the traffic. By using this filter, we can ensure the value of state is respected,
    while still using the max page_size in requests.
    """

    def filter_records(
        self, records: List[Mapping[str, Any]], stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, **kwargs
    ) -> List[Mapping[str, Any]]:
        """
        Filters a list of records, returning only those with a cursor_value greater than the current value in state.
        """
        current_state = stream_state.get("last_edited_time", {})
        cursor_value = self._get_filter_date(self.config.get("start_date"), current_state)
        if cursor_value:
            return [record for record in records if record["last_edited_time"] >= cursor_value]
        return records

    def _get_filter_date(self, start_date: str, state_value: list) -> str:
        """
        Calculates the filter date to pass in the request parameters by comparing the start_date with the value of state obtained from the stream_slice.
        If only the start_date exists, use it by default.
        """

        start_date_timestamp = start_date or None
        state_value_timestamp = state_value or None

        if state_value_timestamp:
            return max(filter(None, [start_date_timestamp, state_value_timestamp]), default=start_date_timestamp)
        return start_date_timestamp
