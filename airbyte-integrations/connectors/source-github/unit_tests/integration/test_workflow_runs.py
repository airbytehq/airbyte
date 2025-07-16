# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase, mock

from freezegun import freeze_time
from source_github import SourceGithub

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .config import ConfigBuilder


_CONFIG = ConfigBuilder().with_repositories(["airbytehq/integration-test"]).build()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="workflow_runs", sync_mode=sync_mode).build()


class TestWorkflowRuns(TestCase):
    def setUp(self) -> None:
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
        self.r_mock.__exit__()

    @mock.patch("time.sleep")
    @freeze_time("2025-01-01T00:00:00Z")
    def test_read_403_status_code_when_wait_time_grt_max_seconds_between_messages(self, time_mock):
        self.r_mock.get(
            HttpRequest(
                url="https://api.github.com/repos/airbytehq/integration-test/actions/runs?per_page=100",
                query_params={},
                headers={},
            ),
            HttpResponse(
                body=json.dumps({"error": "error message"}),
                headers={
                    "X-RateLimit-Resource": "core",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "1735725001",
                    "X-RateLimit-Limit": "5000",
                    "X-RateLimit-Used": "5000",
                },
                status_code=403,
            ),
        )
        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert actual_messages.errors[0].trace.error.message == (
            "The stream workflow_runs have faced rate limits, but waiting time is too long. "
            "The stream will sync data in the next sync when rate limits are refreshed."
        )
        assert actual_messages.errors[0].trace.error.failure_type == FailureType.transient_error
