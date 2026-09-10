#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Unit tests for the custom low-code components in `source_github.components`.

The pagination strategies are tested directly rather than through a read because the property
that matters most is not observable from a single request: all traversal state lives in the
page token, so the same strategy instance can serve concurrent partitions without them
interfering. The legacy streams kept that state in per-stream dicts keyed by repository.
"""

import json
from unittest.mock import MagicMock

import pytest
import requests
from source_github.components import (
    DeepNestedGraphQLPaginationStrategy,
    DeepNestedGraphQLRecordExtractor,
    NestedGraphQLPaginationStrategy,
    NestedGraphQLRecordExtractor,
    ReleasesRecordTransformation,
    _extract_database_id_from_node_id,
)


def _response(payload):
    response = MagicMock(spec=requests.Response)
    response.json.return_value = payload
    return response


def _page_info(has_next_page, end_cursor=None):
    return {"hasNextPage": has_next_page, "endCursor": end_cursor}


# --- NestedGraphQLPaginationStrategy -----------------------------------------------------


def _reviews_strategy():
    return NestedGraphQLPaginationStrategy(
        config={},
        # The documents come from `$parameters`, not from manifest fields: a custom component's
        # string fields are handed over uninterpolated.
        parameters={"list_document": "LIST", "drilldown_document": "DRILL __NUMBER__"},
        list_connection="pullRequests",
        drilldown_field="pullRequest",
        child_connection="reviews",
        page_size=10,
    )


def _listing(pull_requests, has_next_page=False, end_cursor=None):
    return {
        "data": {
            "repository": {
                "name": "airbyte",
                "owner": {"login": "airbytehq"},
                "pullRequests": {"pageInfo": _page_info(has_next_page, end_cursor), "nodes": pull_requests},
            }
        }
    }


def _pull_request(number, reviews, has_next_page=False, end_cursor=None):
    return {
        "number": number,
        "url": f"https://github.com/pr/{number}",
        "reviews": {"pageInfo": _page_info(has_next_page, end_cursor), "nodes": reviews},
    }


def test_nested_strategy_stops_when_nothing_overflows():
    strategy = _reviews_strategy()

    token = strategy.next_page_token(_response(_listing([_pull_request(1, [{"id": 1}])])), 1, None, None)

    assert token is None


def test_nested_strategy_drills_into_a_pull_request_with_more_reviews():
    strategy = _reviews_strategy()

    token = strategy.next_page_token(
        _response(_listing([_pull_request(7, [{"id": 1}], has_next_page=True, end_cursor="REVIEW_CUR")])),
        1,
        None,
        None,
    )

    assert token["document"] == "DRILL 7"
    assert token["after"] == "REVIEW_CUR"
    assert token["number"] == 7


def test_nested_strategy_finishes_the_drilldowns_before_resuming_the_listing():
    """The listing cursor is parked in the token while the queued children are drained."""
    strategy = _reviews_strategy()

    token = strategy.next_page_token(
        _response(
            _listing(
                [
                    _pull_request(1, [{"id": 1}], has_next_page=True, end_cursor="CUR_1"),
                    _pull_request(2, [{"id": 2}], has_next_page=True, end_cursor="CUR_2"),
                ],
                has_next_page=True,
                end_cursor="LIST_CUR",
            )
        ),
        2,
        None,
        None,
    )
    # LIFO, matching the legacy `dict.popitem()`.
    assert token["number"] == 2
    assert token["list_after"] == "LIST_CUR"
    assert token["pending"] == [[1, "CUR_1"]]

    # Drill-down response for pull request 2, no further reviews.
    drilldown = {
        "data": {
            "repository": {
                "name": "airbyte",
                "owner": {"login": "airbytehq"},
                "pullRequest": _pull_request(2, [{"id": 3}]),
            }
        }
    }
    token = strategy.next_page_token(_response(drilldown), 1, None, token)
    assert token["number"] == 1
    assert token["after"] == "CUR_1"
    assert token["list_after"] == "LIST_CUR"

    drilldown["data"]["repository"]["pullRequest"] = _pull_request(1, [{"id": 4}])
    token = strategy.next_page_token(_response(drilldown), 1, None, token)
    # Queue drained, so the listing resumes where it was parked.
    assert token["document"] == "LIST"
    assert token["after"] == "LIST_CUR"
    assert token["pending"] == []
    assert token["list_after"] is None


def test_nested_strategy_requeues_a_drilldown_that_still_has_pages():
    strategy = _reviews_strategy()
    drilldown = {
        "data": {
            "repository": {
                "name": "airbyte",
                "owner": {"login": "airbytehq"},
                "pullRequest": _pull_request(5, [{"id": 1}], has_next_page=True, end_cursor="CUR_NEXT"),
            }
        }
    }

    token = strategy.next_page_token(_response(drilldown), 1, None, {"pending": [], "list_after": None})

    assert token["number"] == 5
    assert token["after"] == "CUR_NEXT"


def test_nested_strategy_keeps_no_state_between_partitions():
    """The regression the legacy `self.reviews_cursors` dict could not avoid: one strategy
    instance serves every partition of the stream, and partitions are read concurrently."""
    strategy = _reviews_strategy()

    repository_a = _listing([_pull_request(1, [{"id": 1}], has_next_page=True, end_cursor="A_CUR")])
    repository_b = _listing([_pull_request(9, [{"id": 2}])])

    token_a = strategy.next_page_token(_response(repository_a), 1, None, None)
    token_b = strategy.next_page_token(_response(repository_b), 1, None, None)

    assert token_a["after"] == "A_CUR"
    # Repository B has nothing to drill into, and must not inherit A's queue.
    assert token_b is None


def test_nested_strategy_handles_an_inaccessible_repository():
    strategy = _reviews_strategy()

    assert strategy.next_page_token(_response({"data": {"repository": None}}), 0, None, None) is None


@pytest.mark.parametrize("missing", ["list_connection", "drilldown_field", "child_connection"])
def test_nested_strategy_requires_its_connection_names(missing):
    kwargs = {"list_connection": "pullRequests", "drilldown_field": "pullRequest", "child_connection": "reviews"}
    kwargs[missing] = ""

    with pytest.raises(ValueError, match=missing):
        NestedGraphQLPaginationStrategy(
            config={},
            parameters={"list_document": "LIST", "drilldown_document": "DRILL"},
            **kwargs,
        )


@pytest.mark.parametrize("missing", ["list_document", "drilldown_document"])
def test_nested_strategy_requires_its_documents_in_parameters(missing):
    parameters = {"list_document": "LIST", "drilldown_document": "DRILL"}
    del parameters[missing]

    with pytest.raises(ValueError, match=missing):
        NestedGraphQLPaginationStrategy(
            config={},
            parameters=parameters,
            list_connection="pullRequests",
            drilldown_field="pullRequest",
            child_connection="reviews",
        )


# --- NestedGraphQLRecordExtractor ---------------------------------------------------------


def _reviews_extractor():
    return NestedGraphQLRecordExtractor(
        config={},
        parameters={},
        list_connection="pullRequests",
        drilldown_field="pullRequest",
        child_connection="reviews",
        parent_fields={"url": "pull_request_url"},
    )


def test_nested_extractor_reads_the_listing_shape_and_copies_parent_fields():
    records = list(
        _reviews_extractor().extract_records(
            _response(_listing([_pull_request(1, [{"id": 11}, {"id": 12}]), _pull_request(2, [{"id": 21}])]))
        )
    )

    assert [record["id"] for record in records] == [11, 12, 21]
    assert {record["repository"] for record in records} == {"airbytehq/airbyte"}
    assert records[0]["pull_request_url"] == "https://github.com/pr/1"
    assert records[2]["pull_request_url"] == "https://github.com/pr/2"


def test_nested_extractor_reads_the_drilldown_shape():
    payload = {
        "data": {
            "repository": {
                "name": "airbyte",
                "owner": {"login": "airbytehq"},
                "pullRequest": _pull_request(3, [{"id": 31}]),
            }
        }
    }

    records = list(_reviews_extractor().extract_records(_response(payload)))

    assert [record["id"] for record in records] == [31]
    assert records[0]["pull_request_url"] == "https://github.com/pr/3"


def test_nested_extractor_yields_nothing_for_an_inaccessible_repository():
    assert list(_reviews_extractor().extract_records(_response({"data": {"repository": None}}))) == []


# --- DeepNestedGraphQLPaginationStrategy --------------------------------------------------


def _deep_strategy():
    return DeepNestedGraphQLPaginationStrategy(
        config={},
        parameters={},
        documents={
            "PullRequest": "ROOT_REPOSITORY",
            "PullRequestReview": "ROOT_PULL_REQUEST __NODE_ID__",
            "PullRequestReviewComment": "ROOT_REVIEW __NODE_ID__",
            "Reaction": "ROOT_COMMENT __NODE_ID__",
        },
        page_size=10,
    )


def _comment(node_id, database_id, reactions_next=False, cursor=None):
    return {
        "node_id": node_id,
        "id": database_id,
        "reactions": {"pageInfo": _page_info(reactions_next, cursor), "nodes": [{"id": database_id * 10}]},
    }


def _review(node_id, database_id, comments, comments_next=False, cursor=None):
    return {
        "node_id": node_id,
        "id": database_id,
        "comments": {"pageInfo": _page_info(comments_next, cursor), "nodes": comments},
    }


def _deep_listing(pull_requests, list_next=False, list_cursor=None):
    return {
        "data": {
            "repository": {
                "name": "airbyte",
                "owner": {"login": "airbytehq"},
                "pullRequests": {"pageInfo": _page_info(list_next, list_cursor), "nodes": pull_requests},
            }
        }
    }


def _deep_pull_request(node_id, reviews, reviews_next=False, cursor=None):
    return {"node_id": node_id, "reviews": {"pageInfo": _page_info(reviews_next, cursor), "nodes": reviews}}


def test_deep_strategy_stops_when_nothing_overflows():
    payload = _deep_listing([_deep_pull_request("PR_1", [_review("RV_1", 1, [_comment("C_1", 1)])])])

    assert _deep_strategy().next_page_token(_response(payload), 1, None, None) is None


def test_deep_strategy_drills_deepest_first():
    """A comment with more reactions must be drained before the pull request listing advances,
    which is what makes the traversal depth-first."""
    payload = _deep_listing(
        [
            _deep_pull_request(
                "PR_1",
                [
                    _review(
                        "RV_1", 1, [_comment("C_1", 1, reactions_next=True, cursor="REACT_CUR")], comments_next=True, cursor="COMMENT_CUR"
                    )
                ],
                reviews_next=True,
                cursor="REVIEW_CUR",
            )
        ],
        list_next=True,
        list_cursor="LIST_CUR",
    )

    token = _deep_strategy().next_page_token(_response(payload), 1, None, None)

    assert token["typename"] == "Reaction"
    assert token["document"] == "ROOT_COMMENT C_1"
    assert token["after"] == "REACT_CUR"
    # Everything shallower stays queued, ordered by depth.
    assert [item[2] for item in sorted(token["pending"], key=lambda i: (i[0], i[1]))] == [
        "PullRequestReviewComment",
        "PullRequestReview",
        "PullRequest",
    ]


def test_deep_strategy_walks_the_whole_queue_in_depth_order():
    payload = _deep_listing(
        [
            _deep_pull_request(
                "PR_1",
                [
                    _review(
                        "RV_1", 1, [_comment("C_1", 1, reactions_next=True, cursor="REACT_CUR")], comments_next=True, cursor="COMMENT_CUR"
                    )
                ],
                reviews_next=True,
                cursor="REVIEW_CUR",
            )
        ],
        list_next=True,
        list_cursor="LIST_CUR",
    )
    strategy = _deep_strategy()
    empty_node = {
        "data": {
            "node": {
                "__typename": "PullRequestReviewComment",
                "node_id": "C_1",
                "id": 1,
                "repository": {},
                "reactions": {"pageInfo": _page_info(False), "nodes": []},
            }
        }
    }

    order = []
    token = strategy.next_page_token(_response(payload), 1, None, None)
    while token:
        order.append((token["typename"], token["document"], token["after"]))
        token = strategy.next_page_token(_response(empty_node), 0, None, token)
        # The stub response only re-queues nothing, so the loop drains the parked queue.

    assert order == [
        ("Reaction", "ROOT_COMMENT C_1", "REACT_CUR"),
        ("PullRequestReviewComment", "ROOT_REVIEW RV_1", "COMMENT_CUR"),
        ("PullRequestReview", "ROOT_PULL_REQUEST PR_1", "REVIEW_CUR"),
        ("PullRequest", "ROOT_REPOSITORY", "LIST_CUR"),
    ]


def test_deep_strategy_re_roots_at_the_repository_listing_without_a_node_id():
    payload = _deep_listing([], list_next=True, list_cursor="LIST_CUR")

    token = _deep_strategy().next_page_token(_response(payload), 0, None, None)

    assert token["typename"] == "PullRequest"
    # No placeholder substitution: the listing is addressed by owner/name, not a node id.
    assert token["document"] == "ROOT_REPOSITORY"
    assert token["after"] == "LIST_CUR"


def test_deep_strategy_queues_from_a_drilldown_response():
    payload = {
        "data": {
            "node": {
                "__typename": "PullRequestReview",
                "node_id": "RV_9",
                "repository": {"name": "airbyte", "owner": {"login": "airbytehq"}},
                "comments": {
                    "pageInfo": _page_info(True, "COMMENT_CUR"),
                    "nodes": [_comment("C_9", 9, reactions_next=True, cursor="REACT_CUR")],
                },
            }
        }
    }

    token = _deep_strategy().next_page_token(_response(payload), 1, None, {"pending": [], "sequence": 0})

    assert token["typename"] == "Reaction"
    assert token["document"] == "ROOT_COMMENT C_9"


def test_deep_strategy_keeps_no_state_between_partitions():
    strategy = _deep_strategy()
    overflowing = _deep_listing([], list_next=True, list_cursor="A_CUR")
    quiet = _deep_listing([_deep_pull_request("PR_9", [])])

    token_a = strategy.next_page_token(_response(overflowing), 0, None, None)
    token_b = strategy.next_page_token(_response(quiet), 0, None, None)

    assert token_a["after"] == "A_CUR"
    assert token_b is None


def test_deep_strategy_requires_a_document_for_every_object_type():
    with pytest.raises(ValueError, match="Reaction"):
        DeepNestedGraphQLPaginationStrategy(
            config={},
            parameters={},
            documents={"PullRequest": "A", "PullRequestReview": "B", "PullRequestReviewComment": "C"},
        )


def test_deep_strategy_reads_its_documents_from_parameters():
    strategy = DeepNestedGraphQLPaginationStrategy(
        config={},
        parameters={
            "root_repository_document": "ROOT_REPOSITORY",
            "root_pull_request_document": "ROOT_PULL_REQUEST",
            "root_review_document": "ROOT_REVIEW",
            "root_comment_document": "ROOT_COMMENT",
        },
    )

    assert strategy.documents["Reaction"] == "ROOT_COMMENT"


# --- DeepNestedGraphQLRecordExtractor -----------------------------------------------------


def test_deep_extractor_reads_the_repository_shape():
    payload = _deep_listing([_deep_pull_request("PR_1", [_review("RV_1", 1, [_comment("C_1", 1), _comment("C_2", 2)])])])

    records = list(DeepNestedGraphQLRecordExtractor(config={}, parameters={}).extract_records(_response(payload)))

    assert [record["id"] for record in records] == [10, 20]
    assert [record["comment_id"] for record in records] == [1, 2]
    assert {record["repository"] for record in records} == {"airbytehq/airbyte"}


@pytest.mark.parametrize(
    ("typename", "node"),
    [
        ("PullRequest", _deep_pull_request("PR_1", [_review("RV_1", 1, [_comment("C_1", 3)])])),
        ("PullRequestReview", _review("RV_1", 1, [_comment("C_1", 3)])),
        ("PullRequestReviewComment", _comment("C_1", 3)),
    ],
)
def test_deep_extractor_reads_every_drilldown_shape(typename, node):
    payload = {"data": {"node": {**node, "__typename": typename, "repository": {"name": "airbyte", "owner": {"login": "airbytehq"}}}}}

    records = list(DeepNestedGraphQLRecordExtractor(config={}, parameters={}).extract_records(_response(payload)))

    assert [record["id"] for record in records] == [30]
    assert records[0]["comment_id"] == 3
    assert records[0]["repository"] == "airbytehq/airbyte"


def test_deep_extractor_sets_the_user_type_when_present():
    """The legacy record carried `user.type`, which the GraphQL `user` field does not return."""
    comment = _comment("C_1", 1)
    comment["reactions"]["nodes"] = [{"id": 1, "user": {"login": "octocat"}}, {"id": 2, "user": None}]
    payload = _deep_listing([_deep_pull_request("PR_1", [_review("RV_1", 1, [comment])])])

    records = list(DeepNestedGraphQLRecordExtractor(config={}, parameters={}).extract_records(_response(payload)))

    assert records[0]["user"]["type"] == "User"
    assert records[1]["user"] is None


# --- Releases transformation ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("node_id", "expected"),
    [
        ("RA_kwDOAbcDEf4AAAAB", 1),
        ("", None),
        (None, None),
        # No `_`, so there is no type prefix to strip and nothing to decode.
        ("nounderscore", None),
        # Anything shorter than 4 decoded bytes cannot carry a uint32.
        ("RA_AA", None),
    ],
)
def test_extract_database_id_from_node_id(node_id, expected):
    assert _extract_database_id_from_node_id(node_id) == expected


def test_extract_database_id_is_lenient_about_malformed_node_ids():
    """Carried over from the legacy decoder unchanged: `urlsafe_b64decode` ignores characters
    outside the alphabet, so a malformed node id yields a plausible-looking integer rather
    than None. Pinned so the behavior is at least visible."""
    assert _extract_database_id_from_node_id("RA_!!!not-base64!!!") == 1839931115


def test_releases_transformation_uses_the_configured_api_url():
    """GitHub Enterprise Server installs have their own host, and the synthesized URLs have to
    follow it rather than hard-coding api.github.com."""
    record = {"id": 5, "tag_name": "v1", "assets": {"nodes": []}, "reaction_groups": []}

    ReleasesRecordTransformation().transform(
        record,
        config={"api_url": "https://github.example.com/api/v3/"},
        stream_slice={"repository": "org/repo"},
    )

    assert record["url"] == "https://github.example.com/api/v3/repos/org/repo/releases/5"
    assert record["tarball_url"] == "https://github.example.com/api/v3/repos/org/repo/tarball/v1"
