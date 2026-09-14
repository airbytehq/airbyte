# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase, mock

from source_github import SourceGithub

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode, TraceType
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder

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
            HttpResponse(json.dumps({"full_name": "airbytehq/integration-test", "default_branch": "master"}), 200),
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/branches",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps([{"repository": "airbytehq/integration-test", "name": "master"}]), 200),
        )

    def teardown(self):
        """Stops and resets HttpMocker instance."""
        self.r_mock.__exit__()

    def test_read_full_refresh_no_pagination(self):
        """Ensure http integration and record extraction"""
        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("events", __file__)), 200),
        )

        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 2

    def test_read_transformation(self):
        """Ensure transformation applied to all records"""

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("events", __file__)), 200),
        )

        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 2
        assert all(("repository", "airbytehq/integration-test") in x.record.data.items() for x in actual_messages.records)

    def test_full_refresh_with_pagination(self):
        """Ensure pagination"""
        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
                query_params={"per_page": 100},
            ),
            HttpResponse(
                body=json.dumps(find_template("events", __file__)),
                status_code=200,
                headers={"Link": '<https://api.github.com/repos/{}/events?page=2>; rel="next"'.format(_CONFIG.get("repositories")[0])},
            ),
        )
        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
                query_params={"per_page": 100, "page": 2},
            ),
            HttpResponse(
                body=json.dumps(find_template("events", __file__)),
                status_code=200,
            ),
        )
        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 4

    def test_given_state_more_recent_than_some_records_when_read_incrementally_then_filter_records(self):
        """Ensure incremental sync.
        `events` is semi-incremental, so all requests will be performed and only new records will be extracted.
        The state is the legacy `{repository: {created_at: ...}}` shape, migrated by the manifest's
        `LegacyToPerPartitionStateMigration`."""

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("events", __file__)), 200),
        )

        state = StateBuilder().with_stream_state("events", {"airbytehq/integration-test": {"created_at": "2022-06-09T10:00:00Z"}}).build()
        # Declarative streams read their state at construction, not from `read()`'s argument.
        source = SourceGithub(config=_CONFIG, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
        assert len(actual_messages.records) == 1

    def test_when_read_incrementally_then_emit_state_message(self):
        """Ensure incremental sync emits correct stream state message. The manifest stream tracks
        the cursor per repository partition, so the shape is the CDK's per-partition state rather
        than the legacy `{repository: {created_at: ...}}` it was fed."""

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("events", __file__)), 200),
        )

        state = StateBuilder().with_stream_state("events", {"airbytehq/integration-test": {"created_at": "2020-06-09T10:00:00Z"}}).build()
        source = SourceGithub(config=_CONFIG, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
        assert len(actual_messages.records) == 2
        assert actual_messages.state_messages[-1].state.stream.stream_state.__dict__["states"] == [
            {"partition": {"repository": "airbytehq/integration-test"}, "cursor": {"created_at": "2022-06-09T12:47:28Z"}}
        ]

    @mock.patch("time.sleep")
    def test_read_skips_the_repository_on_a_permission_error_and_completes(self, time_mock):
        """Ensure a 403 permission error (no rate-limit headers) is not retried and skips the
        repository. The Python stream failed the whole stream here (INCOMPLETE); as a manifest
        stream `events` shares `skip_inaccessible_error_handler` with the other repo-scoped streams
        (Step 3), which mirrors what `GithubStreamABC.read_records` did for them: warn and move on
        to the next repository, so one unreadable repository does not fail the sync."""
        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/events",
                query_params={"per_page": 100},
            ),
            HttpResponse('{"message":"some_error_message"}', 403),
        )
        source = SourceGithub(config=_CONFIG, catalog=_create_catalog())
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert actual_messages.records == []
        assert any("GitHub denied access" in x.log.message and "(HTTP 403)" in x.log.message for x in actual_messages.logs)
        events_stream_status_message = [x for x in actual_messages.trace_messages if x.trace.type == TraceType.STREAM_STATUS][-1]
        assert events_stream_status_message.trace.stream_status.stream_descriptor.name == "events"
        assert events_stream_status_message.trace.stream_status.status == AirbyteStreamStatus.COMPLETE
