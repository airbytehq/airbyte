# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Iterable, List, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class DuplicatedRecordsFilter(RecordFilter):
    """
    Filter duplicated records based on the "Id" field.
    This can happen when we use predicates that could match the same record multiple times.

    e.g.
    With one record like:
    {"type":"RECORD","record":{"stream":"accounts","data":{"Id":151049662,"Name":"Airbyte Plumbing"},"emitted_at":1748277607993}}
    account_names in config:
    [
        {
          "name": "Airbyte",
          "operator": "Contains"
        },
        {
          "name": "Plumbing",
          "operator": "Contains"
        }
    ],
    will return the same record twice, once for each predicate.
    """

    CONFIG_PREDICATES = "account_names"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._seen_keys = set()

    @cached_property
    def _using_predicates(self) -> bool:
        """
        Indicates whether the connection uses predicates.
        :return: True if the connector uses predicates, False otherwise
        """
        predicates = self.config.get(self.CONFIG_PREDICATES)
        return bool(predicates and isinstance(predicates, list) and predicates)

    def filter_records(
        self, records: List[Mapping[str, Any]], stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for record in records:
            if not self._using_predicates:
                yield record
            else:
                key = record["Id"]
                if key not in self._seen_keys:
                    self._seen_keys.add(key)
                    yield record
