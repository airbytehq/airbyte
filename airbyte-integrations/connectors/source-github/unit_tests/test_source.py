#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_github.source import SourceGithub

from .utils import command_check


def check_source(repo_line: str) -> AirbyteConnectionStatus:
    source = SourceGithub()
    config = {"access_token": "test_token", "repository": repo_line}
    logger_mock = MagicMock()
    return source.check(logger_mock, config)


@responses.activate
def test_check_connection_repos_only():
    responses.add("GET", "https://api.github.com/repos/airbytehq/airbyte", json={"full_name": "airbytehq/airbyte"})

    status = check_source("airbytehq/airbyte airbytehq/airbyte airbytehq/airbyte")
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


def test_organization_or_repo_available():
    SourceGithub._get_org_repositories = MagicMock(return_value=(False, False))
    source = SourceGithub()
    with pytest.raises(Exception) as exc_info:
        config = {"access_token": "test_token", "repository": ""}
        source.streams(config=config)
    assert exc_info.value.args[0] == "No streams available. Please check permissions"


def tests_get_and_prepare_repositories_config():
    config = {"repository": "airbytehq/airbyte airbytehq/airbyte.test  airbytehq/integration-test"}
    assert SourceGithub._get_and_prepare_repositories_config(config) == {"airbytehq/airbyte", "airbytehq/airbyte.test", "airbytehq/integration-test"}


def test_check_config_repository():
    source = SourceGithub()
    source.check = MagicMock(return_value=True)
    config = {"credentials": {"access_token": "access_token"}, "start_date": "1900-01-01T00:00:00Z"}

    repos_ok = [
        "airbytehq/airbyte",
        "airbytehq/airbyte-test",
        "airbytehq/airbyte_test",
        "erohmensing/thismonth.rocks",
        "airbytehq/*",
        "airbytehq/.",
        "airbyte_hq/airbyte",
        "airbytehq/123",
        "airbytehq/airbytexgit",
    ]

    repos_fail = [
        "airbytehq",
        "airbytehq/",
        "airbytehq/*/",
        "airbytehq/airbyte.git",
        "airbytehq/airbyte/",
        "airbytehq/air*yte",
        "airbyte*/airbyte",
        "airbytehq/airbyte-test/master-branch",
        "https://github.com/airbytehq/airbyte",
    ]

    config["repository"] = ""
    with pytest.raises(AirbyteTracedException):
        assert command_check(source, config)
    config["repository"] = " "
    with pytest.raises(AirbyteTracedException):
        assert command_check(source, config)

    for repos in repos_ok:
        config["repository"] = repos
        assert command_check(source, config)

    for repos in repos_fail:
        config["repository"] = repos
        with pytest.raises(AirbyteTracedException):
            assert command_check(source, config)

    config["repository"] = " ".join(repos_ok)
    assert command_check(source, config)
    config["repository"] = "    ".join(repos_ok)
    assert command_check(source, config)
    config["repository"] = ",".join(repos_ok)
    with pytest.raises(AirbyteTracedException):
        assert command_check(source, config)

    for repos in repos_fail:
        config["repository"] = " ".join(repos_ok[:len(repos_ok)//2] + [repos] + repos_ok[len(repos_ok)//2:])
        with pytest.raises(AirbyteTracedException):
            assert command_check(source, config)
