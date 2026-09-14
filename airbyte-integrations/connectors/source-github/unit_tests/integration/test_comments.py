# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from source_github import SourceGithub

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template

from .config import ConfigBuilder


_CONFIG = ConfigBuilder().with_repositories(["airbytehq/mock-test-0"]).build()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="comments", sync_mode=sync_mode).build()


class CommentsTest(TestCase):
    def setUp(self) -> None:
        """Base setup for all tests. Add responses for:
        1. rate limit checker
        2. repositories
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
                json.dumps(
                    {
                        "resources": {
                            "core": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 5070908800},
                            "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 5070908800},
                        }
                    }
                ),
                200,
            ),
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps({"full_name": "airbytehq/mock-test-0", "default_branch": "master"}), 200),
        )

    def tearDown(self):
        """Stops and resets HttpMocker instance."""
        self.r_mock.__exit__(None, None, None)

    def test_read_transforms_reaction_fields(self):
        """Ensure that +1 and -1 reaction fields are transformed to plus_one and minus_one"""
        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/issues/comments",
                query_params={"per_page": 10, "since": "2020-05-01T00:00:00Z"},
            ),
            HttpResponse(json.dumps(find_template("comments", __file__)), 200),
        )

        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 1

        record_data = actual_messages.records[0].record.data
        reactions = record_data.get("reactions")

        assert reactions is not None, "reactions field should exist"
        assert "plus_one" in reactions, "plus_one field should exist after transformation"
        assert "minus_one" in reactions, "minus_one field should exist after transformation"
        assert "+1" not in reactions, "+1 field should not exist after transformation"
        assert "-1" not in reactions, "-1 field should not exist after transformation"

        assert reactions["plus_one"] == 2, "plus_one value should match original +1 value"
        assert reactions["minus_one"] == 1, "minus_one value should match original -1 value"
        assert reactions["total_count"] == 5, "total_count should remain unchanged"
