#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_github.source import SourceGithub

from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    UnionPartitionRouter as UnionPartitionRouterModel,
)
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


_CONFIG = {
    "credentials": {"access_token": "test_token"},
    "repositories": [
        "docker/*",
        "airbytehq/integration-test",
        "someuser/personal-repo",
        "docker/compose",
    ],
}


def _build_router(definition_name: str, config: dict):
    source = SourceGithub(config=config)
    definition = source.resolved_manifest["definitions"][definition_name]
    factory = ModelToComponentFactory()
    return factory.create_component(
        model_type=UnionPartitionRouterModel,
        component_definition=definition,
        config=config,
        stream_name="test_stream",
    )


def _mock_github_api(requests_mock):
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            {"id": 1, "full_name": "docker/docker-py", "owner": {"login": "docker"}},
            {"id": 2, "full_name": "docker/compose", "owner": {"login": "docker"}},
        ],
    )
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/integration-test",
        json={"id": 3, "full_name": "airbytehq/integration-test", "organization": {"login": "airbytehq"}},
    )
    requests_mock.get(
        "https://api.github.com/repos/someuser/personal-repo",
        json={"id": 4, "full_name": "someuser/personal-repo"},
    )
    requests_mock.get(
        "https://api.github.com/repos/docker/compose",
        json={"id": 2, "full_name": "docker/compose", "organization": {"login": "docker"}},
    )


def test_repository_partition_router_unions_wildcard_and_explicit_repos(rate_limit_mock_response, requests_mock):
    _mock_github_api(requests_mock)
    router = _build_router("repository_partition_router", _CONFIG)

    slices = list(router.stream_slices())
    partitions = [stream_slice.partition for stream_slice in slices]

    assert sorted(partition["repository"] for partition in partitions) == [
        "airbytehq/integration-test",
        "docker/compose",
        "docker/docker-py",
        "someuser/personal-repo",
    ]
    assert all(set(partition) == {"repository"} for partition in partitions)


def test_organization_partition_router_skips_user_owned_repos(rate_limit_mock_response, requests_mock):
    _mock_github_api(requests_mock)
    router = _build_router("organization_partition_router", _CONFIG)

    slices = list(router.stream_slices())
    partitions = [stream_slice.partition for stream_slice in slices]

    assert sorted(partition["organization"] for partition in partitions) == ["airbytehq", "docker"]
    assert all(set(partition) == {"organization"} for partition in partitions)


def test_repository_partition_router_explicit_repos_only(rate_limit_mock_response, requests_mock):
    _mock_github_api(requests_mock)
    config = {"credentials": {"access_token": "test_token"}, "repositories": ["airbytehq/integration-test"]}
    router = _build_router("repository_partition_router", config)

    partitions = [stream_slice.partition for stream_slice in router.stream_slices()]

    assert partitions == [{"repository": "airbytehq/integration-test"}]


_USER_WILDCARD_CONFIG = {
    "credentials": {"access_token": "test_token"},
    # `octocat` is a user account, not an organization: `orgs/octocat/repos` 404s, and the repo is
    # reachable only as an explicit entry.
    "repositories": ["octocat/*", "octocat/hello-world"],
}


def _mock_user_wildcard_api(requests_mock):
    requests_mock.get("https://api.github.com/orgs/octocat/repos", status_code=404, json={"message": "Not Found"})
    requests_mock.get(
        "https://api.github.com/repos/octocat/hello-world",
        json={"id": 5, "full_name": "octocat/hello-world", "owner": {"login": "octocat"}},
    )


def test_organization_resolution_router_omits_wildcard_user_login(rate_limit_mock_response, requests_mock):
    """A wildcard whose owner is a user must not produce an organization partition.

    Deriving the org from config text put `octocat` on `Organizations`, `Teams` and `Users`,
    where every request to `orgs/octocat` 404s.
    """
    _mock_user_wildcard_api(requests_mock)
    router = _build_router("organization_resolution_partition_router", _USER_WILDCARD_CONFIG)

    assert list(router.stream_slices()) == []


def test_organization_partition_router_still_attempts_wildcard_login(rate_limit_mock_response, requests_mock):
    """The `repositories` stream keeps the unverified candidate on purpose.

    It has to issue `orgs/{login}/repos` to find out whether the login is an organization;
    a 404 there is skipped by the requester's error handler.
    """
    _mock_user_wildcard_api(requests_mock)
    router = _build_router("organization_partition_router", _USER_WILDCARD_CONFIG)

    partitions = [stream_slice.partition for stream_slice in router.stream_slices()]

    assert partitions == [{"organization": "octocat"}]


def test_organization_resolution_router_keeps_payload_confirmed_orgs(rate_limit_mock_response, requests_mock):
    """A wildcard whose owner really is an org resolves through the repo listing's `owner/login`."""
    _mock_github_api(requests_mock)
    router = _build_router("organization_resolution_partition_router", _CONFIG)

    partitions = [stream_slice.partition for stream_slice in router.stream_slices()]

    assert sorted(partition["organization"] for partition in partitions) == ["airbytehq", "docker"]
    assert all(set(partition) == {"organization"} for partition in partitions)
