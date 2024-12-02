# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder
from source_github import SourceGithub

from .config import ConfigBuilder

_CONFIG = ConfigBuilder().with_repositories(["airbytehq/mock-test-0", "airbytehq/mock-test-1", "airbytehq/mock-test-2"]).build()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="assignees", sync_mode=sync_mode).build()


class AssigneesTest(TestCase):
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
            HttpResponse(json.dumps({"full_name": "airbytehq/mock-test-0", "default_branch": "master"}), 200),
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[1]}",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps({"full_name": "airbytehq/mock-test-1", "default_branch": "master"}), 200),
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[2]}",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps({"full_name": "airbytehq/mock-test-2", "default_branch": "master"}), 200),
        )

    def teardown(self):
        """Stops and resets HttpMocker instance."""
        self.r_mock.__exit__()

    def test_read_full_refresh_emits_per_partition_state(self):
        """Ensure http integration and per-partition state is emitted correctly"""
        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/assignees",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("assignees", __file__)), 200),
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[1]}/assignees",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("assignees", __file__)), 200),
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[2]}/assignees",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("assignees", __file__)), 200),
        )

        per_partition_state_0 = {"partition": {"repository": "airbytehq/mock-test-0"}, "cursor": {"__ab_full_refresh_sync_complete": True}}
        per_partition_state_1 = {"partition": {"repository": "airbytehq/mock-test-1"}, "cursor": {"__ab_full_refresh_sync_complete": True}}
        per_partition_state_2 = {"partition": {"repository": "airbytehq/mock-test-2"}, "cursor": {"__ab_full_refresh_sync_complete": True}}

        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 6

        # Validates that each time we sync a parent partition, the size of the per-partition state is increasing for the final
        # state of each parent record
        assert len(actual_messages.state_messages) == 3
        actual_state_after_first_partition = actual_messages.state_messages[0].state.stream.stream_state.model_dump()
        assert len(actual_state_after_first_partition.get("states")) == 1
        actual_state_after_second_partition = actual_messages.state_messages[1].state.stream.stream_state.model_dump()
        assert len(actual_state_after_second_partition.get("states")) == 2
        actual_state_after_third_partition = actual_messages.state_messages[2].state.stream.stream_state.model_dump()
        assert len(actual_state_after_third_partition.get("states")) == 3

        # Validate that the final set of per-partition states includes the terminal value for each successful parent
        final_list_of_per_partition_state = actual_state_after_third_partition.get("states")
        assert per_partition_state_0 in final_list_of_per_partition_state
        assert per_partition_state_1 in final_list_of_per_partition_state
        assert per_partition_state_2 in final_list_of_per_partition_state

    def test_read_full_refresh_emits_per_partition_state(self):
        """Ensure that incoming RFR state skips parent records from state that have already been synced on a prior attempt"""
        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[0]}/assignees",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("assignees", __file__)), 200),
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[1]}/assignees",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("assignees", __file__)), 200),
        )

        self.r_mock.get(
            HttpRequest(
                url=f"https://api.github.com/repos/{_CONFIG.get('repositories')[2]}/assignees",
                query_params={"per_page": 100},
            ),
            HttpResponse(json.dumps(find_template("assignees", __file__)), 200),
        )

        per_partition_state_0 = {"partition": {"repository": "airbytehq/mock-test-0"}, "cursor": {"__ab_full_refresh_sync_complete": True}}
        per_partition_state_1 = {"partition": {"repository": "airbytehq/mock-test-1"}, "cursor": {"__ab_full_refresh_sync_complete": True}}
        per_partition_state_2 = {"partition": {"repository": "airbytehq/mock-test-2"}, "cursor": {"__ab_full_refresh_sync_complete": True}}

        incoming_state = StateBuilder().with_stream_state("assignees", {
            "states": [
                {"partition": {"repository": "airbytehq/mock-test-0"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
                {"partition": {"repository": "airbytehq/mock-test-1"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            ]
        }).build()

        source = SourceGithub()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog(), state=incoming_state)

        assert len(actual_messages.records) == 2

        # There should only be on state message since the first two parents were already successfully synced
        assert len(actual_messages.state_messages) == 1
        final_list_of_per_partition_state = actual_messages.state_messages[0].state.stream.stream_state.model_dump().get("states")
        assert per_partition_state_0 in final_list_of_per_partition_state
        assert per_partition_state_1 in final_list_of_per_partition_state
        assert per_partition_state_2 in final_list_of_per_partition_state
