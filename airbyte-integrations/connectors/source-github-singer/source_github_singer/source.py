"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import sys
from typing import Dict, List

import requests
from airbyte_protocol import AirbyteConnectionStatus, Status, SyncMode
from base_python import AirbyteLogger
from base_singer import SingerSource, SyncModeInfo


class SourceGithubSinger(SingerSource):
    @staticmethod
    def _check_with_catalog(logger: AirbyteLogger, streams: List, config: json):
        repositories = config["repository"].split(" ")
        for repository in repositories:
            org = repository.split("/")[0]
            # requests for checking streams permissions
            # first is for checking if user has access to Collaborators API
            # if user is not one of the collaborators, request will return 403 error
            # third is for checking access and permission to Teams API
            # Teams API is only available to authenticated members of the team's organization,
            # in another case it will return 404 error
            # if user doesn't have permission, it will return 401 error
            check_streams = {
                "collaborators": f"https://api.github.com/repos/{repository}/collaborators",
                "teams": f"https://api.github.com/orgs/{org}/teams?sort=created_at&direction=desc",
            }
            for stream in streams:
                if stream in check_streams:
                    response = requests.get(check_streams[stream], auth=(config["access_token"], ""))
                    if response.status_code != requests.codes.ok:
                        logger.log_by_prefix(f"{repository} {response.text}", "ERROR")
                        sys.exit(1)

    def check_config(self, logger, config_path: str, config: json) -> AirbyteConnectionStatus:
        try:
            repositories = config["repository"].split(" ")
            for repository in repositories:
                url = f"https://api.github.com/repos/{repository}/commits"
                response = requests.get(url, auth=(config["access_token"], ""))
                if response.status_code != requests.codes.ok:
                    return AirbyteConnectionStatus(status=Status.FAILED, message=f"{repository} {response.text}")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            logger.error(err)
            error_msg = f"Unable to connect with the provided credentials. Error: {err}"
            return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg)

    def discover_cmd(self, logger, config_path) -> str:
        return f"tap-github --config {config_path} --discover"

    def get_sync_mode_overrides(self) -> Dict[str, SyncModeInfo]:
        incremental_streams = [
            "team_memberships",
            "events",
            "comments",
            "commit_comments",
            "project_cards",
            "issue_milestones",
            "commits",
            "collaborators",
            "stargazers",
            "teams",
            "review_comments",
            "projects",
            "issue_labels",
            "issues",
            "issue_events",
            "project_columns",
            "team_members",
            "pull_request_reviews",
            "pr_commits",
        ]

        full_refresh_streams = ["assignees", "collaborators", "pull_requests", "reviews", "releases"]
        overrides = {}
        for stream_name in incremental_streams:
            overrides[stream_name] = SyncModeInfo(supported_sync_modes=[SyncMode.incremental])
        for stream_name in full_refresh_streams:
            overrides[stream_name] = SyncModeInfo(supported_sync_modes=[SyncMode.full_refresh])
        return overrides

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        properties_option = f"--properties {catalog_path}"
        state_option = f"--state {state_path}" if state_path else ""
        streams = [
            stream["stream"] for stream in self.read_config(catalog_path).get("streams", []) if stream["schema"].get("selected", False)
        ]
        self._check_with_catalog(logger, streams, self.read_config(config_path))
        return f"tap-github {config_option} {properties_option} {state_option}"
