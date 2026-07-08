#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from unittest.mock import MagicMock, patch

import pytest
import responses
from source_github import constants
from source_github.components import RepositoryListResolver
from source_github.source import SourceGithub

from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteStream, Status, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .utils import command_check


def check_source(repo_line: str) -> AirbyteConnectionStatus:
    config = {"access_token": "test_token", "repository": repo_line}
    source = SourceGithub(config=config)
    logger_mock = MagicMock()
    return source.check(logger_mock, config)


def test_source_extends_yaml_declarative_source():
    source = SourceGithub()
    assert isinstance(source, YamlDeclarativeSource)


def test_source_will_continue_sync_on_stream_failure():
    source = SourceGithub()
    assert source.continue_sync_on_stream_failure


@responses.activate
@pytest.mark.parametrize(
    "config, expected",
    (
        (
            {
                "start_date": "2021-08-27T00:00:46Z",
                "access_token": "test_token",
                "repository": "airbyte/test",
            },
            True,
        ),
        ({"access_token": "test_token", "repository": "airbyte/test"}, True),
    ),
)
def test_check_start_date(config, expected, rate_limit_mock_response, requests_mock):
    requests_mock.get("https://api.github.com/repos/airbyte/test", json={"full_name": "test_full_name"})
    source = SourceGithub()
    status, _ = source.check_connection(logger=logging.getLogger("airbyte"), config=config)
    assert status == expected


@pytest.mark.parametrize(
    "api_url, deployment_env, expected_message",
    (
        ("github.my.company.org", "CLOUD", "Please enter a full url for `API URL` field starting with `http`"),
        (
            "http://github.my.company.org",
            "CLOUD",
            "HTTP connection is insecure and is not allowed in this environment. Please use `https` instead.",
        ),
        ("http:/github.my.company.org", "NOT_CLOUD", "Please provide a correct API URL."),
        ("https:/github.my.company.org", "CLOUD", "Please provide a correct API URL."),
    ),
)
def test_connection_fail_due_to_config_error(api_url, deployment_env, expected_message):
    os.environ["DEPLOYMENT_MODE"] = deployment_env
    source = SourceGithub()
    config = {"access_token": "test_token", "repository": "airbyte/test", "api_url": api_url}

    with pytest.raises(AirbyteTracedException) as e:
        source.check_connection(logging.getLogger(), config)
    assert e.value.message == expected_message


def test_check_connection_repos_only(rate_limit_mock_response, requests_mock):
    status = check_source("airbytehq/airbyte airbytehq/airbyte airbytehq/airbyte")
    assert not status.message
    assert status.status == Status.SUCCEEDED
    # Explicit repos are trusted without HTTP calls
    assert requests_mock.call_count == 0


def test_check_connection_repos_and_org_repos(rate_limit_mock_response, requests_mock):
    repos = [{"name": f"name {i}", "full_name": f"full name {i}", "updated_at": "2020-01-01T00:00:00Z"} for i in range(1000)]
    requests_mock.get("https://api.github.com/orgs/airbytehq/repos", json=repos)
    requests_mock.get("https://api.github.com/orgs/org/repos", json=repos)

    status = check_source("airbyte/test airbyte/test2 airbytehq/* org/*")
    assert not status.message
    assert status.status == Status.SUCCEEDED
    # Only two requests for org wildcards; explicit repos are trusted without HTTP calls
    assert requests_mock.call_count == 2


def test_check_connection_org_only(rate_limit_mock_response, requests_mock):
    repos = [{"name": f"name {i}", "full_name": f"airbytehq/full name {i}", "updated_at": "2020-01-01T00:00:00Z"} for i in range(1000)]
    requests_mock.get("https://api.github.com/orgs/airbytehq/repos", json=repos)

    status = check_source("airbytehq/*")
    assert not status.message
    assert status.status == Status.SUCCEEDED
    # One request to resolve organization repos
    assert requests_mock.call_count == 1


@responses.activate
def test_get_resolved_repositories(requests_mock):
    # Only wildcard orgs need HTTP calls; explicit repos are trusted directly.
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            {"full_name": "docker/docker-py", "owner": {"login": "docker"}},
            {"full_name": "docker/compose", "owner": {"login": "docker"}},
        ],
    )

    config = {"credentials": {"access_token": "test_token"}, "repositories": ["airbytehq/integration-test", "docker/*"]}
    source = SourceGithub()
    config = source._ensure_default_values(config)
    config = source._validate_repositories(config)
    resolver = RepositoryListResolver(parameters={})
    resolver.transform(config)

    organisations = config["_resolved_organizations"]
    repositories = config["_resolved_repositories"]

    assert set(repositories) == {"airbytehq/integration-test", "docker/docker-py", "docker/compose"}
    assert set(organisations) == {"airbytehq", "docker"}


