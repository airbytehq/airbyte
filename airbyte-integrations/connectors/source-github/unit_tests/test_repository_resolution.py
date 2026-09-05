#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import time
from unittest.mock import patch

import pytest
from source_github.source import SourceGithub

from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def _mock_rate_limit(requests_mock, api_url="https://api.github.com"):
    quota = {"remaining": 5000, "reset": int(time.time()) + 3600, "limit": 5000}
    requests_mock.get(f"{api_url}/rate_limit", json={"resources": {"core": dict(quota), "graphql": dict(quota)}})


def _resolve(config):
    """Run repository resolution the way `check_connection`/`streams()` do: config
    normalization first, then enumeration of the manifest's partition routers."""
    source = SourceGithub(config=dict(config))
    normalized = source._validate_and_transform_config(dict(config))
    return source._resolve_repositories_and_organizations(normalized)


def test_check_connection_fails_fast_when_quota_exhausted(requests_mock):
    """`check` is interactive, so an exhausted quota must return an actionable error in seconds
    rather than sleeping up to `max_waiting_time` (120 minutes by default) and surfacing as a
    platform timeout. This replaces the deleted `exit_on_rate_limit` fail-fast."""
    exhausted = {"remaining": 0, "reset": int(time.time()) + 3000, "limit": 5000}
    requests_mock.get(
        "https://api.github.com/rate_limit",
        json={"resources": {"core": dict(exhausted), "graphql": dict(exhausted)}},
    )
    source = SourceGithub(config={"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"]})

    with patch("time.sleep") as sleep_mock:
        ok, message = source.check_connection(
            logging.getLogger("airbyte"),
            {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"]},
        )

    assert ok is False
    assert "Rate limit is exceeded for all provided tokens." in message
    sleep_mock.assert_not_called()


def test_check_connection_fails_fast_when_the_server_reports_a_rate_limit(requests_mock):
    """The other rate-limit path: the local counters look healthy, the request goes out, and
    GitHub rejects it with a reset an hour away. That wait belongs to the error handler, not to
    the authenticator, so `max_waiting_time: 0` could not reach it until the manifest gained
    `max_waiting_time_in_seconds` (CDK #1123). Without the cap this check sleeps ~3600s."""
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        status_code=403,
        headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(int(time.time()) + 3600)},
        json={"message": "API rate limit exceeded for user ID 1."},
    )
    config = {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"]}
    source = SourceGithub(config=dict(config))

    with patch("time.sleep") as sleep_mock:
        ok, message = source.check_connection(logging.getLogger("airbyte"), dict(config))

    assert ok is False
    assert "rate limit" in message.lower()
    assert sleep_mock.call_count == 0 or max(call.args[0] for call in sleep_mock.call_args_list) < 60


def test_sync_still_waits_out_a_rate_limit_within_the_budget(requests_mock):
    """The cap must bound `check` without turning an ordinary sync-time rate limit into a
    failure: a two-minute wait is well inside the default 120-minute budget, so it is slept."""
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        [
            {
                "status_code": 403,
                "headers": {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(int(time.time()) + 120)},
                "json": {"message": "API rate limit exceeded for user ID 1."},
            },
            {"json": [{"id": 1, "full_name": "org/repo", "owner": {"login": "org"}}]},
        ],
    )
    config = {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"]}

    with patch("time.sleep") as sleep_mock:
        organizations, repositories = _resolve(config)

    assert repositories == ["org/repo"]
    assert organizations == ["org"]
    assert max(call.args[0] for call in sleep_mock.call_args_list) > 60


def test_transient_error_still_retries_on_the_smallest_wait_budget(requests_mock):
    """The wait cap must not turn ordinary transient errors into failures. A headerless 5xx falls
    back to the `min_wait: 60` floor, and the CDK raises at `>=`, so a user on the spec's minimum
    Max Waiting Time of 1 minute would hit a 60s cap that exactly equals that floor. Measured
    before the `+ 1` in the manifest: a single 500 failed the whole resolution."""
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        [
            {"status_code": 500, "json": {"message": "Server Error"}},
            {"json": [{"id": 1, "full_name": "org/repo", "owner": {"login": "org"}}]},
        ],
    )
    config = {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"], "max_waiting_time": 1}

    with patch("time.sleep"):
        organizations, repositories = _resolve(config)

    assert repositories == ["org/repo"]
    assert organizations == ["org"]


def test_short_wait_budget_does_not_cost_token_rotation(requests_mock):
    """A budget below the distance to the reset must not stop a sync that had a spare token.

    Rotating is the same retry, seconds from now, on a credential with quota — strictly better
    than ending the stream. This is the end-to-end proof of the CDK fix: it exercises the real
    manifest, the real authenticator and the real capped strategy together.

    Passes only on a CDK carrying airbytehq/airbyte-python-cdk#1126. It was xfail(strict) against
    7.28.0, where the cap raised before rotation was considered, and turned red the moment the
    prerelease of that fix was pinned — which is what removed the marker.
    """
    reset_at = int(time.time()) + 3600
    quota = {"remaining": 5000, "reset": reset_at, "limit": 5000}
    requests_mock.get("https://api.github.com/rate_limit", json={"resources": {"core": dict(quota), "graphql": dict(quota)}})
    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        [
            {
                "status_code": 403,
                "headers": {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(reset_at)},
                "json": {"message": "API rate limit exceeded for user ID 1."},
            },
            {"json": [{"id": 1, "full_name": "org/repo", "owner": {"login": "org"}}]},
        ],
    )
    config = {
        "credentials": {"personal_access_token": "token1,token2"},
        "repositories": ["org/*"],
        "max_waiting_time": 30,
    }

    with patch("time.sleep") as sleep_mock:
        organizations, repositories = _resolve(config)

    assert repositories == ["org/repo"]
    assert organizations == ["org"]
    # The 0.1s rotation retry, not a wait for the reset and not a failure.
    assert max(call.args[0] for call in sleep_mock.call_args_list) < 60


