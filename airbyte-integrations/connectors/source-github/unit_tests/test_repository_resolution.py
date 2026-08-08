#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import time
from unittest.mock import patch

import pytest
from source_github.source import SourceGithub

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

    organizations, repositories = _resolve(
        {"credentials": {"personal_access_token": "test_token"}, "repositories": ["someuser/repo"]}
    )

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

    organizations, repositories = _resolve(
        {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/missing-repo"]}
    )

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

    organizations, repositories = _resolve(
        {"credentials": {"personal_access_token": "test_token"}, "repository": "org/repo1 org/repo2"}
    )

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

    organizations, repositories = _resolve(
        {"credentials": {"personal_access_token": "test_token"}, "repositories": ["org/source-*"]}
    )

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
