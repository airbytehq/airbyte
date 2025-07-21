# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase, mock

from freezegun import freeze_time
from source_github import SourceGithub, constants

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .config import ConfigBuilder


_TOKENS = (
    "GITHUB_TEST_TOKEN1,GITHUB_TEST_TOKEN2,GITHUB_TEST_TOKEN3,GITHUB_TEST_TOKEN4,GITHUB_TEST_TOKEN5,GITHUB_TEST_TOKEN6,GITHUB_TEST_TOKEN7"
)
_CONFIG = ConfigBuilder().with_repositories(["airbytehq/integration-test"]).build()
_CONFIG_WITH_7_TOKENS = ConfigBuilder().with_personal_access_tokens(_TOKENS).with_repositories(["airbytehq/integration-test"]).build()

_FREEZE_TIME = "2025-01-01T00:00:00Z"
_FREEZE_TIME_TIMESTAMP = 1735689600


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="workflow_runs", sync_mode=sync_mode).build()


class TestWorkflowRuns(TestCase):
    def setUp(self) -> None:
        self.r_mock = HttpMocker()

        self.r_mock.__enter__()
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

    def mock_token_request(self, token: str, remaining: int):
        self.r_mock.get(
            HttpRequest(
                url="https://api.github.com/rate_limit",
                query_params={},
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "Authorization": f"token {token}",
                },
            ),
            HttpResponse(
                json.dumps(
                    {
                        "resources": {
                            "core": {"limit": 5000, "used": 0, "remaining": remaining, "reset": 5070908800},
                            "graphql": {"limit": 5000, "used": 0, "remaining": remaining, "reset": 5070908800},
                        }
                    }
                ),
                200,
            ),
        )

    @mock.patch("time.sleep")
    @freeze_time(_FREEZE_TIME)
    def test_read_response_403_status_code_retry_after_more_than_10_minutes_all_tokens_exhausted(self, time_mock):
        self.r_mock.get(
            HttpRequest(
                url="https://api.github.com/repos/airbytehq/integration-test/actions/runs?per_page=100",
                query_params={},
                headers={"Authorization": "token GITHUB_TEST_TOKEN"},
            ),
            HttpResponse(
                body=json.dumps({"error": "error message"}),
                headers={
                    "X-RateLimit-Resource": "core",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(_FREEZE_TIME_TIMESTAMP + 6001),
                    "X-RateLimit-Limit": "5000",
                    "X-RateLimit-Used": "5000",
                },
                status_code=403,
            ),
        )
        # available 2 requests for check rate limiting and getting repos
        self.mock_token_request("GITHUB_TEST_TOKEN", 2)
        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert actual_messages.errors[0].trace.error.internal_message == (
            "Stream: `workflow_runs`, slice: `{'repository': 'airbytehq/integration-test'}`."
            " Limits for all provided tokens are reached, please try again later"
        )
        assert actual_messages.errors[0].trace.error.failure_type == FailureType.config_error

    @mock.patch("time.sleep")
    @freeze_time(_FREEZE_TIME)
    def test_read_response_403_status_code_retry_after_more_than_10_minutes_all_tokens_exhausted_except_1(self, time_mock):
        # read workflow runs with auth token GITHUB_TEST_TOKEN1 returns 403 status code
        self.r_mock.get(
            HttpRequest(
                url="https://api.github.com/repos/airbytehq/integration-test/actions/runs?per_page=100",
                query_params={},
                headers={"Authorization": "token GITHUB_TEST_TOKEN1"},
            ),
            HttpResponse(
                body=json.dumps({"error": "error message"}),
                headers={
                    "X-RateLimit-Resource": "core",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(_FREEZE_TIME_TIMESTAMP + 6001),
                    "X-RateLimit-Limit": "5000",
                    "X-RateLimit-Used": "5000",
                },
                status_code=403,
            ),
        )
        # read workflow runs with auth token GITHUB_TEST_TOKEN7 returns 200 status code
        self.r_mock.get(
            HttpRequest(
                url="https://api.github.com/repos/airbytehq/integration-test/actions/runs?per_page=100",
                query_params={},
                headers={"Authorization": "token GITHUB_TEST_TOKEN7"},
            ),
            HttpResponse(
                body=json.dumps(
                    {
                        "workflow_runs": [
                            {
                                "id": 4,
                                "created_at": "2022-02-05T00:00:00Z",
                                "updated_at": "2022-02-05T00:00:00Z",
                                "repository": {"full_name": "org/repos"},
                            }
                        ],
                    }
                ),
                status_code=200,
            ),
        )

        tokens = _TOKENS.split(constants.TOKEN_SEPARATOR)
        # tokens from GITHUB_TEST_TOKEN2 to GITHUB_TEST_TOKEN6 are exhausted
        for token in tokens[1:-1]:
            self.mock_token_request(token, 0)
        # token GITHUB_TEST_TOKEN1 have 2 available requests for check rate limits and getting repos
        self.mock_token_request(tokens[0], 2)
        # GITHUB_TEST_TOKEN7 is an available token so workflow runs should use it to make requests
        self.mock_token_request(tokens[-1], 200)

        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG_WITH_7_TOKENS, catalog=_create_catalog())

        assert len(actual_messages.records) == 1, "Workflow runs didn't read 1 record with auth token GITHUB_TEST_TOKEN7"
        assert "Retrying. Sleeping for 1 seconds" in [
            mes.log.message for mes in actual_messages.logs
        ], "Workflow runs didn't call backoff strategy for auth token GITHUB_TEST_TOKEN1"
