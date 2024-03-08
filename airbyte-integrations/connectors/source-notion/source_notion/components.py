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
class NotionBlocksTransformation(RecordTransformation):
    """
    Transforms records containing 'mention' objects within their 'rich_text' fields. This method locates the 'mention'
    objects, extracts their type-specific information, and moves this information into a newly created 'info' field within
    the 'mention' object. It then removes the original type-specific field from the 'mention' object.

    The transformation specifically targets a field determined by the record's 'type' attribute. It iterates over each
    'mention' object within the 'rich_text' array of that field, restructures the 'mention' objects for consistency and
    easier access, and updates the record in-place.
    """

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        transform_object_field = record.get("type")

        if transform_object_field:
            rich_text = record.get(
                transform_object_field, {}).get("rich_text", [])
            for r in rich_text:
                mention = r.get("mention")
                if mention:
                    type_info = mention[mention["type"]]
                    record[transform_object_field]["rich_text"][rich_text.index(
                        r)]["mention"]["info"] = type_info
                    del record[transform_object_field]["rich_text"][rich_text.index(
                        r)]["mention"][mention["type"]]

        return record


@dataclass
class NotionSemiIncrementalFilter(RecordFilter):
    """
    The Blocks and Comments endpoints do not support sorting/filtering, and are both semi-incemental in nature.
    This filter is a hack to replicate the existing behaviour until semi-incremental is officially supported by the low-code framework
    """

    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.parameters = parameters

    def filter_records(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Mapping[str, Any]]:
        current_state = [x for x in stream_state.get(
            "states", []) if x["partition"]["id"] == stream_slice.partition["id"]]
        # TODO: REF what to do if no start_date mentioned (see manifest)
        #  implement the same logic
        cursor_value = self.get_filter_date(
            self.config.get("start_date"), current_state)
        if cursor_value:
            print(cursor_value)
            for record in records:
                print(record)
            return [record for record in records if record["last_edited_time"] > cursor_value]
        return records

    def get_filter_date(self, start_date: str, state_value: list) -> str:
        """
        Calculate the filter date to pass in the request parameters by comparing the start_date
        with the value of state obtained from the stream_slice.
        If only one value exists, use it by default. Otherwise, return None.
        If no filter_date is provided, the API will fetch all available records.
        """

        start_date_parsed = pendulum.parse(
            start_date).to_iso8601_string() if start_date else None
        state_date_parsed = (
            pendulum.parse(state_value[0]["cursor"][self.parameters["cursor_field"]]).to_iso8601_string(
            ) if state_value else None
        )

        # Return the max of the two dates if both are present. Otherwise return whichever is present, or None.
        if start_date_parsed or state_date_parsed:
            return max(filter(None, [start_date_parsed, state_date_parsed]), default=None)
