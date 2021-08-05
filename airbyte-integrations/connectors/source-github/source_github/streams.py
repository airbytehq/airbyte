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

import os
import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib import parse

import requests
import vcr
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from requests.exceptions import HTTPError
from vcr.cassette import Cassette


def request_cache() -> Cassette:
    """
    Builds VCR instance.
    It deletes file everytime we create it, normally should be called only once.
    We can't use NamedTemporaryFile here because yaml serializer doesn't work well with empty files.
    """
    filename = "request_cache.yml"
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass

    return vcr.use_cassette(str(filename), record_mode="new_episodes", serializer="yaml")


class GithubStream(HttpStream, ABC):
    cache = request_cache()
    url_base = "https://api.github.com/"

    primary_key = "id"

    # GitHub pagination could be from 1 to 100.
    page_size = 100

    stream_base_params = {}

    # Fields in below variable will be used for data clearing. Put there keys which represent:
    #   - objects `{}`, like `user`, `actor` etc.
    #   - lists `[]`, like `labels`, `assignees` etc.
    fields_to_minimize = ()

    def __init__(self, repository: str, **kwargs):
        super().__init__(**kwargs)
        self.repository = repository

    def path(self, **kwargs) -> str:
        return f"repos/{self.repository}/{self.name}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        links = response.links
        if "next" in links:
            next_link = links["next"]["url"]
            parsed_link = parse.urlparse(next_link)
            page = dict(parse.parse_qsl(parsed_link.query)).get("page")
            return {"page": page}

    def should_retry(self, response: requests.Response) -> bool:
        # We don't call `super()` here because we have custom error handling and GitHub API sometimes returns strange
        # errors. So in `read_records()` we have custom error handling which don't require to call `super()` here.
        return response.headers.get("X-RateLimit-Remaining") == "0" or response.status_code in (
            requests.codes.SERVER_ERROR,
            requests.codes.BAD_GATEWAY,
        )

    def backoff_time(self, response: requests.Response) -> Optional[Union[int, float]]:
        # This method is called if we run into the rate limit. GitHub limits requests to 5000 per hour and provides
        # `X-RateLimit-Reset` header which contains time when this hour will be finished and limits will be reset so
        # we again could have 5000 per another hour.

        if response.status_code == requests.codes.BAD_GATEWAY:
            return 0.5

        reset_time = response.headers.get("X-RateLimit-Reset")
        return float(reset_time) - time.time() if reset_time else 60

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(**kwargs)
        except HTTPError as e:
            error_msg = str(e)

            # This whole try/except situation in `read_records()` isn't good but right now in `self._send_request()`
            # function we have `response.raise_for_status()` so we don't have much choice on how to handle errors.
            # Bocked on https://github.com/airbytehq/airbyte/issues/3514.
            if e.response.status_code == requests.codes.FORBIDDEN:
                error_msg = (
                    f"Syncing `{self.name}` stream isn't available for repository "
                    f"`{self.repository}` and your `access_token`, seems like you don't have permissions for "
                    f"this stream."
                )
            elif e.response.status_code == requests.codes.NOT_FOUND and "/teams?" in error_msg:
                # For private repositories `Teams` stream is not available and we get "404 Client Error: Not Found for
                # url: https://api.github.com/orgs/sherifnada/teams?per_page=100" error.
                error_msg = f"Syncing `Team` stream isn't available for repository `{self.repository}`."

            self.logger.warn(error_msg)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"per_page": self.page_size}

        if next_page_token:
            params.update(next_page_token)

        params.update(self.stream_base_params)

        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        # Without sending `User-Agent` header we will be getting `403 Client Error: Forbidden for url` error.
        return {
            "User-Agent": "PostmanRuntime/7.28.0",
        }

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        for record in response.json():  # GitHub puts records in an array.
            yield self.transform(record=record)

    def transform(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
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
                ... <other fields>
              },
              "body": "lgtm, just  small comment",
              ... <other fields>
            }

            `user` subelement contains almost all possible fields fo user and it's not optimal to store such data in
            `reviews` record. We may leave only `user.id` field and save in to `user_id` field in the record. So if you
            need to do something similar with your record you may use this method.
        """
        for field in self.fields_to_minimize:
            field_value = record.pop(field, None)
            if field_value is None:
                record[field] = field_value
            elif isinstance(field_value, dict):
                record[f"{field}_id"] = field_value.get("id") if field_value else None
            elif isinstance(field_value, list):
                record[field] = [value.get("id") for value in field_value]

        # TODO In the future when we will add support for multiple repositories we will need an additional field in
        #  each stream that will tell which repository the record belongs to. In singer it was `_sdc_repository` field.
        #  You may see an example here:
        #  https://github.com/airbytehq/tap-github/blob/a0530b80d299864a9a106398b74d87c31ecc8a7a/tap_github/__init__.py#L253
        #  We decided to leave this field (and rename it) for future usage when support for multiple repositories
        #  will be added.
        record["_ab_github_repository"] = self.repository

        return record


class SemiIncrementalGithubStream(GithubStream):
    """
    Semi incremental streams are also incremental but with one difference, they:
      - read all records;
      - output only new records.
    This means that semi incremental streams read all records (like full_refresh streams) but do filtering directly
    in the code and output only latest records (like incremental streams).
    """

    cursor_field = "updated_at"

    # This flag is used to indicate that current stream supports `sort` and `direction` request parameters and that
    # we should break processing records if possible. If `sort` is set to `updated` and `direction` is set to `desc`
    # this means that latest records will be at the beginning of the response and after we processed those latest
    # records we can just stop and not process other record. This will increase speed of each incremental stream
    # which supports those 2 request parameters. Currently only `IssueMilestones` and `PullRequests` streams are
    # supporting this.
    is_sorted_descending = False

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        if not self.is_sorted_descending:
            return self.page_size
        return None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state
        object and returning an updated state object.
        """
        state_value = latest_cursor_value = latest_record.get(self.cursor_field)

        if current_stream_state.get(self.repository, {}).get(self.cursor_field):
            state_value = max(latest_cursor_value, current_stream_state[self.repository][self.cursor_field])

        return {self.repository: {self.cursor_field: state_value}}

    def get_starting_point(self, stream_state: Mapping[str, Any]) -> str:
        start_point = self._start_date

        if stream_state and stream_state.get(self.repository, {}).get(self.cursor_field):
            start_point = max(start_point, stream_state[self.repository][self.cursor_field])

        return start_point

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        start_point = self.get_starting_point(stream_state=stream_state)
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            if record.get(self.cursor_field) > start_point:
                yield record
            elif self.is_sorted_descending and record.get(self.cursor_field) < start_point:
                break


