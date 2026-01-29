# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.core import StreamData


# maximum block hierarchy recursive request depth
MAX_BLOCK_DEPTH = 30
# cursor field used for incremental sync
CURSOR_FIELD = "last_edited_time"
# datetime format used by Notion API
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
logger = logging.getLogger("airbyte")


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
class BlocksRetriever(SimpleRetriever):
    """
    Docs: https://developers.notion.com/reference/get-block-children

    According to that fact that block's entity may have children entities that stream also need to retrieve
    BlocksRetriever calls read_records when received record.has_children is True.

    This retriever also implements client-side incremental filtering since the CDK's
    ClientSideIncrementalRecordFilterDecorator is not applied to CustomRetriever components.
    Records are filtered based on their last_edited_time against the cursor state.
    """

    # Cursor state value for filtering - will be set from the stream slice's cursor_slice
    _cursor_state_value: Optional[str] = field(default=None, init=False, repr=False)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.current_block_depth = 0

    def _should_be_synced(self, record_data: Mapping[str, Any]) -> bool:
        """
        Check if a record should be synced based on its last_edited_time.
        Returns True if the record's cursor value is >= the cursor state value.
        """
        if not self._cursor_state_value:
            # No cursor state, sync all records
            return True

        record_cursor_value = record_data.get(CURSOR_FIELD)
        if not record_cursor_value:
            # No cursor field in record, sync it to be safe
            logger.warning(f"Could not find cursor field `{CURSOR_FIELD}` in record. The record will be synced.")
            return True

        try:
            record_time = datetime.strptime(record_cursor_value, DATETIME_FORMAT)
            state_time = datetime.strptime(self._cursor_state_value, DATETIME_FORMAT)
            return record_time >= state_time
        except ValueError as e:
            # If parsing fails, sync the record to be safe
            logger.warning(f"Failed to parse datetime for filtering: {e}. The record will be synced.")
            return True

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        # if reached recursive limit, don't read anymore
        if self.current_block_depth > MAX_BLOCK_DEPTH:
            logger.info("Reached max block depth limit. Exiting.")
            return

        # Extract cursor state from the stream slice for filtering
        # The cursor_slice contains the state from the GlobalSubstreamCursor
        if stream_slice and stream_slice.cursor_slice and self.current_block_depth == 0:
            # Only set cursor state at the top level to avoid overwriting during recursion
            cursor_state = stream_slice.cursor_slice.get(CURSOR_FIELD)
            if cursor_state:
                self._cursor_state_value = cursor_state

        for sequence_number, stream_data in enumerate(super().read_records(records_schema, stream_slice)):
            if stream_data.data.get("has_children"):
                self.current_block_depth += 1
                child_stream_slice = StreamSlice(
                    partition={"block_id": stream_data.data["id"], "parent_slice": {}},
                    cursor_slice=stream_slice.cursor_slice,
                )
                yield from self.read_records(records_schema, child_stream_slice)
                self.current_block_depth -= 1

            if "parent" in stream_data:
                stream_data["parent"]["sequence_number"] = sequence_number

            # Apply client-side incremental filtering
            if self._should_be_synced(stream_data.data):
                yield stream_data