def test_check_retries_a_transient_error_instead_of_reporting_a_rate_limit(requests_mock):
    """`check` must survive one GitHub blip. Its wait budget has to stay above the `min_wait: 60`
    floor that `WaitUntilTimeFromHeader` returns for any retryable response without rate-limit
    headers, or the cap refuses that floor and a 500 fails the connection test on the first
    attempt — reported as "The rate limit wait time is longer than the connector is allowed to
    wait." Measured with `max_waiting_time: 0` in `check_config`: exactly that, one attempt."""
    _mock_rate_limit(requests_mock)
    listing = requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        [
            {"status_code": 500, "json": {"message": "Server Error"}},
            {"json": [{"id": 1, "full_name": "org/repo", "owner": {"login": "org"}}]},
        ],
    )
    config = {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"]}

    with patch("time.sleep"):
        ok, message = SourceGithub(config=dict(config)).check_connection(logging.getLogger("airbyte"), dict(config))

    assert (ok, message) == (True, None)
    assert listing.call_count == 2


def test_check_still_fails_fast_when_the_server_reports_a_rate_limit_after_the_retry_fix(requests_mock):
    """The companion guard to the test above: giving `check` a budget instead of zero must not
    bring back the sleep it exists to prevent. A reset an hour out is still refused immediately."""
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        status_code=403,
        headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(int(time.time()) + 3600)},
        json={"message": "API rate limit exceeded for user ID 1."},
    )
    config = {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"]}

    with patch("time.sleep") as sleep_mock:
        ok, message = SourceGithub(config=dict(config)).check_connection(logging.getLogger("airbyte"), dict(config))

    assert ok is False
    assert "rate limit" in message.lower()
    assert sleep_mock.call_count == 0 or max(call.args[0] for call in sleep_mock.call_args_list) < 62


def test_wildcard_with_an_interior_star_is_expanded(requests_mock):
    """A `*` anywhere in the repo part is a pattern, which is what the legacy Python resolver did.
    While `wildcard_organizations` anchored the star to the end of the entry, an interior-star
    entry matched neither that expression nor the explicit-repo list (`^([^*]+)$`), so it was
    dropped with no request and no warning."""
    _mock_rate_limit(requests_mock)
    listing = requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        json=[
            {"id": 1, "full_name": "org/pre-a-fix", "owner": {"login": "org"}},
            {"id": 2, "full_name": "org/unrelated", "owner": {"login": "org"}},
        ],
    )
    config = {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/pre*fix"]}

    organizations, repositories = _resolve(config)

    assert repositories == ["org/pre-a-fix"]
    assert organizations == ["org"]
    assert listing.call_count == 1


@pytest.mark.parametrize(
    "num_workers",
    [pytest.param(v, id=i) for v, i in [(None, "null"), (1, "spec_minimum"), (4, "spec_default"), (25, "spec_maximum")]],
)
def test_every_num_workers_the_spec_allows_builds(requests_mock, num_workers):
    """`num_workers` feeds `concurrency_level.default_concurrency`, which the CDK resolves while
    the source is being constructed — so a value it cannot render fails every command, `spec`
    included. Null is the case that bit: it renders as "None" and raised `ValueError:
    default_concurrency did not evaluate to an integer`."""
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["org/repo"],
        "num_workers": num_workers,
    }

    source = SourceGithub(config=dict(config))

    assert source.spec(logging.getLogger("airbyte")).connectionSpecification["properties"]["num_workers"]["default"] == 4


