#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Custom low-code components for source-github.

Everything here exists because the GitHub GraphQL responses cannot be reshaped into the
connector's long-standing REST-compatible record shape with declarative transformations
alone. Pagination, page-size reduction, error handling and incremental behavior are all
handled by the manifest.
"""

import base64
import binascii
import logging
import struct
from dataclasses import InitVar, dataclass
from datetime import timedelta
from itertools import groupby
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import (
    PaginationStrategy,
)
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse


LOGGER = logging.getLogger("airbyte")

# GitHub's GraphQL reaction content enum, mapped to the field names the REST API used and
# therefore to the names already present in the `releases` schema and in user warehouses.
GRAPHQL_REACTION_TO_REST = {
    "THUMBS_UP": "plus_one",
    "THUMBS_DOWN": "minus_one",
    "LAUGH": "laugh",
    "HOORAY": "hooray",
    "CONFUSED": "confused",
    "HEART": "heart",
    "ROCKET": "rocket",
    "EYES": "eyes",
}


def _extract_database_id_from_node_id(node_id: Optional[str]) -> Optional[int]:
    """Extract the numeric database ID from a GitHub GraphQL Node ID.

    GitHub Node IDs with type prefixes (e.g. 'RA_...') are URL-safe base64 encodings of a
    msgpack array: [type_flag, repo_database_id, entity_database_id]. The last 4 bytes encode
    the entity's numeric database ID as a big-endian uint32.

    Release assets are the only place this is needed: the GraphQL `ReleaseAsset` type exposes
    no `databaseId`, but the REST-shaped schema has always carried a numeric `id`.
    """
    if not node_id or "_" not in node_id:
        return None
    try:
        encoded = node_id.split("_", 1)[1]
        decoded = base64.urlsafe_b64decode(encoded + "==")
        if len(decoded) >= 4:
            return struct.unpack(">I", decoded[-4:])[0]
    except (ValueError, struct.error, binascii.Error):
        return None
    return None


def _resolve_page_size(page_size: Any, config: Config) -> Optional[int]:
    """Interpolate and coerce a page size supplied to a custom component.

    A custom component's fields are handed over uninterpolated, so a manifest value like
    `"{{ config['page_size_for_large_streams'] }}"` arrives as that literal string. The CDK
    reduces the page size arithmetically, so it has to be an int by the time it is returned
    from `get_page_size`.
    """
    if page_size is None:
        return None
    if isinstance(page_size, str):
        page_size = InterpolatedString.create(page_size, parameters={}).eval(config)
    return int(page_size)


@dataclass
class ReleasesRecordTransformation(RecordTransformation):
    """Reshape a GraphQL `Release` node into the REST-compatible `releases` record.

    Ported verbatim from the legacy `streams.Releases.parse_response`. Five separate
    concerns, none of them expressible as AddFields/RemoveFields:

    - `assets`: unwrap the connection, flatten `uploader` to `uploader_id`, and recover each
      asset's numeric `id` from its node ID.
    - `reactions`: collapse `reactionGroups` into the REST reaction-count object, including
      the zero entries for reactions nobody used and the `total_count` sum.
    - `mentions_count`: unwrap a `totalCount`-only connection.
    - `target_commitish`: unwrap `tagCommit.oid`.
    - `url`/`assets_url`/`upload_url`/`tarball_url`/`zipball_url`: GraphQL does not return
      these, so they are synthesized from the repository, release ID and tag, exactly as the
      REST payload had them.
    """

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        repository = (stream_slice or {}).get("repository")
        record["repository"] = repository

        if record.get("author"):
            record["author"]["type"] = record["author"].pop("__typename", "User")

        record["assets"] = self._assets(record)
        record["reactions"] = self._reactions(record)

        mentions_connection = record.pop("mentions_connection", None)
        if mentions_connection is not None:
            record["mentions_count"] = mentions_connection.get("totalCount", 0)

        tag_commit = record.pop("tagCommit", None)
        record["target_commitish"] = tag_commit.get("target_commitish") if tag_commit else None

        api_url = (config or {}).get("api_url") or "https://api.github.com"
        record.update(
            self._rest_urls(
                api_url=api_url.rstrip("/"),
                repository=repository,
                release_id=record.get("id"),
                tag_name=record.get("tag_name"),
            )
        )

    def _assets(self, record: Mapping[str, Any]) -> list:
        assets_data = record.get("assets") or {}
        if (assets_data.get("pageInfo") or {}).get("hasNextPage"):
            # The query asks for `releaseAssets(first: 100)` and the manifest paginates the
            # releases connection only, so a release with more than 100 assets is truncated.
            # Warn rather than fail, which is what the Python stream did.
            LOGGER.warning(
                "Release %s in %s has >100 assets; only the first 100 were synced. "
                "Sub-pagination for release assets is not yet implemented.",
                record.get("id"),
                record.get("repository"),
            )
        assets = assets_data.get("nodes", [])
        for asset in assets:
            uploader = asset.pop("uploader", None)
            asset["uploader_id"] = uploader.get("id") if uploader else None
            asset["id"] = _extract_database_id_from_node_id(asset.get("node_id"))
        return assets

    def _reactions(self, record: MutableMapping[str, Any]) -> Optional[Mapping[str, Any]]:
        reaction_groups = record.pop("reaction_groups", None)
        if reaction_groups is None:
            return None
        reactions: MutableMapping[str, Any] = {key: 0 for key in GRAPHQL_REACTION_TO_REST.values()}
        total = 0
        for group in reaction_groups:
            rest_key = GRAPHQL_REACTION_TO_REST.get(group.get("content"))
            if rest_key:
                count = (group.get("reactors") or {}).get("totalCount", 0)
                reactions[rest_key] = count
                total += count
        reactions["total_count"] = total
        return reactions

    @staticmethod
    def _rest_urls(api_url: str, repository: Optional[str], release_id: Optional[int], tag_name: Optional[str]) -> Mapping[str, Any]:
        upload_url = api_url.replace("api.github.com", "uploads.github.com")
        return {
            "url": f"{api_url}/repos/{repository}/releases/{release_id}",
            "assets_url": f"{api_url}/repos/{repository}/releases/{release_id}/assets",
            "upload_url": f"{upload_url}/repos/{repository}/releases/{release_id}/assets{{?name,label}}",
            "tarball_url": f"{api_url}/repos/{repository}/tarball/{tag_name}" if tag_name else None,
            "zipball_url": f"{api_url}/repos/{repository}/zipball/{tag_name}" if tag_name else None,
        }


@dataclass
class NestedGraphQLPaginationStrategy(PaginationStrategy):
    """Two-level cursor traversal for `reviews` and `issue_reactions`.

    Both streams walk a repository-level connection (`pullRequests` / `issues`) whose nodes
    each carry a child connection (`reviews` / `reactions`). A child connection that has more
    pages cannot be paginated in place, so the legacy streams switched the query to a
    drill-down rooted at that single parent (`repository.pullRequest(number:)`) and came back
    to the parent listing afterwards.

    All traversal state lives in the page token rather than on this object. That is not a
    stylistic choice: one `PaginationStrategy` instance is shared by every partition of a
    stream, and the partitions are read concurrently, so the legacy `self.reviews_cursors` /
    `self.pull_requests_cursor` dicts were keyed by repository precisely to work around state
    that should never have been shared. A self-contained token removes the sharing instead.

    The token is `{document, after, number, pending, list_after}`:

    - `document` is the query to send next, so the retriever's `request_body` only has to
      choose between "the token's document" and the root listing document.
    - `pending` is the queue of `(parent_number, child_cursor)` pairs still to drill into,
      popped LIFO to match the legacy `dict.popitem()`.
    - `list_after` is where to resume the parent listing once `pending` drains.

    `first` stays a GraphQL variable in both documents so `REDUCE_PAGE_SIZE` still works; only
    the parent's `number` is inlined into the drill-down document, since it is not a page size.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    list_connection: str = ""
    drilldown_field: str = ""
    child_connection: str = ""
    page_size: Optional[int] = None

    # The drill-down document carries the parent's number inline. A literal marker rather than
    # `str.format`, because the GraphQL body is full of braces.
    NUMBER_PLACEHOLDER = "__NUMBER__"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        for field in ("list_connection", "drilldown_field", "child_connection"):
            if not getattr(self, field):
                raise ValueError(f"NestedGraphQLPaginationStrategy requires `{field}`")
        # Read from `$parameters` rather than from a manifest field: a custom component's
        # string fields are not interpolated, so a `{{ parameters[...] }}` reference would
        # arrive verbatim. The stream declares each document once and both the requester's
        # `request_body` and this strategy read that one declaration.
        for field in ("list_document", "drilldown_document"):
            value = parameters.get(field)
            if not value:
                raise ValueError(f"NestedGraphQLPaginationStrategy requires `{field}` in $parameters")
            setattr(self, field, value)

    @property
    def initial_token(self) -> Optional[Any]:
        return None

    def get_page_size(self) -> Optional[int]:
        return _resolve_page_size(self.page_size, self.config)

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Any],
        last_page_token_value: Optional[Any] = None,
        page_size_override: Optional[int] = None,
    ) -> Optional[Mapping[str, Any]]:
        previous = last_page_token_value if isinstance(last_page_token_value, Mapping) else {}
        pending = [list(item) for item in previous.get("pending", [])]
        list_after = previous.get("list_after")

        repository = (response.json().get("data") or {}).get("repository")
        if repository:
            if self.list_connection in repository:
                connection = repository[self.list_connection] or {}
                page_info = connection.get("pageInfo") or {}
                if page_info.get("hasNextPage"):
                    list_after = page_info.get("endCursor")
                for node in connection.get("nodes") or []:
                    self._queue_child(node, pending)
            elif self.drilldown_field in repository:
                self._queue_child(repository[self.drilldown_field] or {}, pending)

        if pending:
            number, after = pending.pop()
            return {
                "document": self.drilldown_document.replace(self.NUMBER_PLACEHOLDER, str(number)),
                "after": after,
                "number": number,
                "pending": pending,
                "list_after": list_after,
            }
        if list_after:
            return {
                "document": self.list_document,
                "after": list_after,
                "number": None,
                "pending": [],
                "list_after": None,
            }
        return None

    def _queue_child(self, node: Mapping[str, Any], pending: list) -> None:
        child = node.get(self.child_connection) or {}
        if (child.get("pageInfo") or {}).get("hasNextPage"):
            pending.append([node.get("number"), child["pageInfo"]["endCursor"]])


