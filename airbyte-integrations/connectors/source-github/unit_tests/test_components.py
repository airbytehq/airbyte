#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_github.components import RepositoryListResolver

from airbyte_cdk.utils.traced_exception import AirbyteTracedException


@pytest.mark.parametrize(
    "config,expected_tokens",
    [
        pytest.param(
            {"access_token": "tok1"},
            ["tok1"],
            id="legacy_root_access_token",
        ),
        pytest.param(
            {"credentials": {"access_token": "tok2"}},
            ["tok2"],
            id="oauth_access_token",
        ),
        pytest.param(
            {"credentials": {"personal_access_token": "tok3,tok4"}},
            ["tok3", "tok4"],
            id="multiple_pats",
        ),
        pytest.param(
            {"credentials": {"personal_access_token": "  tok5 , tok6 "}},
            ["tok5", "tok6"],
            id="pats_with_whitespace",
        ),
        pytest.param(
            {"credentials": {}},
            [],
            id="no_tokens",
        ),
    ],
)
def test_extract_tokens(config, expected_tokens):
    tokens = RepositoryListResolver._extract_tokens(config)
    assert tokens == expected_tokens


def test_transform_raises_on_no_tokens():
    resolver = RepositoryListResolver(parameters={})
    config = {"credentials": {}, "repositories": ["org/repo"]}
    with pytest.raises(AirbyteTracedException, match="No authentication tokens found"):
        resolver.transform(config)


def test_transform_explicit_repos():
    """Explicit repos are trusted without HTTP validation; orgs derived from name."""
    resolver = RepositoryListResolver(parameters={})
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["airbytehq/airbyte", "airbytehq/cdk"],
    }
    resolver.transform(config)

    assert set(config["_resolved_repositories"]) == {"airbytehq/airbyte", "airbytehq/cdk"}
    assert set(config["_resolved_organizations"]) == {"airbytehq"}
    assert config["_repository_pattern"] == ""


def test_transform_wildcard_orgs(requests_mock):
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            {"full_name": "docker/docker-py", "owner": {"login": "docker"}},
            {"full_name": "docker/compose", "owner": {"login": "docker"}},
        ],
    )

    resolver = RepositoryListResolver(parameters={})
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["docker/*"],
    }
    resolver.transform(config)

    assert set(config["_resolved_repositories"]) == {"docker/docker-py", "docker/compose"}
    assert set(config["_resolved_organizations"]) == {"docker"}
    assert config["_repository_pattern"] == "(docker/.*)"


def test_transform_mixed_explicit_and_wildcard(requests_mock):
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            {"full_name": "docker/docker-py", "owner": {"login": "docker"}},
            {"full_name": "docker/compose", "owner": {"login": "docker"}},
        ],
    )

    resolver = RepositoryListResolver(parameters={})
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["airbytehq/airbyte", "docker/*"],
    }
    resolver.transform(config)

    assert set(config["_resolved_repositories"]) == {"airbytehq/airbyte", "docker/docker-py", "docker/compose"}
    assert set(config["_resolved_organizations"]) == {"airbytehq", "docker"}


def test_transform_wildcard_pattern_filtering(requests_mock):
    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        json=[
            {"full_name": "org/source-github", "owner": {"login": "org"}},
            {"full_name": "org/source-mysql", "owner": {"login": "org"}},
            {"full_name": "org/destination-postgres", "owner": {"login": "org"}},
        ],
    )

    resolver = RepositoryListResolver(parameters={})
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["org/source-*"],
    }
    resolver.transform(config)

    assert set(config["_resolved_repositories"]) == {"org/source-github", "org/source-mysql"}
    assert "org/destination-postgres" not in config["_resolved_repositories"]


def test_transform_explicit_repos_trusted():
    """Explicit repos are added without HTTP validation; even non-existent repos are trusted."""
    resolver = RepositoryListResolver(parameters={})
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["org/missing-repo"],
    }
    resolver.transform(config)

    assert config["_resolved_repositories"] == ["org/missing-repo"]
    assert config["_resolved_organizations"] == ["org"]


def test_transform_skip_404_org(requests_mock):
    requests_mock.get(
        "https://api.github.com/orgs/missing-org/repos",
        json={"message": "Not Found"},
        status_code=404,
    )

    resolver = RepositoryListResolver(parameters={})
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["missing-org/*"],
    }
    resolver.transform(config)

    assert config["_resolved_repositories"] == []
    assert config["_resolved_organizations"] == []


def test_transform_custom_api_url():
    """Custom API URL is stored but explicit repos don't need HTTP calls."""
    resolver = RepositoryListResolver(parameters={})
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["org/repo"],
        "api_url": "https://github.example.com/api/v3",
    }
    resolver.transform(config)

    assert config["_resolved_repositories"] == ["org/repo"]


def test_transform_legacy_repository_field():
    """Legacy space-delimited `repository` field is parsed without HTTP calls."""
    resolver = RepositoryListResolver(parameters={})
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repository": "org/repo1 org/repo2",
    }
    resolver.transform(config)

    assert set(config["_resolved_repositories"]) == {"org/repo1", "org/repo2"}


def test_transform_pagination(requests_mock):
    page1 = [{"full_name": f"org/repo{i}", "owner": {"login": "org"}} for i in range(100)]
    page2 = [{"full_name": "org/repo100", "owner": {"login": "org"}}]

    requests_mock.get(
        "https://api.github.com/orgs/org/repos",
        json=page1,
        headers={"Link": '<https://api.github.com/orgs/org/repos?page=2>; rel="next"'},
    )
    requests_mock.get(
        "https://api.github.com/orgs/org/repos?page=2",
        json=page2,
    )

    resolver = RepositoryListResolver(parameters={})
    config = {
        "credentials": {"personal_access_token": "test_token"},
        "repositories": ["org/*"],
    }
    resolver.transform(config)

    assert len(config["_resolved_repositories"]) == 101
    assert "org/repo100" in config["_resolved_repositories"]