def test_github_enterprise_with_rate_limiting_disabled_still_resolves(requests_mock):
    """GHES ships with HTTP API rate limiting off and answers /rate_limit with 404. Quota
    seeding runs before the first stream request, so that 404 used to fail every command;
    `unavailable_status_codes: [404]` seeds the token untracked instead (CDK #1121)."""
    api_url = "https://github.example.com/api/v3"
    requests_mock.get(f"{api_url}/rate_limit", status_code=404, json={"message": "Rate limiting is not enabled."})
    requests_mock.get(
        f"{api_url}/orgs/org/repos",
        json=[{"id": 1, "full_name": "org/repo", "owner": {"login": "org"}}],
    )
    config = {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"], "api_url": api_url}

    organizations, repositories = _resolve(config)

    assert repositories == ["org/repo"]
    assert organizations == ["org"]


def test_rate_limit_404_on_github_dot_com_is_not_swallowed_into_a_broken_sync(requests_mock):
    """The opt-in is scoped to the quota endpoint, so a 404 from a stream still means what it
    always meant — the org does not exist — and resolution yields nothing rather than pretending
    it succeeded."""
    requests_mock.get("https://api.github.com/rate_limit", status_code=404, json={"message": "Rate limiting is not enabled."})
    requests_mock.get("https://api.github.com/orgs/org/repos", status_code=404, json={"message": "Not Found"})
    config = {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"]}

    organizations, repositories = _resolve(config)

    assert repositories == []
    assert organizations == []


@pytest.mark.parametrize(
    "max_waiting_time_config",
    [
        pytest.param({}, id="absent"),
        pytest.param({"max_waiting_time": None}, id="null"),
        pytest.param({"max_waiting_time": 0}, id="zero"),
        pytest.param({"max_waiting_time": 1}, id="spec_minimum"),
        pytest.param({"max_waiting_time": 240}, id="spec_maximum"),
    ],
)
def test_every_max_waiting_time_the_spec_allows_builds(requests_mock, max_waiting_time_config):
    """`max_waiting_time` reaches three interpolations — the authenticator's `max_wait_time` and
    the two backoff caps — and CDK 7.28.1 resolves the caps when the strategy is constructed, so a
    value one of them cannot render fails every command rather than one retry. Null is the case
    that bit: it renders as an empty string, so `config.get('max_waiting_time', 120)` produced
    "PTM" and the source would not build. Zero must keep working too, since `check_connection`
    passes it deliberately.
    """
    quota = {"remaining": 5000, "reset": int(time.time()) + 3600, "limit": 5000}
    requests_mock.get("https://api.github.com/rate_limit", json={"resources": {"core": dict(quota), "graphql": dict(quota)}})
    requests_mock.get(
        "https://api.github.com/repos/org/repo",
        json={"full_name": "org/repo", "organization": {"login": "org"}},
    )
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["org/repo"],
        **max_waiting_time_config,
    }

    source = SourceGithub(config=dict(config))
    python_stream = source.streams(config)[0]
    streams = ConcurrentDeclarativeSource.streams(source, config)

    assert [stream.name for stream in streams] == ["repositories"]
    max_waiting_time = max_waiting_time_config.get("max_waiting_time")
    expected_wait_time = max_waiting_time if max_waiting_time is not None else 120
    assert python_stream.max_wait_time_seconds == expected_wait_time * 60


def test_resolution_raises_on_no_tokens():
    config = {"credentials": {}, "repositories": ["org/repo"]}
    with pytest.raises(AirbyteTracedException, match="No authentication tokens found"):
        _resolve(config)


def test_resolution_explicit_repos(requests_mock):
    """Explicit repos are validated via `GET /repos/{name}`; org derived from `organization.login`."""
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/airbyte",
        json={"full_name": "airbytehq/airbyte", "organization": {"login": "airbytehq"}},
    )
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/cdk",
        json={"full_name": "airbytehq/cdk", "organization": {"login": "airbytehq"}},
    )

    organizations, repositories = _resolve(
        {"credentials": {"personal_access_token": "test_token"}, "repositories": ["airbytehq/airbyte", "airbytehq/cdk"]}
    )

    assert repositories == ["airbytehq/airbyte", "airbytehq/cdk"]
    assert organizations == ["airbytehq"]