@dataclass
class NestedGraphQLRecordExtractor(RecordExtractor):
    """Extract child records from either shape a two-level GraphQL traversal can return.

    The listing query nests the child connection under every parent node:

        data.repository.<list_connection>.nodes[*].<child_connection>.nodes[*]

    the drill-down query returns a single parent:

        data.repository.<drilldown_field>.<child_connection>.nodes[*]

    A `DpathExtractor` can express either path but not both, and the records also need fields
    that only exist on the parent node (`reviews.pull_request_url` comes from the pull
    request's `url`), which a path-based extractor cannot reach at all. `parent_fields` maps a
    field on the parent node to the field name to copy it into.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    list_connection: str = ""
    drilldown_field: str = ""
    child_connection: str = ""
    parent_fields: Optional[Mapping[str, str]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        for field in ("list_connection", "drilldown_field", "child_connection"):
            if not getattr(self, field):
                raise ValueError(f"NestedGraphQLRecordExtractor requires `{field}`")

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        repository = (response.json().get("data") or {}).get("repository")
        if not repository:
            # GitHub answers 200 with a null repository when the token cannot see it.
            return
        repository_name = f"{(repository.get('owner') or {}).get('login')}/{repository.get('name')}"
        if self.list_connection in repository:
            parents = ((repository[self.list_connection] or {}).get("nodes")) or []
        else:
            parent = repository.get(self.drilldown_field)
            parents = [parent] if parent else []
        for parent in parents:
            children = ((parent.get(self.child_connection) or {}).get("nodes")) or []
            for record in children:
                record["repository"] = repository_name
                for source, destination in (self.parent_fields or {}).items():
                    record[destination] = parent.get(source)
                yield record


# Depth-first order for the four-level reaction traversal: the deepest pending connection is
# always drilled into first, so a comment's reactions are finished before the next pull
# request is opened. Ported from `graphql.CursorStorage`, which built the same ordering out of
# a heap keyed on this list reversed.
_REACTION_TRAVERSAL_PRIORITY = {
    "Reaction": 0,
    "PullRequestReviewComment": 1,
    "PullRequestReview": 2,
    "PullRequest": 3,
}

# Which child connection each queued object type needs paginated, and which document roots at
# it. `PullRequest` is the repository-level listing; the rest root at `node(id:)`.
_REACTION_CONNECTION_OF = {
    "PullRequest": "pullRequests",
    "PullRequestReview": "reviews",
    "PullRequestReviewComment": "comments",
    "Reaction": "reactions",
}


@dataclass
class DeepNestedGraphQLPaginationStrategy(PaginationStrategy):
    """Four-level depth-first traversal for `pull_request_comment_reactions`.

    `repository.pullRequests -> reviews -> comments -> reactions`. Every level can have more
    pages than the query asked for, and none of them can be paginated in place, so each
    overflowing connection is queued and later re-rooted with its own document:

    - `PullRequest`      -> the repository listing, paginated by `pullRequests`
    - `PullRequestReview`-> `node(id: <pull request>)`, paginated by `reviews`
    - `PullRequestReviewComment` -> `node(id: <review>)`, paginated by `comments`
    - `Reaction`         -> `node(id: <comment>)`, paginated by `reactions`

    The queue is ordered deepest-first, which is what makes the traversal depth-first: the
    reactions of a comment are drained before the next review is opened.

    Like `NestedGraphQLPaginationStrategy`, the queue lives in the page token rather than on
    this object, because one strategy instance is shared by every partition of the stream and
    the partitions are read concurrently. The legacy `self.cursor_storage` was a single heap
    shared across repositories.

    One legacy behavior is deliberately not carried over: the legacy `request_body_json` used to send
    `first = min(page_size, total_count)` to avoid paying for pages larger than what remained.
    `first` has to stay a GraphQL variable for `REDUCE_PAGE_SIZE` to be able to shrink it, and
    a variable cannot be per-token, so the connector may now over-ask on the last page of a
    connection. GitHub returns fewer records; the cost is a slightly higher query score.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    documents: Optional[Mapping[str, str]] = None
    page_size: Optional[int] = None

    NODE_PLACEHOLDER = "__NODE_ID__"

    # $parameters key holding the document that re-roots at each object type.
    DOCUMENT_PARAMETERS = {
        "PullRequest": "root_repository_document",
        "PullRequestReview": "root_pull_request_document",
        "PullRequestReviewComment": "root_review_document",
        "Reaction": "root_comment_document",
    }

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if self.documents is None:
            # Same reason as NestedGraphQLPaginationStrategy: a custom component's fields are
            # not interpolated, so the documents are read from $parameters.
            self.documents = {typename: parameters[key] for typename, key in self.DOCUMENT_PARAMETERS.items() if parameters.get(key)}
        missing = set(_REACTION_TRAVERSAL_PRIORITY) - set(self.documents or {})
        if missing:
            raise ValueError(f"DeepNestedGraphQLPaginationStrategy requires a document for every object type; missing {sorted(missing)}")

    @property
    def initial_token(self) -> Optional[Any]:
        return None

    def get_page_size(self) -> Optional[int]:
        return _resolve_page_size(self.page_size, self.config)

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Any],
        last_page_token_value: Optional[Any] = None,
        page_size_override: Optional[int] = None,
    ) -> Optional[Mapping[str, Any]]:
        previous = last_page_token_value if isinstance(last_page_token_value, Mapping) else {}
        pending = [list(item) for item in previous.get("pending", [])]
        sequence = previous.get("sequence", 0)

        data = response.json().get("data") or {}

        repository = data.get("repository")
        if repository:
            sequence = self._queue(repository, "PullRequest", pending, sequence)
            for pull_request in self._nodes(repository, "pullRequests"):
                sequence = self._walk_pull_request(pull_request, pending, sequence)

        node = data.get("node")
        if node:
            typename = node.get("__typename")
            if typename == "PullRequest":
                sequence = self._walk_pull_request(node, pending, sequence)
            elif typename == "PullRequestReview":
                sequence = self._walk_review(node, pending, sequence)
            elif typename == "PullRequestReviewComment":
                sequence = self._queue(node, "Reaction", pending, sequence)

        if not pending:
            return None

        # Deepest first, and first-queued first within a depth -- the ordering the heap gave.
        pending.sort(key=lambda item: (item[0], item[1]))
        _, _, typename, cursor, node_id = pending.pop(0)
        document = self.documents[typename]  # type: ignore[index]
        if node_id is not None:
            document = document.replace(self.NODE_PLACEHOLDER, str(node_id))
        return {"document": document, "after": cursor, "typename": typename, "pending": pending, "sequence": sequence}

    def _walk_pull_request(self, pull_request: Mapping[str, Any], pending: list, sequence: int) -> int:
        sequence = self._queue(pull_request, "PullRequestReview", pending, sequence)
        for review in self._nodes(pull_request, "reviews"):
            sequence = self._walk_review(review, pending, sequence)
        return sequence

    def _walk_review(self, review: Mapping[str, Any], pending: list, sequence: int) -> int:
        sequence = self._queue(review, "PullRequestReviewComment", pending, sequence)
        for comment in self._nodes(review, "comments"):
            sequence = self._queue(comment, "Reaction", pending, sequence)
        return sequence

    def _queue(self, node: Mapping[str, Any], typename: str, pending: list, sequence: int) -> int:
        """Queue `node`'s child connection if it has another page."""
        connection = node.get(_REACTION_CONNECTION_OF[typename]) or {}
        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            return sequence
        # `PullRequest` re-roots at the repository listing, which needs no node id.
        node_id = None if typename == "PullRequest" else node.get("node_id")
        pending.append([_REACTION_TRAVERSAL_PRIORITY[typename], sequence, typename, page_info.get("endCursor"), node_id])
        return sequence + 1

    @staticmethod
    def _nodes(node: Mapping[str, Any], connection: str) -> Iterable[Mapping[str, Any]]:
        return ((node.get(connection) or {}).get("nodes")) or []


