#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Behavior of the GraphQL streams migrated to the manifest in Step 9.

These streams replaced `streams.GitHubGraphQLStream` and its subclasses. Two things are
asserted throughout: the records keep the REST-compatible shape the Python classes produced
(destinations already have those columns), and the page-size reduction that used to live in
`errors_handlers.GitHubGraphQLErrorHandler` now actually reaches GitHub.
"""

import json
import logging

import pytest
from source_github.source import SourceGithub

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


GRAPHQL_URL = "https://api.github.com/graphql"
REPOSITORY = "airbytehq/airbyte"

_TOKEN_CONFIG = {"credentials": {"personal_access_token": "token"}}


def _config(**overrides):
    return {**_TOKEN_CONFIG, "repositories": [REPOSITORY], "start_date": "2000-01-01T00:00:00Z", **overrides}


def _catalog(stream_name):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=stream_name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )


def _mock_repository_resolution(requests_mock):
    requests_mock.get(
        f"https://api.github.com/repos/{REPOSITORY}",
        json={"id": 1, "full_name": REPOSITORY, "organization": {"login": REPOSITORY.split("/")[0]}},
    )


def _read(config, stream_name):
    catalog = _catalog(stream_name)
    source = SourceGithub(config=dict(config), catalog=catalog, state=[])
    messages, error = [], None
    try:
        for message in source.read(logging.getLogger("airbyte"), dict(config), catalog, []):
            messages.append(message)
    except Exception as exc:  # noqa: BLE001 - assertions inspect the failure
        error = exc
    records = [message.record.data for message in messages if message.type == Type.RECORD]
    return records, error


def _graphql_requests(requests_mock):
    return [request for request in requests_mock.request_history if request.path == "/graphql"]


def _variables(request):
    return json.loads(request.body)["variables"]


def _repository_envelope(connection, nodes, has_next_page=False, end_cursor=None):
    return {
        "data": {
            "repository": {
                "name": REPOSITORY.split("/")[1],
                "owner": {"login": REPOSITORY.split("/")[0]},
                connection: {
                    "nodes": nodes,
                    "pageInfo": {"hasNextPage": has_next_page, "endCursor": end_cursor},
                },
            }
        }
    }


def _release_node(node_id="RE_1", database_id=11, tag="v1.0.0"):
    return {
        "node_id": node_id,
        "id": database_id,
        "name": "release one",
        "tag_name": tag,
        "created_at": "2022-01-01T00:00:00Z",
        "published_at": "2022-01-01T00:00:00Z",
        "updated_at": "2022-01-02T00:00:00Z",
        "draft": False,
        "prerelease": False,
        "body": "notes",
        "body_html": "<p>notes</p>",
        "html_url": f"https://github.com/{REPOSITORY}/releases/tag/{tag}",
        "tagCommit": {"target_commitish": "abc123"},
        "author": {"__typename": "User", "node_id": "U_1", "id": 7, "login": "octocat"},
        "assets": {
            # `RA_kwDOAbcDEf4AAAAB` decodes to a msgpack array whose last 4 bytes are the
            # asset's numeric database ID.
            "nodes": [{"node_id": "RA_kwDOAbcDEf4AAAAB", "name": "asset.zip", "uploader": {"id": 7}}],
            "pageInfo": {"hasNextPage": False},
        },
        "reaction_groups": [
            {"content": "THUMBS_UP", "reactors": {"totalCount": 3}},
            {"content": "HEART", "reactors": {"totalCount": 1}},
        ],
        "mentions_connection": {"totalCount": 2},
    }


# --- Releases ---------------------------------------------------------------------------


def test_releases_record_keeps_the_rest_compatible_shape(rate_limit_mock_response, requests_mock):
    """`ReleasesRecordTransformation` is a port of `streams.Releases.parse_response`, so every
    field that transformation used to synthesize must still be present and identical."""
    _mock_repository_resolution(requests_mock)
    requests_mock.post(GRAPHQL_URL, json=_repository_envelope("releases", [_release_node()]))

    records, error = _read(_config(), "releases")

    assert error is None
    assert len(records) == 1
    record = records[0]
    assert record["repository"] == REPOSITORY
    assert record["target_commitish"] == "abc123"
    assert record["mentions_count"] == 2
    assert record["author"]["type"] == "User"
    # Reaction groups collapse to the REST counts, including zeros for unused reactions.
    assert record["reactions"] == {
        "plus_one": 3,
        "minus_one": 0,
        "laugh": 0,
        "hooray": 0,
        "confused": 0,
        "heart": 1,
        "rocket": 0,
        "eyes": 0,
        "total_count": 4,
    }
    # Assets are unwrapped, the uploader is flattened, and the numeric id is recovered from
    # the node id because GraphQL's ReleaseAsset has no databaseId.
    assert len(record["assets"]) == 1
    assert record["assets"][0]["uploader_id"] == 7
    assert record["assets"][0]["id"] == 1
    # GraphQL returns none of these; they are synthesized to match the old REST payload.
    assert record["url"] == f"https://api.github.com/repos/{REPOSITORY}/releases/11"
    assert record["assets_url"] == f"https://api.github.com/repos/{REPOSITORY}/releases/11/assets"
    assert record["upload_url"] == f"https://uploads.github.com/repos/{REPOSITORY}/releases/11/assets{{?name,label}}"
    assert record["tarball_url"] == f"https://api.github.com/repos/{REPOSITORY}/tarball/v1.0.0"
    assert record["zipball_url"] == f"https://api.github.com/repos/{REPOSITORY}/zipball/v1.0.0"


def test_releases_sends_owner_and_name_as_graphql_variables(rate_limit_mock_response, requests_mock):
    """The legacy sgqlc builders inlined owner/name/first/after into the query text, which is
    why a retry could never change the page size. They are variables now."""
    _mock_repository_resolution(requests_mock)
    requests_mock.post(GRAPHQL_URL, json=_repository_envelope("releases", [_release_node()]))

    _read(_config(), "releases")

    variables = _variables(_graphql_requests(requests_mock)[0])
    assert variables["owner"] == "airbytehq"
    assert variables["name"] == "airbyte"
    assert variables["first"] == 10
    assert "after" not in variables


def test_releases_paginates_on_end_cursor(rate_limit_mock_response, requests_mock):
    _mock_repository_resolution(requests_mock)
    requests_mock.post(
        GRAPHQL_URL,
        [
            {"json": _repository_envelope("releases", [_release_node("RE_1", 11, "v1")], has_next_page=True, end_cursor="CURSOR")},
            {"json": _repository_envelope("releases", [_release_node("RE_2", 12, "v2")])},
        ],
    )

    records, error = _read(_config(), "releases")

    assert error is None
    assert len(records) == 2
    requests = _graphql_requests(requests_mock)
    assert "after" not in _variables(requests[0])
    assert _variables(requests[1])["after"] == "CURSOR"


def test_releases_draft_with_null_tag_has_no_tarball_urls(rate_limit_mock_response, requests_mock):
    """Ported from `test_releases_draft_release_null_tag`. A draft has no tag, so the two
    URLs built from the tag must stay null rather than render the string "None"."""
    _mock_repository_resolution(requests_mock)
    node = _release_node(node_id="RE_draft", database_id=10, tag=None)
    node.update({"draft": True, "tagCommit": None})
    requests_mock.post(GRAPHQL_URL, json=_repository_envelope("releases", [node]))

    records, error = _read(_config(), "releases")

    assert error is None
    record = records[0]
    assert record["tag_name"] is None
    assert record["draft"] is True
    assert record["target_commitish"] is None
    assert record["tarball_url"] is None
    assert record["zipball_url"] is None
    # The two URLs built from the release id are unaffected.
    assert record["url"] == f"https://api.github.com/repos/{REPOSITORY}/releases/10"
    assert record["assets_url"] == f"https://api.github.com/repos/{REPOSITORY}/releases/10/assets"


def test_releases_warns_when_a_release_has_more_than_100_assets(rate_limit_mock_response, requests_mock, caplog):
    """Ported from `test_releases_asset_truncation_warning`. The query asks for
    `releaseAssets(first: 100)` and nothing sub-paginates them, so the truncation has to be
    visible in the logs."""
    _mock_repository_resolution(requests_mock)
    node = _release_node()
    node["assets"] = {
        "nodes": [{"node_id": f"RA_{index}", "name": f"asset_{index}.zip", "uploader": {"id": 1}} for index in range(100)],
        "pageInfo": {"hasNextPage": True},
    }
    requests_mock.post(GRAPHQL_URL, json=_repository_envelope("releases", [node]))

    records, error = _read(_config(), "releases")

    assert error is None
    assert len(records[0]["assets"]) == 100
    assert any(">100 assets" in message for message in caplog.messages)


def test_releases_without_reaction_groups_reports_null_reactions(rate_limit_mock_response, requests_mock):
    """`reaction_groups: null` meant "unknown", not "zero of everything" -- the legacy
    transformation returned None for it and the schema allows null."""
    _mock_repository_resolution(requests_mock)
    node = _release_node()
    node.pop("reaction_groups")
    requests_mock.post(GRAPHQL_URL, json=_repository_envelope("releases", [node]))

    records, error = _read(_config(), "releases")

    assert error is None
    assert records[0]["reactions"] is None


# --- Page-size reduction ------------------------------------------------------------------


def test_gateway_timeout_refetches_the_same_page_with_a_halved_page_size(rate_limit_mock_response, requests_mock):
    """The behavior Step 9 depends on. The legacy handler halved `stream.page_size` and
    returned RETRY, but HttpClient replays the same PreparedRequest, so the reduced size never
    reached GitHub for the failing page. Here the request is rebuilt."""
    _mock_repository_resolution(requests_mock)
    requests_mock.post(
        GRAPHQL_URL,
        [
            {"status_code": 504, "json": {"message": "Gateway Timeout"}},
            {"json": _repository_envelope("releases", [_release_node()])},
        ],
    )

    records, error = _read(_config(), "releases")

    assert error is None
    assert len(records) == 1
    requests = _graphql_requests(requests_mock)
    assert len(requests) == 2
    assert _variables(requests[0])["first"] == 10
    assert _variables(requests[1])["first"] == 5
    # Same page: neither request carries a cursor, so no records were skipped over.
    assert "after" not in _variables(requests[0])
    assert "after" not in _variables(requests[1])


@pytest.mark.parametrize("status_code", [502, 504])
def test_both_gateway_statuses_trigger_reduction(status_code, rate_limit_mock_response, requests_mock):
    _mock_repository_resolution(requests_mock)
    requests_mock.post(
        GRAPHQL_URL,
        [
            {"status_code": status_code, "json": {"message": "error"}},
            {"json": _repository_envelope("releases", [_release_node()])},
        ],
    )

    records, error = _read(_config(), "releases")

    assert error is None
    assert len(records) == 1
    assert _variables(_graphql_requests(requests_mock)[1])["first"] == 5


def test_reduction_repeats_until_the_page_succeeds(rate_limit_mock_response, requests_mock):
    _mock_repository_resolution(requests_mock)
    requests_mock.post(
        GRAPHQL_URL,
        [
            {"status_code": 504, "json": {"message": "Gateway Timeout"}},
            {"status_code": 504, "json": {"message": "Gateway Timeout"}},
            {"json": _repository_envelope("releases", [_release_node()])},
        ],
    )

    records, error = _read(_config(), "releases")

    assert error is None
    assert len(records) == 1
    assert [_variables(request)["first"] for request in _graphql_requests(requests_mock)] == [10, 5, 2]


def test_reduced_page_size_is_kept_for_the_following_page(rate_limit_mock_response, requests_mock):
    """`reset_policy: NEVER`. Restoring the configured size after a good page would re-trigger
    the timeout on every subsequent page, which is what the legacy handler did."""
    _mock_repository_resolution(requests_mock)
    requests_mock.post(
        GRAPHQL_URL,
        [
            {"status_code": 504, "json": {"message": "Gateway Timeout"}},
            {"json": _repository_envelope("releases", [_release_node("RE_1", 11, "v1")], has_next_page=True, end_cursor="CURSOR")},
            {"json": _repository_envelope("releases", [_release_node("RE_2", 12, "v2")])},
        ],
    )

    records, error = _read(_config(), "releases")

    assert error is None
    assert len(records) == 2
    assert [_variables(request)["first"] for request in _graphql_requests(requests_mock)] == [10, 5, 5]


def test_persistent_gateway_timeout_fails_the_stream_instead_of_looping(rate_limit_mock_response, requests_mock):
    """`max_attempts: 5` with `minimum_page_size: 1` bounds the reduction. Without a bound a
    permanently timing-out repository would request forever."""
    _mock_repository_resolution(requests_mock)
    requests_mock.post(GRAPHQL_URL, status_code=504, json={"message": "Gateway Timeout"})

    records, error = _read(_config(), "releases")

    assert records == []
    sizes = [_variables(request)["first"] for request in _graphql_requests(requests_mock)]
    # 10 -> 5 -> 2 -> 1, then the floor is reached and the stream gives up.
    assert sizes == [10, 5, 2, 1]


def test_page_size_for_large_streams_config_is_still_honored(rate_limit_mock_response, requests_mock):
    """The deprecated knob keeps working; reduction starts from whatever it set."""
    _mock_repository_resolution(requests_mock)
    requests_mock.post(
        GRAPHQL_URL,
        [
            {"status_code": 504, "json": {"message": "Gateway Timeout"}},
            {"json": _repository_envelope("releases", [_release_node()])},
        ],
    )

    _read(_config(page_size_for_large_streams=40), "releases")

    assert [_variables(request)["first"] for request in _graphql_requests(requests_mock)] == [40, 20]


# --- ProjectsV2 --------------------------------------------------------------------------


def test_projects_v2_flattens_owner_and_stamps_repository(rate_limit_mock_response, requests_mock):
    _mock_repository_resolution(requests_mock)
    node = {
        "node_id": "PVT_1",
        "id": 5,
        "number": 1,
        "title": "board",
        "updated_at": "2022-05-05T00:00:00Z",
        "created_at": "2022-05-01T00:00:00Z",
        "closed": False,
        "owner": {"id": "O_1"},
    }
    requests_mock.post(GRAPHQL_URL, json=_repository_envelope("projectsV2", [node]))

    records, error = _read(_config(), "projects_v2")

    assert error is None
    assert len(records) == 1
    assert records[0]["owner_id"] == "O_1"
    assert records[0]["repository"] == REPOSITORY
    assert "owner" not in records[0]


def test_projects_v2_uses_the_default_page_size(rate_limit_mock_response, requests_mock):
    """Not a `large_stream` in the Python code, so it keeps constants.DEFAULT_PAGE_SIZE."""
    _mock_repository_resolution(requests_mock)
    requests_mock.post(GRAPHQL_URL, json=_repository_envelope("projectsV2", []))

    _read(_config(page_size_for_large_streams=10), "projects_v2")

    assert _variables(_graphql_requests(requests_mock)[0])["first"] == 100


# --- PullRequestStats ----------------------------------------------------------------------


def test_pull_request_stats_aggregates_the_connection_counts(rate_limit_mock_response, requests_mock):
    _mock_repository_resolution(requests_mock)
    node = {
        "node_id": "PR_1",
        "id": 21,
        "number": 3,
        "updated_at": "2022-06-06T00:00:00Z",
        "changed_files": 4,
        "deletions": 1,
        "additions": 2,
        "merged": True,
        "mergeable": "MERGEABLE",
        "comments": {"totalCount": 6},
        "commits": {"totalCount": 9},
        "review_comments": {"totalCount": 2, "nodes": [{"comments": {"totalCount": 3}}, {"comments": {"totalCount": 4}}]},
        # The query aliases `__typename` to `type`, matching the legacy record shape.
        "merged_by": {"type": "User", "node_id": "U_1", "id": 7, "login": "octocat"},
    }
    requests_mock.post(GRAPHQL_URL, json=_repository_envelope("pullRequests", [node]))

    records, error = _read(_config(), "pull_request_stats")

    assert error is None
    assert len(records) == 1
    record = records[0]
    # The Python stream summed the per-review comment counts rather than taking totalCount.
    assert record["review_comments"] == 7
    assert record["comments"] == 6
    assert record["commits"] == 9
    assert record["repository"] == REPOSITORY
    assert record["merged_by"]["type"] == "User"
    assert "__typename" not in record["merged_by"]
    assert record["merged_by"]["id"] == 7


def test_pull_request_stats_leaves_merged_by_null_when_not_merged(rate_limit_mock_response, requests_mock):
    """Writing `type` into a null `merged_by` would materialize an object where the legacy
    record had null."""
    _mock_repository_resolution(requests_mock)
    node = {
        "node_id": "PR_2",
        "id": 22,
        "number": 4,
        "updated_at": "2022-06-07T00:00:00Z",
        "comments": {"totalCount": 0},
        "commits": {"totalCount": 1},
        "review_comments": {"totalCount": 0, "nodes": []},
        "merged_by": None,
    }
    requests_mock.post(GRAPHQL_URL, json=_repository_envelope("pullRequests", [node]))

    records, error = _read(_config(), "pull_request_stats")

    assert error is None
    assert records[0]["merged_by"] is None
    assert records[0]["review_comments"] == 0


# --- Shared behavior ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("stream_name", "connection"),
    [("releases", "releases"), ("projects_v2", "projectsV2"), ("pull_request_stats", "pullRequests")],
)
def test_inaccessible_repository_ends_the_partition_without_raising(stream_name, connection, rate_limit_mock_response, requests_mock):
    """GitHub answers 200 with `data.repository: null` when the token cannot see the repo. The
    null-guarded pagination expressions must end the partition rather than raise."""
    _mock_repository_resolution(requests_mock)
    requests_mock.post(GRAPHQL_URL, json={"data": {"repository": None}})

    records, error = _read(_config(), stream_name)

    assert error is None
    assert records == []


@pytest.mark.parametrize("stream_name", ["releases", "projects_v2", "pull_request_stats"])
def test_streams_post_to_the_graphql_endpoint(stream_name, rate_limit_mock_response, requests_mock):
    _mock_repository_resolution(requests_mock)
    requests_mock.post(GRAPHQL_URL, json={"data": {"repository": None}})

    _read(_config(), stream_name)

    requests = _graphql_requests(requests_mock)
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert "query" in json.loads(requests[0].body)