def test_resolution_user_owned_repo_registers_no_organization(requests_mock):
    """User-owned repos contribute a repository but no organization partition."""
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/repos/someuser/repo",
        json={"full_name": "someuser/repo", "owner": {"login": "someuser", "type": "User"}},
    )

    organizations, repositories = _resolve({"credentials": {"personal_access_token": "test_token"}, "repositories": ["someuser/repo"]})

    assert repositories == ["someuser/repo"]
    assert organizations == []


def test_resolution_wildcard_orgs(requests_mock):
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            {"full_name": "docker/docker-py", "owner": {"login": "docker"}},
            {"full_name": "docker/compose", "owner": {"login": "docker"}},
        ],
    )

    organizations, repositories = _resolve({"credentials": {"personal_access_token": "test_token"}, "repositories": ["docker/*"]})

    assert repositories == ["docker/compose", "docker/docker-py"]
    assert organizations == ["docker"]


def test_resolution_mixed_explicit_and_wildcard(requests_mock):
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            {"full_name": "docker/docker-py", "owner": {"login": "docker"}},
            {"full_name": "docker/compose", "owner": {"login": "docker"}},
        ],
    )
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/airbyte",
        json={"full_name": "airbytehq/airbyte", "organization": {"login": "airbytehq"}},
    )

    organizations, repositories = _resolve(
        {"credentials": {"personal_access_token": "test_token"}, "repositories": ["airbytehq/airbyte", "docker/*"]}
    )

    assert repositories == ["airbytehq/airbyte", "docker/compose", "docker/docker-py"]
    assert organizations == ["airbytehq", "docker"]


def test_resolution_wildcard_pattern_filtering(requests_mock):
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        json=[
            {"full_name": "org/source-github", "owner": {"login": "org"}},
            {"full_name": "org/source-mysql", "owner": {"login": "org"}},
            {"full_name": "org/destination-postgres", "owner": {"login": "org"}},
        ],
    )

    organizations, repositories = _resolve({"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/source-*"]})

    assert repositories == ["org/source-github", "org/source-mysql"]
    assert "org/destination-postgres" not in repositories


def test_resolution_skip_404_repo(requests_mock):
    """Explicit repos that 404 are skipped with a warning instead of failing resolution."""
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/repos/org/missing-repo",
        json={"message": "Not Found"},
        status_code=404,
    )

    organizations, repositories = _resolve({"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/missing-repo"]})

    assert repositories == []
    assert organizations == []


def test_resolution_skip_404_org(requests_mock):
    _mock_rate_limit(requests_mock)
    requests_mock.get(
        "https://api.github.com/orgs/missing-org/repos",
        json={"message": "Not Found"},
        status_code=404,
    )

    organizations, repositories = _resolve({"credentials": {"personal_access_token": "test_token"}, "repositories": ["missing-org/*"]})

    assert repositories == []
    assert organizations == []


