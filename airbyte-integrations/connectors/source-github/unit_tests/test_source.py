#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from unittest.mock import MagicMock
from urllib.parse import urljoin

import pytest
import responses
from source_github import constants
from source_github.source import SourceGithub

from airbyte_cdk.models import AirbyteConnectionStatus, Status, SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .utils import ProbeStream, command_check


def check_source(repo_line: str) -> AirbyteConnectionStatus:
    config = {"access_token": "test_token", "repository": repo_line}
    source = SourceGithub(config=config)
    logger_mock = MagicMock()
    return source.check(logger_mock, config)


def test_source_extends_yaml_declarative_source():
    source = SourceGithub()
    assert isinstance(source, YamlDeclarativeSource)


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


@pytest.mark.parametrize("api_url", ("https://github.example.com/api/v3", "https://github.example.com/api/v3/"))
def test_api_url_slash_normalization_keeps_python_and_manifest_urls_consistent(api_url):
    """The manifest concatenates after `.rstrip('/')`, but Python streams `urljoin` their
    `url_base` with a relative path — which silently drops the last path segment of a GHES
    base URL lacking a trailing slash (`.../api/v3` + `repos/...` -> `.../api/repos/...`).
    `ConfigNormalization` must normalize the slash so both halves resolve the same base."""
    config = {"access_token": "test_token", "repository": "org/repo", "api_url": api_url}
    source = SourceGithub(config=dict(config))
    config = source._config
    assert config["api_url"] == "https://github.example.com/api/v3/"

    stream = ProbeStream(repositories=["org/repo"], page_size_for_large_streams=10, api_url=config["api_url"])
    joined = urljoin(stream.url_base, stream.path(stream_slice={"repository": "org/repo"}))
    assert joined == "https://github.example.com/api/v3/repos/org/repo/probe_stream"

    manifest_url_base = SourceGithub(config=config).resolved_manifest["definitions"]["requester_base"]["url_base"]
    interpolated = InterpolatedString.create(manifest_url_base, parameters={}).eval(config)
    assert interpolated == "https://github.example.com/api/v3"


@pytest.mark.parametrize(
    "api_url_value",
    (
        pytest.param({}, id="key_absent"),
        pytest.param({"api_url": None}, id="present_but_null"),
        pytest.param({"api_url": ""}, id="empty_string"),
        pytest.param({"api_url": "https://api.github.com"}, id="no_trailing_slash"),
        pytest.param({"api_url": "https://api.github.com/"}, id="already_normalized"),
    ),
)
def test_api_url_default_covers_absent_null_and_empty(api_url_value):
    """A null or empty `api_url` must land on the default rather than reaching `urlparse` as a
    non-string. Null arrives via the API and Terraform, and the spec description tells users to
    "leave it empty to use GitHub", so both are configurations the connector invites."""
    config = SourceGithub(config={"access_token": "test_token", "repository": "org/repo", **api_url_value})._config

    assert config["api_url"] == "https://api.github.com/"


def test_check_connection_repos_only(rate_limit_mock_response, requests_mock):
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/airbyte",
        json={"full_name": "airbytehq/airbyte", "organization": {"login": "airbytehq"}},
    )
    status = check_source("airbytehq/airbyte airbytehq/airbyte airbytehq/airbyte")
    assert not status.message
    assert status.status == Status.SUCCEEDED
    # One quota-status call plus one validation call for the deduplicated explicit repo
    assert requests_mock.call_count == 2


def test_check_connection_repos_and_org_repos(rate_limit_mock_response, requests_mock):
    # A real GitHub listing page holds at most `per_page` (100) records. The paginator follows
    # GitHub's `rel="next"` link and stops when the link is absent, which is why these mocked
    # responses — no Link header — are a single page regardless of how many records they hold.
    repos = [{"name": f"name {i}", "full_name": f"full name {i}", "updated_at": "2020-01-01T00:00:00Z"} for i in range(99)]
    requests_mock.get("https://api.github.com/orgs/airbytehq/repos", json=repos)
    requests_mock.get("https://api.github.com/orgs/org/repos", json=repos)

    requests_mock.get("https://api.github.com/repos/airbyte/test", json={"full_name": "airbyte/test"})
    requests_mock.get("https://api.github.com/repos/airbyte/test2", json={"full_name": "airbyte/test2"})

    status = check_source("airbyte/test airbyte/test2 airbytehq/* org/*")
    assert not status.message
    assert status.status == Status.SUCCEEDED
    # One quota-status call, two org wildcard expansions, and two explicit repo validations
    assert requests_mock.call_count == 5


