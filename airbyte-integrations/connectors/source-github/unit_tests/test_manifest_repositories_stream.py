#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import time
from unittest.mock import patch

from source_github.source import SourceGithub

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    Type,
)


def _repo(repo_id, full_name, org=None, updated_at="2026-01-01T00:00:00Z"):
    """Build a repository payload.

    `org` adds the `organization` object that only the *single-repo* endpoint
    (`GET /repos/{owner}/{repo}`) returns; the org listing response (GitHub's Minimal
    Repository) has no such field. Listing mocks therefore omit it on purpose, so the
    `organization` value on emitted records can only come from the AddFields transformation.
    """
    record = {
        "id": repo_id,
        "full_name": full_name,
        "owner": {"login": full_name.split("/")[0]},
        "updated_at": updated_at,
        "created_at": "2020-01-01T00:00:00Z",
        "pushed_at": updated_at,
    }
    if org:
        record["organization"] = {"login": org}
    return record


def _next_link(url):
    return {"Link": f'<{url}>; rel="next"'}


def _catalog():
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="repositories",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )


def _names(records):
    return [record["full_name"] for record in records]


def _read_messages(config, state=None):
    catalog = _catalog()
    source = SourceGithub(config=dict(config), catalog=catalog, state=state)
    return list(source.read(logging.getLogger("airbyte"), dict(config), catalog, state or []))


def _read(config, state=None):
    catalog = _catalog()
    source = SourceGithub(config=dict(config), catalog=catalog, state=state)
    records, statuses, error = [], [], None
    try:
        for message in source.read(logging.getLogger("airbyte"), dict(config), catalog, state or []):
            if message.type == Type.RECORD:
                records.append(message.record.data)
            if message.type == Type.TRACE and message.trace.stream_status:
                statuses.append(message.trace.stream_status.status.value)
    except Exception as exc:  # noqa: BLE001 - the assertions inspect the failure
        error = exc
    return records, statuses, error


def _error_messages(config, state=None):
    """The user-facing failure text, which is what the platform surfaces.

    `HttpClient` puts a matched filter's `error_message` on the exception's `message` and the
    generic request dump on `internal_message` (http_client.py), and only the latter survives
    into `str(exception)` once the concurrent source aggregates stream failures. Asserting on
    the exception string therefore cannot tell a curated message from the CDK default -- read
    the emitted TRACE errors instead.
    """
    catalog = _catalog()
    source = SourceGithub(config=dict(config), catalog=catalog, state=state)
    messages = []
    try:
        for message in source.read(logging.getLogger("airbyte"), dict(config), catalog, state or []):
            if message.type == Type.TRACE and message.trace.error:
                messages.append(message.trace.error.message or "")
    except Exception:  # noqa: BLE001 - the failure itself is asserted through the trace messages
        pass
    return messages


def test_org_404_is_skipped_and_sync_completes(rate_limit_mock_response, requests_mock):
    """A 404 on one org (renamed/deleted) must not fail the sync for the remaining orgs."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["ghost-org/*", "airbytehq/*"]}
    requests_mock.get("https://api.github.com/orgs/ghost-org/repos", status_code=404, json={"message": "Not Found"})
    requests_mock.get("https://api.github.com/orgs/airbytehq/repos", json=[_repo(1, "airbytehq/airbyte")])

    records, statuses, error = _read(config)

    assert error is None
    assert _names(records) == ["airbytehq/airbyte"]
    # AddFields overwrites the payload with the partition's org login (a plain string, as in
    # the legacy transform). The listing mock carries no `organization`, so this only passes
    # while the transformation is wired.
    assert [record["organization"] for record in records] == ["airbytehq"]
    assert statuses[-1] == "COMPLETE"


def test_explicit_repo_404_is_skipped_and_sync_completes(rate_limit_mock_response, requests_mock):
    """A deleted explicit repo 404s during partition generation and must be skipped, not fail the sync."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/compose", "ghost/deleted-repo"]}
    requests_mock.get("https://api.github.com/repos/docker/compose", json=_repo(2, "docker/compose", org="docker"))
    requests_mock.get("https://api.github.com/repos/ghost/deleted-repo", status_code=404, json={"message": "Not Found"})
    requests_mock.get("https://api.github.com/orgs/docker/repos", json=[_repo(2, "docker/compose")])

    records, statuses, error = _read(config)

    assert error is None
    assert sorted(set(_names(records))) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"