@responses.activate
def test_organization_or_repo_available(monkeypatch, rate_limit_mock_response):
    monkeypatch.setattr(SourceGithub, "_get_resolved_repositories", MagicMock(return_value=([], [], None)))
    monkeypatch.setattr(RepositoryListResolver, "transform", MagicMock())
    source = SourceGithub()
    with pytest.raises(Exception) as exc_info:
        config = {"access_token": "test_token", "repository": ""}
        source.streams(config=config)
    assert exc_info.value.args[0] == "No streams available. Please check permissions"


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
        "airbytehq/a*",
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

    config["repositories"] = []
    with pytest.raises(AirbyteTracedException):
        assert command_check(source, config)
    config["repositories"] = []
    with pytest.raises(AirbyteTracedException):
        assert command_check(source, config)

    for repos in repos_ok:
        config["repositories"] = [repos]
        assert command_check(source, config)

    for repos in repos_fail:
        config["repositories"] = [repos]
        with pytest.raises(AirbyteTracedException):
            assert command_check(source, config)


@responses.activate
def test_streams_no_streams_available_error(monkeypatch, rate_limit_mock_response):
    monkeypatch.setattr(SourceGithub, "_get_resolved_repositories", MagicMock(return_value=([], [], None)))
    monkeypatch.setattr(RepositoryListResolver, "transform", MagicMock())
    with pytest.raises(AirbyteTracedException) as e:
        SourceGithub().streams(config={"access_token": "test_token", "repository": "airbytehq/airbyte-test"})
    assert str(e.value) == (
        "No streams available. Looks like your config for repositories or organizations is not valid."
        " Please, check your permissions, names of repositories and organizations."
        " Needed scopes: repo, read:org, read:repo_hook, read:user, read:discussion, workflow."
    )


def test_streams_page_size(rate_limit_mock_response, requests_mock):
    requests_mock.get("https://api.github.com/repos/airbytehq/airbyte", json={"full_name": "airbytehq/airbyte", "default_branch": "master"})
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/airbyte/branches", json=[{"repository": "airbytehq/airbyte", "name": "master"}]
    )

    config = {
        "credentials": {"access_token": "access_token"},
        "repository": "airbytehq/airbyte",
        "start_date": "1900-07-12T00:00:00Z",
    }

    source = SourceGithub()
    streams = source.streams(config)
    assert constants.DEFAULT_PAGE_SIZE != constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM

    for stream in streams:
        if not hasattr(stream, "page_size"):
            continue
        if stream.large_stream:
            assert stream.page_size == constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM
        else:
            assert stream.page_size == constants.DEFAULT_PAGE_SIZE


@pytest.mark.parametrize(
    "config, expected",
    (
        (
            {
                "start_date": "2021-08-27T00:00:46Z",
                "access_token": "test_token",
                "repository": "airbyte/test",
            },
            38,
        ),
        ({"access_token": "test_token", "repository": "airbyte/test"}, 38),
    ),
)
def test_streams_config_start_date(config, expected, rate_limit_mock_response, requests_mock):
    requests_mock.get("https://api.github.com/repos/airbyte/test", json={"full_name": "airbyte/test", "default_branch": "default_branch"})
    requests_mock.get(
        "https://api.github.com/repos/airbyte/test/branches",
        json=[{"repository": "airbyte/test", "name": "name"}],
    )
    source = SourceGithub()
    streams = source.streams(config=config)
    # Find a Python stream that accepts start_date to verify config propagation
    python_streams_with_start_date = [s for s in streams if hasattr(s, "_start_date")]
    assert len(streams) == expected
    assert len(python_streams_with_start_date) > 0
    sample_stream = python_streams_with_start_date[0]
    if config.get("start_date"):
        assert sample_stream._start_date == "2021-08-27T00:00:46Z"
    else:
        assert not sample_stream._start_date


