# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import json
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http.mocker import HttpMocker
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from source_github import SourceGithub

from .config import ConfigBuilder

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

        self.r_mock = HttpMocker()
        self.r_mock.__enter__()
        self.r_mock.get(
            HttpRequest(
                url="https://api.github.com/rate_limit",
                query_params={},
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "Authorization": "token GITHUB_TEST_TOKEN",
                },
            ),
            HttpResponse(
                json.dumps({
                    "resources": {
                        "core": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 5070908800},
                        "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 5070908800},
                    }
                }),
                200
            )
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}",
                query_params={"per_page": 100},
            ),
            HttpResponse(
                json.dumps({"full_name": "airbytehq/integration-test", "default_branch": "master"}),
                200
            )
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/branches",
                query_params={"per_page": 100},
            ),
            HttpResponse(
                json.dumps([{"repository": "airbytehq/integration-test", "name": "master"}]),
                200
            )
        )

    def teardown(self):
        """Stops and resets RequestsMock instance.

        If ``assert_all_requests_are_fired`` is set to ``True``, will raise an error
        if some requests were not processed.
        """
        self.r_mock.__exit__()

    def test_full_refresh_no_pagination(self):
        """Ensure http integration, record extraction and transformation"""

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
                query_params={"per_page": 100},
            ),
            HttpResponse(
                json.dumps(find_template("events", __file__)),
                200
            )
        )

        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 2
        assert all(("repository", "airbytehq/integration-test") in x.record.data.items() for x in actual_messages.records)
