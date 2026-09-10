#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import timedelta
from itertools import groupby
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse


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
    # GitHub ids were stored as strings and the routers carry them as integers; branch names stay strings.
    integer_ids: bool = True

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

    def _to_id(self, key: str) -> Any:
        return int(key) if self.integer_ids and isinstance(key, str) and key.isdigit() else key


@dataclass
class WorkflowJobsLegacyStateMigration(StateMigration):
    """Migrate the legacy `{repository: {completed_at: value}}` state of `workflow_jobs`.

    The declarative stream keeps one global `completed_at` cursor and lets its parent
    (`workflow_runs`) resume per repository, which is what the Python class did by handing its own
    cursor to the parent as `updated_at`. The lowest repository cursor becomes the global one so no
    repository skips jobs; the parent state keeps the per-repository values.
    """

    config: Config
    parameters: Mapping[str, Any]

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if not stream_state or "state" in stream_state or "states" in stream_state or "parent_state" in stream_state:
            return False
        return all(isinstance(value, Mapping) and set(value) == {"completed_at"} for value in stream_state.values())

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        cursors = {repository: value["completed_at"] for repository, value in stream_state.items()}
        return {
            "use_global_cursor": True,
            "state": {"completed_at": min(cursors.values(), key=ab_datetime_parse)},
            "parent_state": {"workflow_runs": {repository: {"updated_at": cursor} for repository, cursor in cursors.items()}},
        }


@dataclass
class FlattenAuthorTransformation(RecordTransformation):
    """`ContributorActivity.transform`: lift the `author` object's fields onto the record."""

    config: Config
    parameters: Mapping[str, Any]

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        author = record.pop("author", None)
        if author:
            record.update(author)


@dataclass
class CommitsBranchPartitionRouter(SubstreamPartitionRouter):
    """One partition per branch to pull commits from, resolved the way `Commits.stream_slices` did.

    The parent lists every branch of every repository. For a repository, the configured `branches`
    entries (`owner/repo/branch`) that exist are used; when none is configured, or none of the
    configured ones exists, the repository's default branch is used instead.
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        configured = set(self.config.get("branches") or [])
        for repository, branch_slices in groupby(super().stream_slices(), key=lambda s: s.partition["parent_slice"]["repository"]):
            branch_slices = list(branch_slices)
            wanted = [s for s in branch_slices if f"{repository}/{s.partition['branch']}" in configured]
            if not wanted:
                default_branch = next((s.extra_fields.get("default_branch") for s in branch_slices), None)
                wanted = [s for s in branch_slices if s.partition["branch"] == default_branch]
                if not wanted and default_branch:
                    wanted = [
                        StreamSlice(partition={"branch": default_branch, "parent_slice": {"repository": repository}}, cursor_slice={})
                    ]
            yield from wanted


@dataclass
class WorkflowRunsPaginationStrategy(CursorPaginationStrategy):
    """Stop paging once the page's oldest run was created more than 32 days before the slice start.

    Runs are listed newest-created first and can be re-run for 32 days, so nothing older can still
    change: the legacy `WorkflowRuns.read_records` broke out of the page loop there. The slice start
    travels in a request header because the paginator only sees the records that survived the
    client-side filter, not the slice, and GitHub ignores the header.
    """

    window_header: str = "X-Airbyte-Window-Start"
    re_run_period_days: int = 32

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any] = None,
    ) -> Optional[Any]:
        window_start = response.request.headers.get(self.window_header) if response.request else None
        try:
            runs = (response.json() or {}).get("workflow_runs") or []
        except ValueError:
            runs = []
        oldest = runs[-1].get("created_at") if runs and isinstance(runs[-1], Mapping) else None
        if (
            window_start
            and oldest
            and ab_datetime_parse(oldest) < ab_datetime_parse(window_start) - timedelta(days=self.re_run_period_days)
        ):
            return None
        return super().next_page_token(response, last_page_size, last_record, last_page_token_value)
