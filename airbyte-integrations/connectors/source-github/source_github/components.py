#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, MutableMapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.types import Config


@dataclass
class IssueTimelineEventsExtractor(RecordExtractor):
    """Collapse an issue's timeline page into one record keyed by event type.

    The legacy `IssueTimelineEvents.parse_response` yielded `{<event type>: <event>, ...}` per page,
    the last event of each type winning, and a bare record when the body was not a list.
    `repository` and `issue_number` are added by the stream's transformations.
    """

    config: Config
    parameters: Mapping[str, Any]

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        try:
            body = response.json()
        except ValueError:
            body = None
        record: MutableMapping[str, Any] = {}
        if isinstance(body, list):
            for event in body:
                if isinstance(event, Mapping) and "event" in event:
                    record[event["event"]] = event
        yield record


@dataclass
class NestedLegacyToPerPartitionStateMigration(StateMigration):
    """Migrate the nested state the Python parent-child streams wrote to per-partition state.

    Legacy shape: `{repository: {<parent id>: {cursor_field: value}}}`, one more level of ids per
    parent (`project_cards` nests `project_id` then `column_id`). `partition_fields` lists those id
    levels, outermost first. Ids were stored as strings; the declarative partitions carry them as
    the integers GitHub returns.
    """

    config: Config
    parameters: Mapping[str, Any]
    cursor_field: str
    partition_fields: List[str]

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if not stream_state or "states" in stream_state or "state" in stream_state:
            return False
        return all(self._is_legacy_repository_state(value) for value in stream_state.values())

    def _is_legacy_repository_state(self, node: Any, depth: int = 0) -> bool:
        if not isinstance(node, Mapping) or not node:
            return False
        if depth == len(self.partition_fields):
            return set(node) == {self.cursor_field}
        return all(self._is_legacy_repository_state(child, depth + 1) for child in node.values())

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        states = []
        for repository, node in stream_state.items():
            self._collect(node, {"repository": repository}, 0, states)
        return {"states": states}

    def _collect(self, node: Mapping[str, Any], partition: Mapping[str, Any], depth: int, states: List[Mapping[str, Any]]) -> None:
        if depth == len(self.partition_fields):
            states.append({"partition": partition, "cursor": {self.cursor_field: node[self.cursor_field]}})
            return
        for key, child in node.items():
            child_partition = {self.partition_fields[depth]: self._to_id(key), "parent_slice": partition}
            self._collect(child, child_partition, depth + 1, states)

    @staticmethod
    def _to_id(key: str) -> Any:
        return int(key) if isinstance(key, str) and key.isdigit() else key
