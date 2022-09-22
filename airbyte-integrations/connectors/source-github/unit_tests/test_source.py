#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from source_github.source import SourceGithub


def check_source(repo_line: str) -> AirbyteConnectionStatus:
    source = SourceGithub()
    config = {"access_token": "test_token", "repository": repo_line}
    logger_mock = MagicMock()
    return source.check(logger_mock, config)


@responses.activate
def test_check_connection_repos_only():
    responses.add("GET", "https://api.github.com/repos/airbyte", json={"full_name": "airbyte"})

    status = check_source("airbyte airbyte airbyte")
    assert not status.message
    assert status.status == Status.SUCCEEDED
    # Only one request since 3 repos have same name
    assert len(responses.calls) == 1


@responses.activate
def test_check_connection_repos_and_org_repos():
    repos = [{"name": f"name {i}", "full_name": f"full name {i}", "updated_at": "2020-01-01T00:00:00Z"} for i in range(1000)]
    responses.add(
        "GET", "https://api.github.com/repos/airbyte/test", json={"full_name": "airbyte/test", "organization": {"login": "airbyte"}}
    )
    responses.add(
        "GET", "https://api.github.com/repos/airbyte/test2", json={"full_name": "airbyte/test2", "organization": {"login": "airbyte"}}
    )
    responses.add("GET", "https://api.github.com/orgs/airbytehq/repos", json=repos)
    responses.add("GET", "https://api.github.com/orgs/org/repos", json=repos)

    status = check_source("airbyte/test airbyte/test2 airbytehq/* org/*")
    assert not status.message
    assert status.status == Status.SUCCEEDED
    # Two requests for repos and two for organization
    assert len(responses.calls) == 4


@responses.activate
def test_check_connection_org_only():
    repos = [{"name": f"name {i}", "full_name": f"full name {i}", "updated_at": "2020-01-01T00:00:00Z"} for i in range(1000)]
    responses.add("GET", "https://api.github.com/orgs/airbytehq/repos", json=repos)

    status = check_source("airbytehq/*")
    assert not status.message
    assert status.status == Status.SUCCEEDED
    # One request to check organization
    assert len(responses.calls) == 1


@responses.activate
def test_get_branches_data():

    repository_args = {"repositories": ["airbytehq/integration-test"], "page_size_for_large_streams": 10}

    source = SourceGithub()

    responses.add(
        "GET",
        "https://api.github.com/repos/airbytehq/integration-test",
        json={"full_name": "airbytehq/integration-test", "default_branch": "master"},
    )

    responses.add(
        "GET",
        "https://api.github.com/repos/airbytehq/integration-test/branches",
        json=[
            {"repository": "airbytehq/integration-test", "name": "feature/branch_0"},
            {"repository": "airbytehq/integration-test", "name": "feature/branch_1"},
            {"repository": "airbytehq/integration-test", "name": "feature/branch_2"},
            {"repository": "airbytehq/integration-test", "name": "master"},
        ],
    )

    default_branches, branches_to_pull = source._get_branches_data("", repository_args)
    assert default_branches == {"airbytehq/integration-test": "master"}
    assert branches_to_pull == {"airbytehq/integration-test": ["master"]}

    default_branches, branches_to_pull = source._get_branches_data(
        "airbytehq/integration-test/feature/branch_0 airbytehq/integration-test/feature/branch_1 airbytehq/integration-test/feature/branch_3",
        repository_args,
    )

    assert default_branches == {"airbytehq/integration-test": "master"}
    assert len(branches_to_pull["airbytehq/integration-test"]) == 2
    assert "feature/branch_0" in branches_to_pull["airbytehq/integration-test"]
    assert "feature/branch_1" in branches_to_pull["airbytehq/integration-test"]


@responses.activate
def test_get_org_repositories():

    source = SourceGithub()

    with pytest.raises(Exception):
        config = {"repository": ""}
        source._get_org_repositories(config, authenticator=None)

    responses.add(
        "GET",
        "https://api.github.com/repos/airbytehq/integration-test",
        json={"full_name": "airbytehq/integration-test", "organization": {"login": "airbytehq"}},
    )

    responses.add(
        "GET",
        "https://api.github.com/orgs/docker/repos",
        json=[
            {"full_name": "docker/docker-py", "updated_at": "2020-01-01T00:00:00Z"},
            {"full_name": "docker/compose", "updated_at": "2020-01-01T00:00:00Z"},
        ],
    )

    config = {"repository": "airbytehq/integration-test docker/*"}
    organisations, repositories = source._get_org_repositories(config, authenticator=None)

    assert set(repositories) == {"airbytehq/integration-test", "docker/docker-py", "docker/compose"}
    assert set(organisations) == {"airbytehq", "docker"}
