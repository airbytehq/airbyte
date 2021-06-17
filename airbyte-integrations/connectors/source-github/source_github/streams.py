#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import tempfile
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
import vcr
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

cache_file = tempfile.NamedTemporaryFile()


class GithubStream(HttpStream, ABC):
    url_base = "https://api.github.com/"

    primary_key = "id"

    # GitHub pagination could be from 1 to 100.
    page_size = 100

    # These fields will be used for data clearing. Put here keys which represent
    # objects `{}`, like `user`, `actor` etc.
    object_fields = ()

    # These fields will be used for data clearing. Put here keys which represent
    # lists `[]`, like `labels`, `assignees` etc.
    list_fields = ()

    def __init__(self, repository: str, **kwargs):
        super().__init__(**kwargs)
        self.owner, self.repo = repository.split("/")
        self.repository = repository
        self._page = 1

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if response.json():
            self._page += 1
            return {"page": self._page}

    # def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
    #     with vcr.use_cassette("wut.json", record_mode="new_episodes", serializer="json"):
    #         yield from super().read_records(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"per_page": self.page_size}

        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # Without sending `User-Agent` header we will be getting `403 Client Error: Forbidden for url` error.
        return {
            "User-Agent": "PostmanRuntime/7.28.0",
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in response.json():  # GitHub puts records in an array.
            yield self.transform(record=record)

    def transform(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Use this method to:
            - remove excessive fields from record;
            - minify subelements in the record. For example, if you have `reviews` record which looks like this:
            {
              "id": 671782869,
              "node_id": "MDE3OlB1bGxSZXF1ZXN0UmV2aWV3NjcxNzgyODY5",
              "user": {
                "login": "keu",
                "id": 1619536,
                ...
              },
              "body": "lgtm, just  small comment",
              "state": "CHANGES_REQUESTED",
              "html_url": "https://github.com/airbytehq/airbyte/pull/3734#pullrequestreview-671782869",
              "pull_request_url": "https://api.github.com/repos/airbytehq/airbyte/pulls/3734",
              "author_association": "MEMBER",
              "_links": {
                "html": {
                  "href": "https://github.com/airbytehq/airbyte/pull/3734#pullrequestreview-671782869"
                },
                "pull_request": {
                  "href": "https://api.github.com/repos/airbytehq/airbyte/pulls/3734"
                }
              },
              "submitted_at": "2021-05-30T01:14:37Z",
              "commit_id": "be921b0a5a1c5b17539c92420aa231f58c055169"
            }

            `user` subelement contains almost all possible fields fo user and it's not optimal to store such data in
            `reviews` record. We may leave only `user.id` field and save in to `user_id` field in the record. So if you
            need to do something similar with your record you may use this method.
        """
        for field in self.object_fields:
            field_value = record.pop(field, None)
            record[f"{field}_id"] = field_value.get("id") if field_value else None

        for field in self.list_fields:
            field_values = record.pop(field, [])
            record[field] = [value["id"] for value in field_values]

        return record


class Assignees(GithubStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/assignees"


class Reviews(GithubStream):
    object_fields = ("user",)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        pull_request_number = stream_slice["pull_request_number"]
        return f"repos/{self.repository}/pulls/{pull_request_number}/reviews"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        pull_requests_stream = PullRequests(authenticator=self.authenticator, repository=self.repository)
        for pull_request in pull_requests_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"pull_request_number": pull_request["number"]}


class Collaborators(GithubStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/collaborators"


class Releases(GithubStream):
    object_fields = ("author",)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/releases"

    def transform(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        record = super().transform(record=record)

        assets = record.get("assets", [])
        for asset in assets:
            uploader = asset.pop("uploader", None)
            asset["uploader_id"] = uploader.get("id") if uploader else None

        return record


class Events(GithubStream):
    object_fields = (
        "actor",
        "repo",
        "org",
    )

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/events"


class Comments(GithubStream):
    object_fields = ("user",)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/issues/comments"


class PullRequests(GithubStream):
    object_fields = (
        "user",
        "milestone",
        "assignee",
    )
    list_fields = (
        "labels",
        "assignees",
        "requested_reviewers",
        "requested_teams",
    )

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        with vcr.use_cassette(cache_file.name, record_mode="new_episodes", serializer="json"):
            yield from super().read_records(**kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/pulls"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["state"] = "all"
        return params

    def transform(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        record = super().transform(record=record)

        head = record.get("head", {})
        head_user = head.pop("user", None)
        head["user_id"] = head_user.get("id") if head_user else None
        head_repo = head.pop("repo", None)
        head["repo_id"] = head_repo.get("id") if head_repo else None

        base = record.get("base", {})
        base_user = base.pop("user", None)
        base["user_id"] = base_user.get("id") if base_user else None
        base_repo = base.pop("repo", None)
        base["repo_id"] = base_repo.get("id") if base_repo else None

        return record


class CommitComments(GithubStream):
    object_fields = ("user",)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/comments"


class IssueMilestones(GithubStream):
    object_fields = ("creator",)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/milestones"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["state"] = "all"
        return params


class Commits(GithubStream):
    primary_key = "sha"
    object_fields = (
        "author",
        "committer",
    )

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/commits"


class Stargazers(GithubStream):
    primary_key = "user_id"
    object_fields = ("user",)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/stargazers"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        # We need to send below header if we want to get `starred_at` field. See docs (Alternative response with
        # star creation timestamps) - https://docs.github.com/en/rest/reference/activity#list-stargazers.
        headers["Accept"] = "application/vnd.github.v3.star+json"
        return headers


class Teams(GithubStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"orgs/{self.owner}/teams"


class Projects(GithubStream):
    object_fields = ("creator",)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/projects"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["state"] = "all"
        return params

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        # Projects stream requires sending following `Accept` header. If we won't sent it
        # we'll get `415 Client Error: Unsupported Media Type` error.
        headers["Accept"] = "application/vnd.github.inertia-preview+json"
        return headers


class IssueLabels(GithubStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/labels"


class Issues(GithubStream):
    object_fields = (
        "user",
        "assignee",
        "milestone",
    )
    list_fields = (
        "labels",
        "assignees",
    )

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/issues"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["state"] = "all"
        return params


class IssueEvents(GithubStream):
    object_fields = (
        "actor",
        "issue",
    )

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{self.repository}/issues/events"