def test_check_connection_org_only(rate_limit_mock_response, requests_mock):
    repos = [{"name": f"name {i}", "full_name": f"airbytehq/full name {i}", "updated_at": "2020-01-01T00:00:00Z"} for i in range(99)]
    requests_mock.get("https://api.github.com/orgs/airbytehq/repos", json=repos)

    status = check_source("airbytehq/*")
    assert not status.message
    assert status.status == Status.SUCCEEDED
    # One quota-status call and one request to resolve organization repos
    assert requests_mock.call_count == 2


@responses.activate
def test_resolve_repositories_and_organizations(requests_mock, rate_limit_mock_response):
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/integration-test",
        json={"full_name": "airbytehq/integration-test", "organization": {"login": "airbytehq"}},
    )
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            {"full_name": "docker/docker-py", "owner": {"login": "docker"}},
            {"full_name": "docker/compose", "owner": {"login": "docker"}},
        ],
    )

    config = {"credentials": {"access_token": "test_token"}, "repositories": ["airbytehq/integration-test", "docker/*"]}
    source = SourceGithub(config=config)
    config = source._config
    organisations, repositories = source._resolve_repositories_and_organizations(config)

    assert set(repositories) == {"airbytehq/integration-test", "docker/docker-py", "docker/compose"}
    assert set(organisations) == {"airbytehq", "docker"}


def test_check_config_repository():
    config = {"credentials": {"access_token": "access_token"}, "start_date": "1900-01-01T00:00:00Z"}

    def check_with_fresh_source(check_config):
        # One SourceGithub per check, mirroring the entrypoint, which builds the source and
        # calls spec() once per process. The manifest `spec:` block's Spec component is only
        # safe for a single generate_spec() call: it converts `advanced_auth.auth_flow_type`
        # from enum to str in place (CDK spec.py:57), so a second call on the same instance
        # raises AttributeError on the now-plain string.
        source = SourceGithub()
        source.check = MagicMock(return_value=True)
        return command_check(source, check_config)

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
        assert check_with_fresh_source(config)
    config["repositories"] = []
    with pytest.raises(AirbyteTracedException):
        assert check_with_fresh_source(config)

    for repos in repos_ok:
        config["repositories"] = [repos]
        assert check_with_fresh_source(config)

    for repos in repos_fail:
        config["repositories"] = [repos]
        with pytest.raises(AirbyteTracedException):
            assert check_with_fresh_source(config)


@pytest.mark.parametrize(
    "error_message, expected_user_friendly_message",
    [
        # No 404 cases: the shared manifest error handler maps 404 to IGNORE, so those two
        # branches were unreachable and have been removed from the helper.
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


_CONFIG = {"access_token": "test_token", "repository": "airbyte/test"}


def test_read_and_discover_reject_invalid_api_url():
    config = {"access_token": "t", "repositories": ["org/repo"], "api_url": "github.my.company.org"}
    source = SourceGithub(config=config)

    with pytest.raises(AirbyteTracedException) as e:
        source.discover(logging.getLogger("airbyte"), config)
    assert e.value.message == "Please enter a full url for `API URL` field starting with `http`"

    with pytest.raises(AirbyteTracedException) as e:
        list(
            source.read(
                logging.getLogger("airbyte"),
                config,
                CatalogBuilder().with_stream("workflow_runs", SyncMode.full_refresh).build(),
            )
        )
    assert e.value.message == "Please enter a full url for `API URL` field starting with `http`"


def test_discover_does_not_issue_http(requests_mock):
    catalog = SourceGithub(config=_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG)
    assert len(catalog.streams) > 0
    assert requests_mock.call_count == 0


def test_every_discovered_schema_is_fully_expanded():
    """No `$ref` may survive into a discovered schema.

    The manifest cannot resolve a JSON-Schema `$ref`: a relative one (`user.json`) is left as a
    literal string, and `#/definitions/...` is swallowed by the manifest's own `$ref` resolver.
    Either way the platform receives `"user.json"` where an object belongs and DISCOVER fails.
    The shared schemas are expanded at every use instead, so nothing here may look like a ref.
    """
    source = SourceGithub(config=_CONFIG)
    catalog = source.discover(logging.getLogger("airbyte"), _CONFIG)

    offenders = []
    for stream in catalog.streams:
        stack = [(stream.name, stream.json_schema)]
        while stack:
            path, node = stack.pop()
            if isinstance(node, dict):
                if "$ref" in node:
                    offenders.append(f"{path}.$ref = {node['$ref']!r}")
                stack.extend((f"{path}.{key}", value) for key, value in node.items())
            elif isinstance(node, list):
                stack.extend((f"{path}[{index}]", value) for index, value in enumerate(node))
            elif isinstance(node, str) and node.endswith(".json"):
                offenders.append(f"{path} = {node!r}")
    assert offenders == []
