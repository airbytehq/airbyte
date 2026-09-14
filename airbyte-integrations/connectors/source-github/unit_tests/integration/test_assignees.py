# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from source_github import SourceGithub

from airbyte_cdk.models import AirbyteStateBlob, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder


_CONFIG = ConfigBuilder().with_repositories(["airbytehq/mock-test-0", "airbytehq/mock-test-1", "airbytehq/mock-test-2"]).build()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="assignees", sync_mode=sync_mode).build()


class AssigneesTest(TestCase):
    """`assignees` is served by the manifest, partitioned by `repository_partition_router`.

    It is a plain full-refresh declarative stream, so it no longer checkpoints per repository
    the way the Python `SubstreamResumableFullRefreshCursor` did: a single terminal state
    message is emitted and a resumed sync re-reads every repository.
    """

    def setUp(self) -> None:
        """Base setup for all tests. Add responses for:
        1. rate limit checker
        2. the explicit repositories, resolved by the manifest's `repository_stats` stream
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

        for repository in _CONFIG.get("repositories"):
            self.r_mock.get(
                HttpRequest(
                    url=f"https://api.github.com/repos/{repository}",
                    query_params={"per_page": 100},
                ),
                HttpResponse(json.dumps({"id": 1, "full_name": repository, "default_branch": "master"}), 200),
            )

    def teardown(self):
        """Stops and resets HttpMocker instance."""
        self.r_mock.__exit__()

    def _mock_assignees(self):
        for repository in _CONFIG.get("repositories"):
            self.r_mock.get(
                HttpRequest(
                    url=f"https://api.github.com/repos/{repository}/assignees",
                    query_params={"per_page": 100},
                ),
                HttpResponse(json.dumps(find_template("assignees", __file__)), 200),
            )

    def test_read_full_refresh_reads_every_repository_partition(self):
        """Every configured repository is read and stamped with its `repository`."""
        self._mock_assignees()

        source = SourceGithub(config=_CONFIG, catalog=_create_catalog())
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 6
        assert sorted({record.record.data["repository"] for record in actual_messages.records}) == _CONFIG.get("repositories")
        # `repository` is not part of the GitHub payload; it can only come from the manifest's
        # AddFields transformation, which replaces the legacy `GithubStream.transform`.
        assert all("login" in record.record.data for record in actual_messages.records)

        # A full-refresh declarative stream checkpoints once, at the end, with no cursor value.
        assert len(actual_messages.state_messages) == 1
        assert actual_messages.state_messages[0].state.stream.stream_state == AirbyteStateBlob({"__ab_no_cursor_state_message": True})

    def test_read_ignores_legacy_resumable_full_refresh_state(self):
        """State written by the Python implementation carried a per-repository
        `__ab_full_refresh_sync_complete` marker. The manifest stream has no such cursor, so
        that state is ignored rather than skipping the repositories it names."""
        self._mock_assignees()

        incoming_state = (
            StateBuilder()
            .with_stream_state(
                "assignees",
                {
                    "states": [
                        {"partition": {"repository": "airbytehq/mock-test-0"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
                        {"partition": {"repository": "airbytehq/mock-test-1"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
                    ]
                },
            )
            .build()
        )

        source = SourceGithub(config=_CONFIG, catalog=_create_catalog(), state=incoming_state)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog(), state=incoming_state)

        assert len(actual_messages.records) == 6
        assert sorted({record.record.data["repository"] for record in actual_messages.records}) == _CONFIG.get("repositories")