@pytest.mark.parametrize(
    "error_message, expected_user_friendly_message",
    [
        (
            "404 Client Error: Not Found for url: https://api.github.com/repos/repo_name",
            'Repo name: "repo_name" is unknown, "repository" config option should use existing full repo name <organization>/<repository>',
        ),
        (
            "404 Client Error: Not Found for url: https://api.github.com/orgs/org_name",
            'Organization name: "org_name" is unknown, "repository" config option should be updated. Please validate your repository config.',
        ),
        (
            "401 Client Error: Unauthorized for url",
            "GitHub authentication failed (HTTP 401). Please verify your Personal Access Token or OAuth credentials are valid and not expired.",
        ),
    ],
)
def test_user_friendly_message(error_message, expected_user_friendly_message):
    source = SourceGithub()
    user_friendly_error_message = source.user_friendly_error_message(error_message)
    assert user_friendly_error_message == expected_user_friendly_message


_MANIFEST_WITH_STREAM = {
    "version": "7.12.0",
    "type": "DeclarativeSource",
    "check": {"type": "CheckStream", "stream_names": []},
    "streams": [
        {
            "type": "DeclarativeStream",
            "name": "dummy_manifest_stream",
            "retriever": {
                "type": "SimpleRetriever",
                "requester": {
                    "type": "HttpRequester",
                    "url_base": "https://api.github.com",
                    "path": "/dummy",
                    "http_method": "GET",
                },
                "record_selector": {
                    "type": "RecordSelector",
                    "extractor": {"type": "DpathExtractor", "field_path": []},
                },
            },
            "schema_loader": {
                "type": "InlineSchemaLoader",
                "schema": {"type": "object", "properties": {}},
            },
        }
    ],
}

_CONFIG = {"access_token": "test_token", "repository": "airbyte/test"}


def _mock_python_stream(name: str) -> MagicMock:
    stream = MagicMock()
    stream.name = name
    stream.as_airbyte_stream.return_value = AirbyteStream(name=name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    return stream


def _source_with_manifest_stream() -> SourceGithub:
    with patch.object(YamlDeclarativeSource, "_read_and_parse_yaml_file", return_value=_MANIFEST_WITH_STREAM):
        return SourceGithub(config=_CONFIG)


def test_discover_returns_union_of_python_and_manifest_streams(monkeypatch):
    source = _source_with_manifest_stream()
    monkeypatch.setattr(SourceGithub, "streams", MagicMock(return_value=[_mock_python_stream("teams")]))

    catalog = source.discover(logging.getLogger("airbyte"), _CONFIG)

    stream_names = {stream.name for stream in catalog.streams}
    assert stream_names == {"teams", "dummy_manifest_stream"}


def test_read_routes_manifest_streams_to_concurrent_and_python_streams_to_synchronous(monkeypatch):
    source = _source_with_manifest_stream()
    monkeypatch.setattr(SourceGithub, "streams", MagicMock(return_value=[_mock_python_stream("teams")]))

    catalog = (
        CatalogBuilder()
        .with_stream(name="dummy_manifest_stream", sync_mode=SyncMode.full_refresh)
        .with_stream(name="teams", sync_mode=SyncMode.full_refresh)
        .build()
    )

    with (
        patch.object(ConcurrentSource, "read", return_value=iter([])) as concurrent_read,
        patch.object(AbstractSource, "read", return_value=iter([])) as synchronous_read,
    ):
        list(source.read(logging.getLogger("airbyte"), _CONFIG, catalog))

    selected_concurrent_streams = concurrent_read.call_args.args[0]
    assert [stream.name for stream in selected_concurrent_streams] == ["dummy_manifest_stream"]

    synchronous_catalog = synchronous_read.call_args.args[3]
    assert [s.stream.name for s in synchronous_catalog.streams] == ["teams"]


def test_read_with_empty_manifest_skips_concurrent_read():
    source = SourceGithub(config=_CONFIG)
    catalog = CatalogBuilder().with_stream(name="teams", sync_mode=SyncMode.full_refresh).build()

    with (
        patch.object(ConcurrentSource, "read", return_value=iter([])) as concurrent_read,
        patch.object(AbstractSource, "read", return_value=iter([])) as synchronous_read,
    ):
        list(source.read(logging.getLogger("airbyte"), _CONFIG, catalog))

    concurrent_read.assert_not_called()
    synchronous_read.assert_called_once()
    synchronous_catalog = synchronous_read.call_args.args[3]
    assert [s.stream.name for s in synchronous_catalog.streams] == ["teams"]
