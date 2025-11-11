# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass
from enum import Enum
from typing import Any, Iterable, List, Mapping, Optional, Set

from airbyte_cdk.sources.declarative.requesters.query_properties.strategies import GroupByKey
from airbyte_cdk.sources.declarative.requesters.query_properties.strategies.merge_strategy import (
    RecordMergeStrategy,
)
from airbyte_cdk.sources.types import Config, Record


class PropertyLimitType(Enum):
    """
    The heuristic that determines when the maximum size of the current chunk of properties and when a new
    one should be started.
    """

    characters = "characters"
    property_count = "property_count"


@dataclass
class PropertyChunking:
    """
    Defines the behavior for how the complete list of properties to query for are broken down into smaller groups
    that will be used for multiple requests to the target API.
    """

    property_limit_type: PropertyLimitType
    property_limit: Optional[int]
    record_merge_strategy: Optional[RecordMergeStrategy]
    parameters: InitVar[Mapping[str, Any]]
    config: Config

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._record_merge_strategy = self.record_merge_strategy or GroupByKey(
            key="id", config=self.config, parameters=parameters
        )

    def get_request_property_chunks(
        self,
        property_fields: List[str],
        always_include_properties: Optional[List[str]],
        configured_properties: Optional[Set[str]],
    ) -> Iterable[List[str]]:
        if not self.property_limit:
            single_property_chunk = list(property_fields)
            if always_include_properties:
                single_property_chunk.extend(always_include_properties)
            yield single_property_chunk
            return
        current_chunk = list(always_include_properties) if always_include_properties else []
        chunk_size = 0
        for property_field in property_fields:
            # If property_limit_type is not defined, we default to property_count which is just an incrementing count
            # todo: Add ability to specify parameter delimiter representation and take into account in property_field_size
            if configured_properties is not None and property_field not in configured_properties:
                continue
            property_field_size = (
                len(property_field)
                + 3  # The +3 represents the extra characters for encoding the delimiter in between properties
                if self.property_limit_type == PropertyLimitType.characters
                else 1
            )
            if chunk_size + property_field_size > self.property_limit:
                yield current_chunk
                current_chunk = list(always_include_properties) if always_include_properties else []
                chunk_size = 0
            current_chunk.append(property_field)
            chunk_size += property_field_size
        yield current_chunk

    def get_merge_key(self, record: Record) -> Optional[str]:
        return self._record_merge_strategy.get_group_key(record=record)
