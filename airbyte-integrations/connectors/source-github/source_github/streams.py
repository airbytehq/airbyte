#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib import parse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from requests.exceptions import HTTPError

from .graphql import get_query
from .utils import getter

DEFAULT_PAGE_SIZE = 100


class GithubStream(HttpStream, ABC):
    url_base = "https://api.github.com/"

    primary_key = "id"

    # Detect streams with high API load
    large_stream = False

    stream_base_params = {}

    def __init__(self, repositories: List[str], page_size_for_large_streams: int, **kwargs):
        super().__init__(**kwargs)
        self.repositories = repositories

        # GitHub pagination could be from 1 to 100.
        self.page_size = page_size_for_large_streams if self.large_stream else DEFAULT_PAGE_SIZE

        MAX_RETRIES = 3
        adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/{self.name}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for repository in self.repositories:
            yield {"repository": repository}

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
        retry_flag = response.headers.get("X-RateLimit-Remaining") == "0" or response.status_code in (
            requests.codes.SERVER_ERROR,
            requests.codes.BAD_GATEWAY,
        )
        if retry_flag:
            self.logger.info(
                f"Rate limit handling for stream `{self.name}` for the response with {response.status_code} status code with message: {response.text}"
            )

        # Handling secondary rate limits for Github
        # Additional information here: https://docs.github.com/en/rest/guides/best-practices-for-integrators#dealing-with-secondary-rate-limits
        elif response.headers.get("Retry-After"):
            time_delay = int(response.headers["Retry-After"])
            self.logger.info(f"Handling Secondary Rate limits, setting sync delay for {time_delay} second(s)")
            time.sleep(time_delay)
        return retry_flag

    def backoff_time(self, response: requests.Response) -> Union[int, float]:
        # This method is called if we run into the rate limit. GitHub limits requests to 5000 per hour and provides
        # `X-RateLimit-Reset` header which contains time when this hour will be finished and limits will be reset so
        # we again could have 5000 per another hour.

        if response.status_code == requests.codes.SERVER_ERROR:
            return None

        reset_time = response.headers.get("X-RateLimit-Reset")
        backoff_time = float(reset_time) - time.time() if reset_time else 60

        return max(backoff_time, 60)  # This is a guarantee that no negative value will be returned.

    def read_records(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        # get out the stream_slice parts for later use.
        organisation = stream_slice.get("organization", "")
        repository = stream_slice.get("repository", "")
        # Reading records while handling the errors
        try:
            yield from super().read_records(stream_slice=stream_slice, **kwargs)
        except HTTPError as e:
            error_msg = str(e.response.json().get("message"))
            # This whole try/except situation in `read_records()` isn't good but right now in `self._send_request()`
            # function we have `response.raise_for_status()` so we don't have much choice on how to handle errors.
            # Bocked on https://github.com/airbytehq/airbyte/issues/3514.
            if e.response.status_code == requests.codes.NOT_FOUND:
                # A lot of streams are not available for repositories owned by a user instead of an organization.
                if isinstance(self, Organizations):
                    error_msg = (
                        f"Syncing `{self.__class__.__name__}` stream isn't available for organization `{stream_slice['organization']}`."
                    )
                else:
                    error_msg = f"Syncing `{self.__class__.__name__}` stream isn't available for repository `{stream_slice['repository']}`."
            elif e.response.status_code == requests.codes.FORBIDDEN:
                # When using the `check_connection` method, we should raise an error if we do not have access to the repository.
                if isinstance(self, Repositories):
                    raise e
                # When `403` for the stream, that has no access to the organization's teams, based on OAuth Apps Restrictions:
                # https://docs.github.com/en/organizations/restricting-access-to-your-organizations-data/enabling-oauth-app-access-restrictions-for-your-organization
                # For all `Organisation` based streams
                elif isinstance(self, Organizations) or isinstance(self, Teams) or isinstance(self, Users):
                    error_msg = (
                        f"Syncing `{self.name}` stream isn't available for organization `{organisation}`. Full error message: {error_msg}"
                    )
                # For all other `Repository` base streams
                else:
                    error_msg = (
                        f"Syncing `{self.name}` stream isn't available for repository `{repository}`. Full error message: {error_msg}"
                    )
            elif e.response.status_code == requests.codes.GONE and isinstance(self, Projects):
                # Some repos don't have projects enabled and we we get "410 Client Error: Gone for
                # url: https://api.github.com/repos/xyz/projects?per_page=100" error.
                error_msg = f"Syncing `Projects` stream isn't available for repository `{stream_slice['repository']}`."
            elif e.response.status_code == requests.codes.CONFLICT:
                error_msg = (
                    f"Syncing `{self.name}` stream isn't available for repository "
                    f"`{stream_slice['repository']}`, it seems like this repository is empty."
                )
            else:
                self.logger.error(f"Undefined error while reading records: {error_msg}")
                raise e

            self.logger.warn(error_msg)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
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
            yield self.transform(record=record, stream_slice=stream_slice)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record["repository"] = stream_slice["repository"]
        return record


class SemiIncrementalMixin:
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
    is_sorted = False

    def __init__(self, start_date: str = "", **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date
        self._starting_point_cache = {}

    @property
    def __slice_key(self):
        if hasattr(self, "repositories"):
            return "repository"
        return "organization"

    record_slice_key = __slice_key

    def convert_cursor_value(self, value):
        return value

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        if self.is_sorted == "asc":
            return self.page_size

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state
        object and returning an updated state object.
        """
        slice_value = getter(latest_record, self.record_slice_key)
        updated_state = self.convert_cursor_value(latest_record[self.cursor_field])
        stream_state_value = current_stream_state.get(slice_value, {}).get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state.setdefault(slice_value, {})[self.cursor_field] = updated_state
        return current_stream_state

    def _get_starting_point(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any]) -> str:
        if stream_state:
            slice_value = stream_slice[self.__slice_key]
            stream_state_value = stream_state.get(slice_value, {}).get(self.cursor_field)
            if stream_state_value:
                return max(self._start_date, stream_state_value)
        return self._start_date

    def get_starting_point(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any]) -> str:
        slice_value = stream_slice[self.__slice_key]
        if slice_value not in self._starting_point_cache:
            self._starting_point_cache[slice_value] = self._get_starting_point(stream_state, stream_slice)
        return self._starting_point_cache[slice_value]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        start_point = self.get_starting_point(stream_state=stream_state, stream_slice=stream_slice)
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            cursor_value = self.convert_cursor_value(record[self.cursor_field])
            if cursor_value > start_point:
                yield record
            elif self.is_sorted == "desc" and cursor_value < start_point:
                break

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        self._starting_point_cache.clear()
        yield from super().stream_slices(**kwargs)


class IncrementalMixin(SemiIncrementalMixin):
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        since_params = self.get_starting_point(stream_state=stream_state, stream_slice=stream_slice)
        if since_params:
            params["since"] = since_params
        return params


# Below are full refresh streams


class RepositoryStats(GithubStream):
    """
    This stream is technical and not intended for the user, we use it for checking connection with the repository.
    API docs: https://docs.github.com/en/rest/reference/repos#get-a-repository
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class Assignees(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-assignees
    """


class Branches(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-branches
    """

    primary_key = ["repository", "name"]

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/branches"


class Collaborators(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-repository-collaborators
    """


class IssueLabels(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/issues/labels#list-labels-for-a-repository
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/labels"


class Organizations(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/orgs#get-an-organization
    """

    # GitHub pagination could be from 1 to 100.
    page_size = 100

    def __init__(self, organizations: List[str], **kwargs):
        super(GithubStream, self).__init__(**kwargs)
        self.organizations = organizations

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for organization in self.organizations:
            yield {"organization": organization}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"orgs/{stream_slice['organization']}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record["organization"] = stream_slice["organization"]
        return record


class Repositories(SemiIncrementalMixin, Organizations):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-organization-repositories
    """

    is_sorted = "desc"
    stream_base_params = {
        "sort": "updated",
        "direction": "desc",
    }

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"orgs/{stream_slice['organization']}/repos"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        for record in response.json():  # GitHub puts records in an array.
            yield self.transform(record=record, stream_slice=stream_slice)


class Tags(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-repository-tags
    """

    primary_key = ["repository", "name"]

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/tags"


class Teams(Organizations):
    """
    API docs: https://docs.github.com/en/rest/reference/teams#list-teams
    """

    use_cache = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"orgs/{stream_slice['organization']}/teams"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        for record in response.json():
            yield self.transform(record=record, stream_slice=stream_slice)


class Users(Organizations):
    """
    API docs: https://docs.github.com/en/rest/reference/orgs#list-organization-members
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"orgs/{stream_slice['organization']}/members"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        for record in response.json():
            yield self.transform(record=record, stream_slice=stream_slice)


# Below are semi incremental streams


class Releases(SemiIncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-releases
    """

    cursor_field = "created_at"

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record, stream_slice=stream_slice)

        assets = record.get("assets", [])
        for asset in assets:
            uploader = asset.pop("uploader", None)
            asset["uploader_id"] = uploader.get("id") if uploader else None

        return record


class Events(SemiIncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/activity#list-repository-events
    """

    cursor_field = "created_at"


class PullRequests(SemiIncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/pulls/pulls#list-pull-requests
    """

    use_cache = True
    large_stream = True
    first_read_override_key = "first_read_override"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._first_read = True

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Decide if this a first read or not by the presence of the state object
        """
        self._first_read = not bool(stream_state) or stream_state.get(self.first_read_override_key, False)
        yield from super().read_records(stream_state=stream_state, **kwargs)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/pulls"

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record, stream_slice=stream_slice)

        for nested in ("head", "base"):
            entry = record.get(nested, {})
            entry["repo_id"] = (record.get("head", {}).pop("repo", {}) or {}).get("id")

        return record

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        base_params = super().request_params(**kwargs)
        # The very first time we read this stream we want to read ascending so we can save state in case of
        # a halfway failure. But if there is state, we read descending to allow incremental behavior.
        params = {"state": "all", "sort": "updated", "direction": self.is_sorted}

        return {**base_params, **params}

    @property
    def is_sorted(self) -> str:
        """
        Depending if there any state we read stream in ascending or descending order.
        """
        if self._first_read:
            return "asc"
        return "desc"


class CommitComments(SemiIncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-commit-comments-for-a-repository
    """

    use_cache = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/comments"


class IssueMilestones(SemiIncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-milestones
    """

    is_sorted = "desc"
    stream_base_params = {
        "state": "all",
        "sort": "updated",
        "direction": "desc",
    }

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/milestones"


class Stargazers(SemiIncrementalMixin, GithubStream):
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

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        """
        We need to provide the "user_id" for the primary_key attribute
        and don't remove the whole "user" block from the record.
        """
        record = super().transform(record=record, stream_slice=stream_slice)
        record["user_id"] = record.get("user").get("id")
        return record


class Projects(SemiIncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/projects#list-repository-projects
    """

    use_cache = True
    stream_base_params = {
        "state": "all",
    }

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        base_headers = super().request_headers(**kwargs)
        # Projects stream requires sending following `Accept` header. If we won't sent it
        # we'll get `415 Client Error: Unsupported Media Type` error.
        headers = {"Accept": "application/vnd.github.inertia-preview+json"}

        return {**base_headers, **headers}


class IssueEvents(SemiIncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-issue-events-for-a-repository
    """

    cursor_field = "created_at"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/issues/events"


# Below are incremental streams


class Comments(IncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/issues#list-issue-comments-for-a-repository
    """

    use_cache = True
    large_stream = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/issues/comments"


class Commits(IncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/repos#list-commits

    Pull commits from each branch of each repository, tracking state for each branch
    """

    primary_key = "sha"
    cursor_field = "created_at"

    def __init__(self, branches_to_pull: Mapping[str, List[str]], default_branches: Mapping[str, str], **kwargs):
        super().__init__(**kwargs)
        self.branches_to_pull = branches_to_pull
        self.default_branches = default_branches

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super(IncrementalMixin, self).request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        params["since"] = self.get_starting_point(stream_state=stream_state, stream_slice=stream_slice)
        params["sha"] = stream_slice["branch"]
        return params

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for stream_slice in super().stream_slices(**kwargs):
            repository = stream_slice["repository"]
            for branch in self.branches_to_pull.get(repository, []):
                yield {"branch": branch, "repository": repository}

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record, stream_slice=stream_slice)

        # Record of the `commits` stream doesn't have an updated_at/created_at field at the top level (so we could
        # just write `record["updated_at"]` or `record["created_at"]`). Instead each record has such value in
        # `commit.author.date`. So the easiest way is to just enrich the record returned from API with top level
        # field `created_at` and use it as cursor_field.
        # Include the branch in the record
        record["created_at"] = record["commit"]["author"]["date"]
        record["branch"] = stream_slice["branch"]

        return record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        state_value = latest_cursor_value = latest_record.get(self.cursor_field)
        current_repository = latest_record["repository"]
        current_branch = latest_record["branch"]

        if current_stream_state.get(current_repository):
            repository_commits_state = current_stream_state[current_repository]
            if repository_commits_state.get(self.cursor_field):
                # transfer state from old source version to per-branch version
                if current_branch == self.default_branches[current_repository]:
                    state_value = max(latest_cursor_value, repository_commits_state[self.cursor_field])
                    del repository_commits_state[self.cursor_field]
            elif repository_commits_state.get(current_branch, {}).get(self.cursor_field):
                state_value = max(latest_cursor_value, repository_commits_state[current_branch][self.cursor_field])

        if current_repository not in current_stream_state:
            current_stream_state[current_repository] = {}

        current_stream_state[current_repository][current_branch] = {self.cursor_field: state_value}
        return current_stream_state

    def get_starting_point(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any]) -> str:
        repository = stream_slice["repository"]
        branch = stream_slice["branch"]
        if stream_state:
            stream_state_value = stream_state.get(repository, {}).get(branch, {}).get(self.cursor_field)
            if stream_state_value:
                return max(self._start_date, stream_state_value)
        if branch == self.default_branches[repository]:
            return super().get_starting_point(stream_state=stream_state, stream_slice=stream_slice)
        return self._start_date


class Issues(IncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/issues/issues#list-repository-issues
    """

    use_cache = True
    large_stream = True
    is_sorted = "asc"

    stream_base_params = {
        "state": "all",
        "sort": "updated",
        "direction": "asc",
    }


class ReviewComments(IncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/pulls#list-review-comments-in-a-repository
    """

    use_cache = True
    large_stream = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/pulls/comments"


# Pull request substreams


class PullRequestSubstream(HttpSubStream, SemiIncrementalMixin, GithubStream, ABC):
    def __init__(self, parent: PullRequests, **kwargs):
        super().__init__(parent=parent, **kwargs)

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override the parent PullRequests stream configuration to always fetch records in ascending order
        """
        parent_state = deepcopy(stream_state) or {}
        parent_state[PullRequests.first_read_override_key] = True
        parent_stream_slices = super().stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=parent_state)
        for parent_stream_slice in parent_stream_slices:
            yield {
                "pull_request_updated_at": parent_stream_slice["parent"]["updated_at"],
                "pull_request_number": parent_stream_slice["parent"]["number"],
                "repository": parent_stream_slice["parent"]["repository"],
            }

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        We've already determined the list of pull requests to run the stream against.
        Skip the start_point_map and cursor_field logic in SemiIncrementalMixin.read_records.
        """
        yield from super(SemiIncrementalMixin, self).read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        )


class PullRequestStats(SemiIncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/graphql/reference/objects#pullrequest
    """

    is_sorted = "asc"
    http_method = "POST"

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "graphql"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        nodes = response.json()["data"]["repository"]["pullRequests"]["nodes"]
        for record in nodes:
            record["review_comments"] = sum([node["comments"]["totalCount"] for node in record["review_comments"]["nodes"]])
            record["comments"] = record["comments"]["totalCount"]
            record["commits"] = record["commits"]["totalCount"]
            record["repository"] = record["repository"]["name"]
            if record["merged_by"]:
                record["merged_by"]["type"] = record["merged_by"].pop("__typename")
            yield record

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pageInfo = response.json()["data"]["repository"]["pullRequests"]["pageInfo"]
        if pageInfo["hasNextPage"]:
            return pageInfo["endCursor"]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        organization, name = stream_slice["repository"].split("/")
        query = get_query(owner=organization, name=name, page_size=self.page_size, next_page_token=next_page_token)
        return {"query": query}

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        base_headers = super().request_headers(**kwargs)
        # https://docs.github.com/en/graphql/overview/schema-previews#merge-info-preview
        headers = {"Accept": "application/vnd.github.merge-info-preview+json"}
        return {**base_headers, **headers}


class Reviews(PullRequestSubstream):
    """
    API docs: https://docs.github.com/en/rest/reference/pulls#list-reviews-for-a-pull-request
    """

    cursor_field = "pull_request_updated_at"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"repos/{stream_slice['repository']}/pulls/{stream_slice['pull_request_number']}/reviews"

    # Set the parent stream state's cursor field before fetching its records
    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_state = deepcopy(stream_state) or {}
        for repository in self.repositories:
            if repository in parent_state and self.cursor_field in parent_state[repository]:
                parent_state[repository][self.parent.cursor_field] = parent_state[repository][self.cursor_field]
        yield from super().stream_slices(stream_state=parent_state, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record, stream_slice=stream_slice)
        record[self.cursor_field] = stream_slice[self.cursor_field]
        return record


class PullRequestCommits(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/pulls#list-commits-on-a-pull-request
    """

    primary_key = "sha"

    def __init__(self, parent: HttpStream, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/pulls/{stream_slice['pull_number']}/commits"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"repository": record["repository"], "pull_number": record["number"]}

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record, stream_slice=stream_slice)
        record["pull_number"] = stream_slice["pull_number"]
        return record


# Reactions streams


class ReactionStream(GithubStream, ABC):

    parent_key = "id"
    copy_parent_key = "comment_id"
    cursor_field = "created_at"

    def __init__(self, start_date: str = "", **kwargs):
        super().__init__(**kwargs)
        kwargs["start_date"] = start_date
        self._parent_stream = self.parent_entity(**kwargs)
        self._start_date = start_date

    @property
    @abstractmethod
    def parent_entity(self):
        """
        Specify the class of the parent stream for which receive reactions
        """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        parent_path = self._parent_stream.path(stream_slice=stream_slice, **kwargs)
        return f"{parent_path}/{stream_slice[self.copy_parent_key]}/reactions"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for stream_slice in super().stream_slices(**kwargs):
            for parent_record in self._parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                yield {self.copy_parent_key: parent_record[self.parent_key], "repository": stream_slice["repository"]}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        repository = latest_record["repository"]
        parent_id = str(latest_record[self.copy_parent_key])
        updated_state = latest_record[self.cursor_field]
        stream_state_value = current_stream_state.get(repository, {}).get(parent_id, {}).get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state.setdefault(repository, {}).setdefault(parent_id, {})[self.cursor_field] = updated_state
        return current_stream_state

    def get_starting_point(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any]) -> str:
        if stream_state:
            repository = stream_slice["repository"]
            parent_id = str(stream_slice[self.copy_parent_key])
            stream_state_value = stream_state.get(repository, {}).get(parent_id, {}).get(self.cursor_field)
            if stream_state_value:
                return max(self._start_date, stream_state_value)
        return self._start_date

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        starting_point = self.get_starting_point(stream_state=stream_state, stream_slice=stream_slice)
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            if record[self.cursor_field] > starting_point:
                yield record

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record, stream_slice)
        record[self.copy_parent_key] = stream_slice[self.copy_parent_key]
        return record


class CommitCommentReactions(ReactionStream):
    """
    API docs: https://docs.github.com/en/rest/reference/reactions#list-reactions-for-a-commit-comment
    """

    parent_entity = CommitComments


class IssueCommentReactions(ReactionStream):
    """
    API docs: https://docs.github.com/en/rest/reference/reactions#list-reactions-for-an-issue-comment
    """

    parent_entity = Comments


class IssueReactions(ReactionStream):
    """
    API docs: https://docs.github.com/en/rest/reference/reactions#list-reactions-for-an-issue
    """

    parent_entity = Issues
    parent_key = "number"
    copy_parent_key = "issue_number"


class PullRequestCommentReactions(ReactionStream):
    """
    API docs: https://docs.github.com/en/rest/reference/reactions#list-reactions-for-a-pull-request-review-comment
    """

    parent_entity = ReviewComments


class Deployments(SemiIncrementalMixin, GithubStream):
    """
    API docs: https://docs.github.com/en/rest/deployments/deployments#list-deployments
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/deployments"


class ProjectColumns(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/projects#list-project-columns
    """

    use_cache = True
    cursor_field = "updated_at"

    def __init__(self, parent: HttpStream, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self._start_date = start_date

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"projects/{stream_slice['project_id']}/columns"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"repository": record["repository"], "project_id": record["id"]}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        starting_point = self.get_starting_point(stream_state=stream_state, stream_slice=stream_slice)
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            if record[self.cursor_field] > starting_point:
                yield record

    def get_starting_point(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any]) -> str:
        if stream_state:
            repository = stream_slice["repository"]
            project_id = str(stream_slice["project_id"])
            stream_state_value = stream_state.get(repository, {}).get(project_id, {}).get(self.cursor_field)
            if stream_state_value:
                return max(self._start_date, stream_state_value)
        return self._start_date

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        repository = latest_record["repository"]
        project_id = str(latest_record["project_id"])
        updated_state = latest_record[self.cursor_field]
        stream_state_value = current_stream_state.get(repository, {}).get(project_id, {}).get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state.setdefault(repository, {}).setdefault(project_id, {})[self.cursor_field] = updated_state
        return current_stream_state

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record, stream_slice=stream_slice)
        record["project_id"] = stream_slice["project_id"]
        return record


class ProjectCards(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/projects#list-project-cards
    """

    cursor_field = "updated_at"

    def __init__(self, parent: HttpStream, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self._start_date = start_date

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"projects/columns/{stream_slice['column_id']}/cards"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"repository": record["repository"], "project_id": record["project_id"], "column_id": record["id"]}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        starting_point = self.get_starting_point(stream_state=stream_state, stream_slice=stream_slice)
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            if record[self.cursor_field] > starting_point:
                yield record

    def get_starting_point(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any]) -> str:
        if stream_state:
            repository = stream_slice["repository"]
            project_id = str(stream_slice["project_id"])
            column_id = str(stream_slice["column_id"])
            stream_state_value = stream_state.get(repository, {}).get(project_id, {}).get(column_id, {}).get(self.cursor_field)
            if stream_state_value:
                return max(self._start_date, stream_state_value)
        return self._start_date

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        repository = latest_record["repository"]
        project_id = str(latest_record["project_id"])
        column_id = str(latest_record["column_id"])
        updated_state = latest_record[self.cursor_field]
        stream_state_value = current_stream_state.get(repository, {}).get(project_id, {}).get(column_id, {}).get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state.setdefault(repository, {}).setdefault(project_id, {}).setdefault(column_id, {})[
            self.cursor_field
        ] = updated_state
        return current_stream_state

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record = super().transform(record=record, stream_slice=stream_slice)
        record["project_id"] = stream_slice["project_id"]
        record["column_id"] = stream_slice["column_id"]
        return record


class Workflows(SemiIncrementalMixin, GithubStream):
    """
    Get all workflows of a GitHub repository
    API documentation: https://docs.github.com/en/rest/actions/workflows#list-repository-workflows
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/actions/workflows"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        response = response.json().get("workflows")
        for record in response:
            yield self.transform(record=record, stream_slice=stream_slice)

    def convert_cursor_value(self, value):
        return pendulum.parse(value).in_tz(tz="UTC").format("YYYY-MM-DDTHH:mm:ss[Z]")


class WorkflowRuns(SemiIncrementalMixin, GithubStream):
    """
    Get all workflow runs for a GitHub repository
    API documentation: https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-repository
    """

    # key for accessing slice value from record
    record_slice_key = ["repository", "full_name"]

    # https://docs.github.com/en/actions/managing-workflow-runs/re-running-workflows-and-jobs
    re_run_period = 32  # days

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/actions/runs"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        response = response.json().get("workflow_runs")
        for record in response:
            yield record

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # Records in the workflows_runs stream are naturally descending sorted by `created_at` field.
        # On first sight this is not big deal because cursor_field is `updated_at`.
        # But we still can use `created_at` as a breakpoint because after 30 days period
        # https://docs.github.com/en/actions/managing-workflow-runs/re-running-workflows-and-jobs
        # workflows_runs records cannot be updated. It means if we initially fully synced stream on subsequent incremental sync we need
        # only to look behind on 30 days to find all records which were updated.
        start_point = self.get_starting_point(stream_state=stream_state, stream_slice=stream_slice)
        break_point = (pendulum.parse(start_point) - pendulum.duration(days=self.re_run_period)).to_iso8601_string()
        for record in super(SemiIncrementalMixin, self).read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            cursor_value = record[self.cursor_field]
            created_at = record["created_at"]
            if cursor_value > start_point:
                yield record
            if created_at < break_point:
                break


class TeamMembers(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/teams#list-team-members
    """

    use_cache = True
    primary_key = ["id", "team_slug"]

    def __init__(self, parent: Teams, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"orgs/{stream_slice['organization']}/teams/{stream_slice['team_slug']}/members"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"organization": record["organization"], "team_slug": record["slug"]}

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record["organization"] = stream_slice["organization"]
        record["team_slug"] = stream_slice["team_slug"]
        return record


class TeamMemberships(GithubStream):
    """
    API docs: https://docs.github.com/en/rest/reference/teams#get-team-membership-for-a-user
    """

    primary_key = ["url"]

    def __init__(self, parent: TeamMembers, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"orgs/{stream_slice['organization']}/teams/{stream_slice['team_slug']}/memberships/{stream_slice['username']}"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"organization": record["organization"], "team_slug": record["team_slug"], "username": record["login"]}

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        yield self.transform(response.json(), stream_slice=stream_slice)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record["organization"] = stream_slice["organization"]
        record["team_slug"] = stream_slice["team_slug"]
        record["username"] = stream_slice["username"]
        return record