def test_resolution_custom_api_url(requests_mock):
    api_url = "https://github.example.com/api/v3"
    _mock_rate_limit(requests_mock, api_url)
    requests_mock.get(
        f"{api_url}/repos/org/repo",
        json={"full_name": "org/repo", "organization": {"login": "org"}},
    )

    organizations, repositories = _resolve(
        {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/repo"], "api_url": api_url}
    )

    assert repositories == ["org/repo"]
    assert organizations == ["org"]


def test_resolution_legacy_repository_field(requests_mock):
    """Legacy space-delimited `repository` field is normalized by
    `_validate_and_transform_config` before resolution and validated."""
    _mock_rate_limit(requests_mock)
    for repo in ("org/repo1", "org/repo2"):
        requests_mock.get(
            f"https://api.github.com/repos/{repo}",
            json={"full_name": repo, "organization": {"login": "org"}},
        )

    organizations, repositories = _resolve({"credentials": {"personal_access_token": "test_token"}, "repository": "org/repo1 org/repo2"})

    assert repositories == ["org/repo1", "org/repo2"]
    assert organizations == ["org"]


def _next_link(page):
    return {"Link": f'<https://api.github.com/orgs/org/repos?page={page}>; rel="next"'}


def test_resolution_pagination(requests_mock):
    """Wildcard expansion follows GitHub's `rel="next"` link header to the next page."""
    _mock_rate_limit(requests_mock)
    page1 = [{"full_name": f"org/repo{i}", "owner": {"login": "org"}} for i in range(100)]
    page2 = [{"full_name": "org/repo100", "owner": {"login": "org"}}]

    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        [{"json": page1, "headers": _next_link(2)}, {"json": page2}],
    )

    organizations, repositories = _resolve({"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"]})

    assert len(repositories) == 101
    assert "org/repo100" in repositories
    assert organizations == ["org"]


def test_resolution_pagination_with_pattern_filter(requests_mock):
    """A page whose records mostly fail the wildcard filter must still advance while GitHub
    advertises a next link: pagination is driven by the link header, not by how many records
    survived the filter. Wildcard expansion feeds every repo-scoped partition, so stopping early
    here would silently drop repositories from every downstream stream."""
    _mock_rate_limit(requests_mock)
    page1 = [{"full_name": "org/source-github", "owner": {"login": "org"}}] + [
        {"full_name": f"org/destination-{i}", "owner": {"login": "org"}} for i in range(99)
    ]
    page2 = [{"full_name": "org/source-mysql", "owner": {"login": "org"}}]

    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        [{"json": page1, "headers": _next_link(2)}, {"json": page2}],
    )

    organizations, repositories = _resolve({"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/source-*"]})

    assert repositories == ["org/source-github", "org/source-mysql"]
    assert organizations == ["org"]


def test_resolution_stops_without_next_link(requests_mock):
    """A full page with no next link is the last page — GitHub's documented end-of-data signal."""
    _mock_rate_limit(requests_mock)
    page1 = [{"full_name": f"org/repo{i}", "owner": {"login": "org"}} for i in range(100)]

    listing = requests_mock.get("https://api.github.com/orgs/org/repos", [{"json": page1}])

    _, repositories = _resolve({"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/*"]})

    assert len(repositories) == 100
    assert listing.call_count == 1


def test_wildcard_on_user_account_resolves_no_organization(requests_mock):
    """A wildcard naming a user account contributes repositories but no organization.

    `orgs/{user}/repos` 404s, so the wildcard expands to nothing and the repo is reachable
    only through its explicit entry. Handing `octocat` to the org-scoped streams anyway made
    every `orgs/octocat` request 404, and the swallowed 404 on those full-refresh streams
    retried the same partition until the platform's source heartbeat killed the sync. The
    legacy resolver collected orgs from fetched repo metadata, which is why 2.1.x synced this
    config fine."""
    _mock_rate_limit(requests_mock)
    requests_mock.get("https://api.github.com/orgs/octocat/repos", status_code=404, json={"message": "Not Found"})
    requests_mock.get(
        "https://api.github.com/repos/octocat/hello-world",
        json={"full_name": "octocat/hello-world", "owner": {"login": "octocat"}},
    )

    organizations, repositories = _resolve(
        {"credentials": {"personal_access_token": "test_token"}, "repositories": ["octocat/*", "octocat/hello-world"]}
    )

    assert repositories == ["octocat/hello-world"]
    assert organizations == []
