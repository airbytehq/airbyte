# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState


logger = logging.getLogger("airbyte")

# Maximum block hierarchy recursive request depth
MAX_BLOCK_DEPTH = 30


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


@dataclass
class NotionBlocksPartitionRouter(SubstreamPartitionRouter):
    """
    Custom partition router for Notion blocks that handles recursive hierarchy traversal.
    This router implements depth-first traversal of block hierarchy with depth limiting.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._block_id_stack = []
        self._visited_blocks = set()  # Track visited blocks to prevent cycles

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Generate stream slices for each page, then recursively traverse block hierarchy.
        """
        # Get all parent pages first
        parent_pages = []
        for parent_stream_config in self.parent_stream_configs:
            for parent_record in parent_stream_config.stream.read_records(sync_mode=SyncMode.full_refresh):
                parent_pages.append(parent_record)

        # Process each page and its blocks recursively
        for page in parent_pages:
            page_id = page["id"]
            self._block_id_stack = [page_id]  # Initialize with page ID
            self._visited_blocks = {page_id}

            # Generate slice for this page's immediate children
            yield StreamSlice(partition={"block_id": page_id, "parent_id": page_id, "depth": 0}, cursor_slice={})


@dataclass
class NotionBlocksTransformation(RecordTransformation):
    """
    Custom transformation for Notion blocks that handles:
    1. Rich text mention transformations
    2. Adding sequence numbers to parent relationships
    3. Adding parent information for hierarchy tracking
    """

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> MutableMapping[str, Any]:
        # Transform rich_text mentions
        transform_object_field = record.get("type")
        if transform_object_field:
            rich_text = record.get(transform_object_field, {}).get("rich_text", [])
            for i, r in enumerate(rich_text):
                mention = r.get("mention")
                if mention:
                    mention_type = mention.get("type")
                    if mention_type and mention_type in mention:
                        type_info = mention[mention_type]
                        record[transform_object_field]["rich_text"][i]["mention"]["info"] = type_info
                        del record[transform_object_field]["rich_text"][i]["mention"][mention_type]

        # Add parent information from stream slice
        if stream_slice:
            parent_id = stream_slice.partition.get("parent_id")
            depth = stream_slice.partition.get("depth", 0)

            if parent_id:
                record.setdefault("parent", {})["id"] = parent_id
                record.setdefault("parent", {})["depth"] = depth

        return record


@dataclass
class NotionBlocksFilter(RecordFilter):
    """
    Custom filter for Notion blocks that excludes unsupported block types
    and implements incremental filtering logic.
    """

    excluded_types: List[str] = field(default_factory=lambda: ["child_page", "child_database", "ai_block"])

    def filter_records(
        self, records: List[Mapping[str, Any]], stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, **kwargs
    ) -> List[Mapping[str, Any]]:
        """
        Filter out excluded block types and apply incremental filtering.
        """
        filtered_records = []

        for record in records:
            # Filter out excluded block types
            if record.get("type") in self.excluded_types:
                logger.debug(f"Filtering out block of type: {record.get('type')}")
                continue

            # Apply incremental filtering if needed
            if stream_state:
                cursor_field = "last_edited_time"
                record_time = record.get(cursor_field, "")
                state_time = stream_state.get(cursor_field, "")

                if state_time and record_time < state_time:
                    continue

            filtered_records.append(record)

        return filtered_records


@dataclass
class NotionBlocksErrorHandler(ErrorHandler):
    """
    Custom error handler for Notion blocks that handles:
    1. 404 errors for inaccessible blocks
    2. 400 errors for unsupported ai_block types
    3. Custom backoff for rate limiting
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ResponseAction:
        """
        Interpret the response and determine the appropriate action.
        """
        if not isinstance(response_or_exception, requests.Response):
            return ResponseAction.FAIL

        response = response_or_exception

        # Handle 404 errors for inaccessible blocks
        if response.status_code == 404:
            logger.warning(
                f"Block not accessible (404): {response.json().get('message', 'Unknown error')}. "
                "This is expected when the integration doesn't have access to certain blocks."
            )
            return ResponseAction.IGNORE

        # Handle 400 errors for unsupported ai_block types
        if response.status_code == 400:
            error_data = response.json()
            error_code = error_data.get("code", "")
            error_msg = error_data.get("message", "")

            if "validation_error" in error_code and "ai_block is not supported" in error_msg:
                logger.warning(
                    f"Unsupported ai_block type encountered: {error_msg}. "
                    "Skipping this block as ai_block types are not supported by the API."
                )
                return ResponseAction.IGNORE

        # Handle rate limiting (429)
        if response.status_code == 429:
            return ResponseAction.RETRY

        # Handle server errors (5xx)
        if response.status_code >= 500:
            return ResponseAction.RETRY

        # For all other cases, use default handling
        return ResponseAction.FAIL