class IncrementalGithubStream(SemiIncrementalGithubStream):
    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["since"] = self.get_starting_point(stream_state=stream_state)
        return params


# Below are full refresh streams


class Assignees(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-assignees
    """


class Reviews(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/pulls#list-reviews-for-a-pull-request
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        pull_request_number = stream_slice["pull_request_number"]
        return f"repos/{self.repository}/pulls/{pull_request_number}/reviews"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        pull_requests_stream = PullRequests(authenticator=self.authenticator, repository=self.repository, start_date="")
        for pull_request in pull_requests_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"pull_request_number": pull_request["number"]}


class Collaborators(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-repository-collaborators
    """


class IssueLabels(GithubStream):
    """
    API docs: https://docs.github.com/en/free-pro-team@latest/rest/reference/issues#list-labels-for-a-repository
    """

    def path(self, **kwargs) -> str:
        return f"repos/{self.repository}/labels"


class Teams(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/teams#list-teams
    """

    def path(self, **kwargs) -> str:
        owner, _ = self.repository.split("/")
        return f"orgs/{owner}/teams"


# Below are semi incremental streams


class Releases(SemiIncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-releases
    """

    cursor_field = "created_at"
    fields_to_minimize = ("author",)

    def transform(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record)

        assets = record.get("assets", [])
        for asset in assets:
            uploader = asset.pop("uploader", None)
            asset["uploader_id"] = uploader.get("id") if uploader else None

        return record


class Events(SemiIncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/activity#list-repository-events
    """

    cursor_field = "created_at"
    fields_to_minimize = (
        "actor",
        "repo",
        "org",
    )


class PullRequests(SemiIncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/pulls#list-pull-requests
    """

    page_size = 50
    fields_to_minimize = (
        "milestone",
        "assignee",
        "labels",
        "assignees",
        "requested_reviewers",
        "requested_teams",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._first_read = True

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Decide if this a first read or not by the presence of the state object
        """
        self._first_read = not bool(stream_state)
        with self.cache:
            yield from super().read_records(stream_state=stream_state, **kwargs)

    def path(self, **kwargs) -> str:
        return f"repos/{self.repository}/pulls"

    def transform(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record)

        for nested in ("head", "base"):
            entry = record.get(nested, {})
            entry["repo_id"] = (record.get("head", {}).pop("repo", {}) or {}).get("id")

        return record

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        base_params = super().request_params(**kwargs)
        # The very first time we read this stream we want to read ascending so we can save state in case of
        # a halfway failure. But if there is state, we read descending to allow incremental behavior.
        params = {"state": "all", "sort": "updated", "direction": "desc" if self.is_sorted_descending else "asc"}

        return {**base_params, **params}

    @property
    def is_sorted_descending(self) -> bool:
        """
        Depending if there any state we read stream in ascending or descending order.
        """
        return self._first_read


class CommitComments(SemiIncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-commit-comments-for-a-repository
    """

    def path(self, **kwargs) -> str:
        return f"repos/{self.repository}/comments"


class IssueMilestones(SemiIncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-milestones
    """

    is_sorted_descending = True
    fields_to_minimize = ("creator",)
    stream_base_params = {
        "state": "all",
        "sort": "updated",
        "direction": "desc",
    }

    def path(self, **kwargs) -> str:
        return f"repos/{self.repository}/milestones"


class Stargazers(SemiIncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/activity#list-stargazers
    """

    primary_key = "user_id"
    cursor_field = "starred_at"

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        base_headers = super().request_headers(**kwargs)
        # We need to send below header if we want to get `starred_at` field. See docs (Alternative response with
        # star creation timestamps) - https://docs.github.com/en/rest/reference/activity#list-stargazers.
        headers = {"Accept": "application/vnd.github.v3.star+json"}

        return {**base_headers, **headers}

    def transform(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        We need to provide the "user_id" for the primary_key attribute
        and don't remove the whole "user" block from the record.
        """
        record = super().transform(record=record)
        record["user_id"] = record.get("user").get("id")
        return record


class Projects(SemiIncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/projects#list-repository-projects
    """

    fields_to_minimize = ("creator",)
    stream_base_params = {
        "state": "all",
    }

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        base_headers = super().request_headers(**kwargs)
        # Projects stream requires sending following `Accept` header. If we won't sent it
        # we'll get `415 Client Error: Unsupported Media Type` error.
        headers = {"Accept": "application/vnd.github.inertia-preview+json"}

        return {**base_headers, **headers}


class IssueEvents(SemiIncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-issue-events-for-a-repository
    """

    cursor_field = "created_at"
    fields_to_minimize = (
        "actor",
        "issue",
    )

    def path(self, **kwargs) -> str:
        return f"repos/{self.repository}/issues/events"


# Below are incremental streams


class Comments(IncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-issue-comments-for-a-repository
    """

    page_size = 30  # `comments` is a large stream so it's better to set smaller page size.

    def path(self, **kwargs) -> str:
        return f"repos/{self.repository}/issues/comments"


class Commits(IncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-issue-comments-for-a-repository
    """

    primary_key = "sha"
    cursor_field = "created_at"
    fields_to_minimize = (
        "author",
        "committer",
    )

    def transform(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record)

        # Record of the `commits` stream doesn't have an updated_at/created_at field at the top level (so we could
        # just write `record["updated_at"]` or `record["created_at"]`). Instead each record has such value in
        # `commit.author.date`. So the easiest way is to just enrich the record returned from API with top level
        # field `created_at` and use it as cursor_field.
        record["created_at"] = record["commit"]["author"]["date"]

        return record


class Issues(IncrementalGithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-repository-issues
    """

    page_size = 50  # `issues` is a large stream so it's better to set smaller page size.

    fields_to_minimize = (
        "assignee",
        "milestone",
        "labels",
        "assignees",
    )
    stream_base_params = {
        "state": "all",
        "sort": "updated",
        "direction": "asc",
    }