@patch("time.sleep")
def test_secondary_rate_limit_is_retried(sleep_mock, rate_limit_mock_response, requests_mock):
    """GitHub secondary rate limits arrive as 403 + Retry-After and must be waited out, not failed."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        [
            {
                "status_code": 403,
                "headers": {"Retry-After": "120"},
                "json": {"message": "You have exceeded a secondary rate limit"},
            },
            {"json": [_repo(2, "docker/compose")]},
        ],
    )

    records, statuses, error = _read(config)

    assert error is None
    assert _names(records) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"
    # The wait came from `Retry-After`, which takes precedence over the X-RateLimit-Reset strategy.
    assert max(call.args[0] for call in sleep_mock.call_args_list) > 100


@patch("time.sleep")
def test_secondary_rate_limit_without_retry_after_is_retried(sleep_mock, rate_limit_mock_response, requests_mock):
    """GitHub does not always send `Retry-After` on secondary-limit 403s; the message alone must
    classify the response as rate limited rather than as a scopes/SSO config error. Secondary limits
    are tracked separately from the primary quota, so `X-RateLimit-Remaining` is still non-zero."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        [
            {
                "status_code": 403,
                "headers": {"X-RateLimit-Remaining": "4999", "X-RateLimit-Reset": "0"},
                "json": {"message": "You have exceeded a secondary rate limit. Please wait a few minutes before you try again."},
            },
            {"json": [_repo(2, "docker/compose")]},
        ],
    )

    records, statuses, error = _read(config)

    assert error is None
    assert _names(records) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"


@patch("time.sleep")
def test_exhausted_quota_error_without_retry_after_is_retried(sleep_mock, rate_limit_mock_response, requests_mock):
    """Legacy retried any non-200 carrying `X-RateLimit-Remaining: 0` (errors_handlers.py), which is
    also the fallback GitHub's docs prescribe when `Retry-After` is absent. Such a 403 must be waited
    out even when its message matches neither documented rate-limit wording."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        [
            {
                "status_code": 403,
                "headers": {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "0"},
                "json": {"message": "Forbidden"},
            },
            {"json": [_repo(2, "docker/compose")]},
        ],
    )

    records, statuses, error = _read(config)

    assert error is None
    assert _names(records) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"


@patch("time.sleep")
def test_primary_rate_limit_is_retried(sleep_mock, rate_limit_mock_response, requests_mock):
    """GitHub primary rate limits arrive as 403/429 with an "API rate limit exceeded" body and no
    `Retry-After`: the body filter must mark them RATE_LIMITED (not config_error, which the terminal
    403 filter would otherwise do) and the wait must come from `X-RateLimit-Reset`."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    reset_at = int(time.time()) + 120
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        [
            {
                "status_code": 403,
                "headers": {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(reset_at)},
                "json": {"message": "API rate limit exceeded for user ID 1."},
            },
            {"json": [_repo(2, "docker/compose")]},
        ],
    )

    records, statuses, error = _read(config)

    assert error is None
    assert _names(records) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"
    # Proves the backoff came from WaitUntilTimeFromHeader(X-RateLimit-Reset) rather than the
    # CDK's default exponential backoff, whose first interval is far below 60s.
    assert max(call.args[0] for call in sleep_mock.call_args_list) > 60


