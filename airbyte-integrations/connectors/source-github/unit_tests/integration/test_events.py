# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import responses
from airbyte_protocol.models import Level

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder
from responses import matchers
from source_github import SourceGithub

from .config import ConfigBuilder

_TOKEN = "GITHUB_TEST_TOKEN"

_CONFIG = ConfigBuilder().with_repositories(["airbytehq/integration-test"]).build()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="events", sync_mode=sync_mode).build()


class EventsTest(TestCase):
    def setUp(self) -> None:
        """Base setup for all tests. Add responses for:
        1. rate limit checker
        2. repositories
        3. branches
        """
        responses.get(
            "https://api.github.com/rate_limit",
            match=[
                matchers.header_matcher(
                    {
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                        "Authorization": "token GITHUB_TEST_TOKEN",
                    }
                )
            ],
            json={
                "resources": {
                    "core": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 5070908800},
                    "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 5070908800},
                }
            },
        )
        responses.get(
            f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}",
            match=[matchers.query_param_matcher({"per_page": 100})],
            json={"full_name": "airbytehq/integration-test", "default_branch": "master"},
        )
        responses.get(
            f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/branches",
            match=[matchers.query_param_matcher({"per_page": 100})],
            json=[{"repository": "airbytehq/integration-test", "name": "master"}],
        )

    @responses.activate
    def test_full_refresh_no_pagination(self):
        """Ensure http integration and record extraction"""
        responses.get(
            f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
            match=[matchers.query_param_matcher({"per_page": 100})],
            json=find_template("events", __file__),
        )

        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 2

    @responses.activate
    def test_full_refresh_with_pagination(self):
        """Ensure pagination"""
        responses.get(
            f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
            headers={"Link": '<https://api.github.com/repos/{}/events?page=2>; rel="next"'.format(_CONFIG.get("repositories")[0])},
            match=[matchers.query_param_matcher({"per_page": 100})],
            json=find_template("events", __file__),
        )
        responses.get(
            f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
            match=[matchers.query_param_matcher({"per_page": 100, "page": 2})],
            json=find_template("events", __file__),
        )
        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 4

    @responses.activate
    def test_incremental_read(self):
        """Ensure incremental sync.
        Stream `Events` is semi-incremental, so all request  will be performed and only new records will be extracted"""

        responses.get(
            f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
            match=[matchers.query_param_matcher({"per_page": 100})],
            json=find_template("events", __file__),
        )

        source = SourceGithub()
        actual_messages = read(
            source,
            config=_CONFIG,
            catalog=_create_catalog(sync_mode=SyncMode.incremental),
            state=StateBuilder()
            .with_stream_state("events", {"airbytehq/integration-test": {"created_at": "2022-06-09T10:00:00Z"}})
            .build(),
        )
        assert len(actual_messages.records) == 1

    @responses.activate
    def test_read_with_error(self):
        """Ensure read() method does not raise an Exception and log message with error is in output"""

        responses.get(
            f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
            match=[matchers.query_param_matcher({"per_page": 100})],
            body='{"message":"some_error_message"}',
            status=403,
        )
        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 0
        assert Level.ERROR in [x.log.level for x in actual_messages.logs]