@dataclass
class DeepNestedGraphQLRecordExtractor(RecordExtractor):
    """Extract reaction records from any of the four roots the traversal can return.

    Ported from `streams.PullRequestCommentReactions.parse_response`. Each reaction is stamped
    with its repository and the id of the comment it belongs to; `user.type` is set because the
    legacy record carried it and the GraphQL `user` field here is not a union.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        pass

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        data = response.json().get("data") or {}

        repository = data.get("repository")
        if repository:
            for pull_request in self._nodes(repository, "pullRequests"):
                yield from self._from_pull_request(pull_request, repository)

        node = data.get("node")
        if node:
            # The drill-down documents select the repository alongside the node, so the record
            # can still be stamped with it.
            repository = node.get("repository") or {}
            typename = node.get("__typename")
            if typename == "PullRequest":
                yield from self._from_pull_request(node, repository)
            elif typename == "PullRequestReview":
                yield from self._from_review(node, repository)
            elif typename == "PullRequestReviewComment":
                yield from self._from_comment(node, repository)

    def _from_pull_request(self, pull_request: Mapping[str, Any], repository: Mapping[str, Any]):
        for review in self._nodes(pull_request, "reviews"):
            yield from self._from_review(review, repository)

    def _from_review(self, review: Mapping[str, Any], repository: Mapping[str, Any]):
        for comment in self._nodes(review, "comments"):
            yield from self._from_comment(comment, repository)

    def _from_comment(self, comment: Mapping[str, Any], repository: Mapping[str, Any]):
        repository_name = f"{(repository.get('owner') or {}).get('login')}/{repository.get('name')}"
        for reaction in self._nodes(comment, "reactions"):
            reaction["repository"] = repository_name
            reaction["comment_id"] = comment.get("id")
            if reaction.get("user"):
                reaction["user"]["type"] = "User"
            yield reaction

    @staticmethod
    def _nodes(node: Mapping[str, Any], connection: str) -> Iterable[Mapping[str, Any]]:
        return ((node.get(connection) or {}).get("nodes")) or []


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
class CommitsBranchPartitionRouter(SubstreamPartitionRouter):
    """One partition per branch to pull commits from, resolved the way `Commits.stream_slices` did.

    The parent lists every branch of every repository. For a repository, the configured `branches`
    entries (`owner/repo/branch`) that exist are used; when none is configured, or none of the
    configured ones exists, the repository's default branch is used instead.
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        configured = set(self.config.get("branches") or [])
        # groupby groups only adjacent items. Branch slices arrive repo-by-repo because
        # SubstreamPartitionRouter iterates parent partitions outer / parent records inner, and
        # repository_partition_router emits each repository once -- UnionPartitionRouter dedupes
        # partition values (union_partition_router.py:55-70), so a repository matched by both an
        # explicit entry and a wildcard is not visited twice. Without that, each duplicate group
        # would re-emit the same branch partitions.
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
    change: the legacy `WorkflowRuns.read_records` broke out of the page loop there.

    This is a workaround for a CDK gap, not a GitHub quirk. `CursorPaginationStrategy` already
    exposes the decoded page to `stop_condition`, but the paginator's interpolation context has no
    `stream_slice` (only `config`, `response`, `headers`, `last_record`, `last_page_size`), so the
    slice start cannot be compared against the page from YAML. Until that lands
    (https://github.com/airbytehq/airbyte-python-cdk/issues/1166), the requester injects the slice
    start as a request header GitHub ignores and this strategy reads it back from
    `response.request`. Once `stream_slice` is available, delete this class and the header and use
    a `stop_condition` on the built-in strategy instead.
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