@patch("time.sleep")
def test_primary_rate_limit_rotates_instead_of_waiting_out_the_reset(sleep_mock, rate_limit_mock_response, requests_mock):
    """With a second token available, a primary rate limit must cost a rotation, not the reset
    window. `X-RateLimit-Remaining: 0` spends the rejected token's pool (CDK 7.26.0 reconciles
    pools against response headers), `HttpClient` then asks `has_alternative_token` and retries
    on the spare token immediately instead of sleeping until `X-RateLimit-Reset`.

    The reset the 403 carries matches the one /rate_limit seeded, because a response describing
    an older window than the authenticator holds is ignored on purpose; in production both come
    from the same GitHub quota window."""
    config = {"credentials": {"personal_access_token": "token1,token2"}, "repositories": ["rotationorg/*"]}
    # A real quota window, re-seeding /rate_limit over the fixture's year-2099 value: the
    # response's reset has to belong to the window the authenticator holds for the reconciliation
    # to accept its zero, and the wait it implies has to sit under the manifest's
    # `max_waiting_time_in_seconds` cap, which is what rotation is being measured against.
    seeded_reset = int(time.time()) + 3600
    quota = {"remaining": 5000, "reset": seeded_reset, "limit": 5000}
    requests_mock.get("https://api.github.com/rate_limit", json={"resources": {"core": dict(quota), "graphql": dict(quota)}})
    tokens_used = []

    def respond(request, context):
        # Recorded at call time: requests_mock's history can hand back the same mutated
        # PreparedRequest for both attempts, which would hide the rotation being asserted.
        tokens_used.append(request.headers["Authorization"])
        if len(tokens_used) == 1:
            context.status_code = 403
            context.headers.update({"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(seeded_reset)})
            return {"message": "API rate limit exceeded for user ID 1."}
        return [_repo(2, "rotationorg/compose")]

    requests_mock.get("https://api.github.com/orgs/rotationorg/repos", json=respond)

    records, statuses, error = _read(config)

    assert error is None
    assert _names(records) == ["rotationorg/compose"]
    assert statuses[-1] == "COMPLETE"
    # Which token goes first depends on rotation earlier in the sync; what matters is that the
    # retry did not re-send on the token GitHub just rejected.
    assert len(tokens_used) == 2 and tokens_used[0] != tokens_used[1]
    assert set(tokens_used) == {"token token1", "token token2"}
    # The 0.1s rotation backoff, not the 60s floor the reset-window strategy would have returned.
    assert max(call.args[0] for call in sleep_mock.call_args_list) < 60


@patch("time.sleep")
def test_rate_limit_backoff_respects_min_wait(sleep_mock, rate_limit_mock_response, requests_mock):
    """A reset timestamp already in the past must still back off for the 60s floor the legacy
    strategy enforced (backoff_strategies.py:26), not retry immediately against a quota that
    has not refilled."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        [
            {
                "status_code": 403,
                "headers": {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(int(time.time()) - 500)},
                "json": {"message": "API rate limit exceeded for user ID 1."},
            },
            {"json": [_repo(2, "docker/compose")]},
        ],
    )

    records, _, error = _read(config)

    assert error is None
    assert _names(records) == ["docker/compose"]
    assert max(call.args[0] for call in sleep_mock.call_args_list) >= 60


def test_successful_response_with_exhausted_quota_is_not_rate_limited(rate_limit_mock_response, requests_mock):
    """The request that spends the last quota point returns 200 with `X-RateLimit-Remaining: 0`.
    Its records must be kept and the request must not be retried — the response filters run before
    the CDK's success check, so a header-only rate-limit predicate would discard valid pages."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    listing = requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "0"},
        json=[_repo(2, "docker/compose")],
    )

    records, statuses, error = _read(config)

    assert error is None
    assert _names(records) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"
    assert listing.call_count == 1


def test_successful_response_carrying_retry_after_is_not_rate_limited(rate_limit_mock_response, requests_mock):
    """A 200 that merely carries `Retry-After` — GHE, a proxy or a CDN throttling on its own
    account — must be delivered as-is. Response filters are evaluated before the CDK's success
    check, so without the `http_codes: [200] -> SUCCESS` guard ahead of them the page would be
    discarded and retried until `max_retries` ran out, failing the stream."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    listing = requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        headers={"Retry-After": "30"},
        json=[_repo(2, "docker/compose")],
    )

    records, statuses, error = _read(config)

    assert error is None
    assert _names(records) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"
    assert listing.call_count == 1


def test_plain_403_fails_stream(rate_limit_mock_response, requests_mock):
    """A plain 403 (bad scopes / SAML SSO) must fail the stream so `check` can surface it, and it
    must carry the curated guidance rather than a bare status code — asserting only `"403" in
    error` would still pass if the scopes/SSO filter were dropped and the CDK default took over."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get("https://api.github.com/orgs/docker/repos", status_code=403, json={"message": "Must have admin rights"})

    records, statuses, error = _read(config)

    assert records == []
    assert error is not None
    assert "403" in str(error)
    # The curated guidance reaches the user as the TRACE error message, not as the exception
    # string. Asserting only on the latter would still pass with the scopes/SSO filter deleted.
    guidance = " ".join(_error_messages(config))
    assert "GitHub denied access (HTTP 403)" in guidance
    assert "repo, read:org, read:user, read:project, workflow" in guidance, "the curated scope list must survive"
    assert "SAML SSO" in guidance


def test_401_fails_fast_without_retrying(rate_limit_mock_response, requests_mock):
    """The migrated stream deliberately does *not* inherit the legacy `401 -> RETRY` mapping.

    `GITHUB_DEFAULT_ERROR_MAPPING` retried 401 five times, but git history shows that entry
    arrived as a copy-paste artifact of the CDK v3 migration (401/403/404/409 all identical,
    all messaged "Conflict."), and its sibling 403 was later fixed as a bug in #76090. The
    manifest declares no 401 filter, so the CDK default applies: fail once, with an actionable
    message. This test pins that contract, since retrying a bad credential only delays a config
    error while burning rate-limit quota."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    listing = requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        status_code=401,
        json={"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest"},
    )

    records, statuses, error = _read(config)

    assert records == []
    assert error is not None
    assert listing.call_count == 1, "401 must not be retried; the legacy Python path still retries it 5 times"
    guidance = " ".join(_error_messages(config))
    assert "401" in guidance and "Unauthorized" in guidance, (
        "the CDK default 401 message is the intended contract here, and it is more actionable "
        'than the legacy mapping\'s literal "Conflict."'
    )


def test_record_filter_mixed_wildcard_and_explicit_config(rate_limit_mock_response, requests_mock):
    """With wildcards present, only records matching the wildcard patterns are emitted —
    explicit repos outside the wildcard orgs drop, replicating the legacy pattern-from-wildcards behavior."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["airbytehq/*", "docker/compose"]}
    requests_mock.get("https://api.github.com/orgs/airbytehq/repos", json=[_repo(1, "airbytehq/airbyte")])
    requests_mock.get("https://api.github.com/repos/docker/compose", json=_repo(2, "docker/compose", org="docker"))
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[_repo(2, "docker/compose"), _repo(3, "docker/docker-py")],
    )

    records, _, error = _read(config)

    assert error is None
    assert sorted(set(_names(records))) == ["airbytehq/airbyte"]


def test_record_filter_explicit_only_config_emits_all_org_repos(rate_limit_mock_response, requests_mock):
    """With no wildcard patterns all repos of the explicit repos' orgs pass the filter,
    replicating the legacy `Repositories(pattern=None)` behavior."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/compose"]}
    requests_mock.get("https://api.github.com/repos/docker/compose", json=_repo(2, "docker/compose", org="docker"))
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[_repo(2, "docker/compose"), _repo(3, "docker/docker-py")],
    )

    records, _, error = _read(config)

    assert error is None
    assert sorted(set(_names(records))) == ["docker/compose", "docker/docker-py"]

    # Pin the outgoing request shape: the stop condition relies on the desc ordering, and
    # `per_page` decides which page a record lands on.
    org_listings = [request for request in requests_mock.request_history if request.path == "/orgs/docker/repos"]
    assert org_listings, "expected the repositories stream to list the org"
    for request in org_listings:
        assert request.qs["per_page"] == ["100"]
        assert request.qs["sort"] == ["updated"]
        assert request.qs["direction"] == ["desc"]
    # CursorPagination has no initial token, so the first request carries no `page` parameter
    # and GitHub defaults to page 1.
    assert "page" not in org_listings[0].qs

    repo_stats = [request for request in requests_mock.request_history if request.path == "/repos/docker/compose"]
    assert repo_stats and repo_stats[0].qs["per_page"] == ["100"]


def test_null_start_date_falls_back_to_epoch(rate_limit_mock_response, requests_mock):
    """A present-but-null `start_date` (reachable via the API/Terraform) must fall back to the
    epoch rather than reaching the cursor as the string "None" and aborting the stream."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"], "start_date": None}
    requests_mock.get("https://api.github.com/orgs/docker/repos", json=[_repo(2, "docker/compose")])

    records, statuses, error = _read(config)

    assert error is None
    assert _names(records) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"


def test_pagination_follows_link_header(rate_limit_mock_response, requests_mock):
    """Pagination must follow GitHub's `rel="next"` link and stop when it is absent."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    page1 = [_repo(index, f"docker/repo{index}") for index in range(100)]
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        [
            {"json": page1, "headers": _next_link("https://api.github.com/orgs/docker/repos?page=2")},
            {"json": [_repo(200, "docker/last")]},
        ],
    )

    records, _, error = _read(config)

    assert error is None
    assert len(records) == 101
    assert "docker/last" in _names(records)
    listings = [request for request in requests_mock.request_history if request.path == "/orgs/docker/repos"]
    assert [request.qs.get("page") for request in listings] == [None, ["2"]]


def test_short_page_with_next_link_is_followed(rate_limit_mock_response, requests_mock):
    """A page shorter than `per_page` that still carries a next link must be followed. Inferring
    end-of-data from a short page (the PageIncrement behavior this replaced) truncated the org
    listing that drives every downstream partition."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        [
            {"json": [_repo(1, "docker/a")], "headers": _next_link("https://api.github.com/orgs/docker/repos?page=2")},
            {"json": [_repo(2, "docker/b")]},
        ],
    )

    records, _, error = _read(config)

    assert error is None
    assert sorted(_names(records)) == ["docker/a", "docker/b"]


def test_legacy_state_migration_round_trip(rate_limit_mock_response, requests_mock):
    """Legacy `{org: {updated_at: ...}}` state must migrate to per-partition state and re-attach
    to the org partition."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    legacy_state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="repositories"),
                stream_state=AirbyteStateBlob({"docker": {"updated_at": "2025-06-01T00:00:00Z"}}),
            ),
        )
    ]
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            _repo(2, "docker/compose", updated_at="2026-01-01T00:00:00Z"),
            _repo(3, "docker/old-repo", updated_at="2024-01-01T00:00:00Z"),
        ],
    )

    records, statuses, error = _read(config, state=legacy_state)

    assert error is None
    # The data-feed post-pagination filter drops the boundary page's records that are at or
    # below the migrated partition cursor, so only records newer than the legacy state are
    # emitted. The migration is asserted by the emitted per-partition state below.
    assert sorted(_names(records)) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"

    migrated = [message.state for message in _read_messages(config, state=legacy_state) if message.type == Type.STATE]
    assert migrated, "the repositories stream emitted no state message"
    assert migrated[-1].stream.stream_state.states == [
        {"partition": {"organization": "docker"}, "cursor": {"updated_at": "2026-01-01T00:00:00Z"}}
    ]


def test_pagination_stops_at_cursor(rate_limit_mock_response, requests_mock):
    """The listing is served most-recent-first, so once a page ends at or below the partition
    cursor the stop condition must end pagination — this replaces the legacy
    `Repositories.is_sorted = "desc"` early break and keeps incremental syncs at ~1 request/org."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get("https://api.github.com/orgs/docker/repos", json=[_repo(999, "docker/new", updated_at="2026-06-01T00:00:00Z")])
    state = [message.state for message in _read_messages(config) if message.type == Type.STATE][-1]

    stale_page = [_repo(index, f"docker/repo{index}", updated_at="2024-01-01T00:00:00Z") for index in range(100)]
    requests_mock.reset_mock()
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        [
            {"json": stale_page, "headers": _next_link("https://api.github.com/orgs/docker/repos?page=2")},
            {"json": [_repo(200, "docker/last", updated_at="2024-01-01T00:00:00Z")]},
        ],
    )

    _, _, error = _read(config, state=[state])

    assert error is None
    listings = [request for request in requests_mock.request_history if request.path == "/orgs/docker/repos"]
    assert len(listings) == 1, "the cursor stop condition must end pagination on the first stale page"


def test_newly_added_org_filtered_by_global_cursor(rate_limit_mock_response, requests_mock):
    """An org added to `repositories` on an existing connection gets its partition seeded from
    the *global* cursor, so the data-feed filter drops its repos that predate it. Repos updated
    after the global cursor are still emitted."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get("https://api.github.com/orgs/docker/repos", json=[_repo(1, "docker/compose", updated_at="2026-01-01T00:00:00Z")])
    state = [message.state for message in _read_messages(config) if message.type == Type.STATE][-1]

    config_with_new_org = {**config, "repositories": ["docker/*", "airbytehq/*"]}
    requests_mock.get(
        "https://api.github.com/orgs/airbytehq/repos",
        json=[
            _repo(10, "airbytehq/airbyte", updated_at="2024-01-01T00:00:00Z"),
            _repo(11, "airbytehq/airbyte-platform", updated_at="2026-02-01T00:00:00Z"),
        ],
    )

    records, _, error = _read(config_with_new_org, state=[state])

    assert error is None
    assert sorted(name for name in _names(records) if name.startswith("airbytehq/")) == [
        "airbytehq/airbyte-platform",
    ]


def test_emitted_state_resumes_next_sync(rate_limit_mock_response, requests_mock):
    """The state the migrated stream emits must re-attach to the `organization` partition on the
    next sync and bound its pagination."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[_repo(2, "docker/compose", updated_at="2026-01-01T00:00:00Z")],
    )

    emitted = [message.state for message in _read_messages(config) if message.type == Type.STATE]
    assert emitted, "the migrated repositories stream emitted no state message"
    assert emitted[-1].stream.stream_state.states == [
        {"partition": {"organization": "docker"}, "cursor": {"updated_at": "2026-01-01T00:00:00Z"}}
    ]

    requests_mock.reset_mock()
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            _repo(4, "docker/new-repo", updated_at="2026-06-01T00:00:00Z"),
            _repo(3, "docker/old-repo", updated_at="2024-01-01T00:00:00Z"),
        ],
    )

    records, _, error = _read(config, state=[emitted[-1]])

    assert error is None
    assert "docker/new-repo" in _names(records)
    # A single page is fetched: the stop condition sees the page ending below the resumed
    # cursor, so the sync does not walk the rest of the listing.
    assert len([request for request in requests_mock.request_history if request.path == "/orgs/docker/repos"]) == 1
