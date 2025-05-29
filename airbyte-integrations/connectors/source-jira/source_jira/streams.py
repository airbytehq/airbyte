#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import logging as Logger
import re
import urllib.parse as urlparse
from abc import ABC
from datetime import timedelta
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl

import pendulum
import requests
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import CheckpointMixin, Stream
from airbyte_cdk.sources.streams.checkpoint.checkpoint_reader import FULL_REFRESH_COMPLETE_STATE
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.http_status_error_handler import HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests.exceptions import HTTPError
from source_jira.type_transfromer import DateTimeTransformer

from .utils import read_full_refresh, read_incremental, safe_max

API_VERSION = 3


class JiraErrorHandler(HttpStatusErrorHandler):
    def __init__(
        self,
        stream_name: str,
        ignore_status_codes: List[int],
        logger: logging.Logger,
        error_mapping: Optional[Mapping[Union[int, str, type[Exception]], ErrorResolution]] = None,
        max_retries: int = 5,
        max_time: timedelta = timedelta(seconds=600),
    ) -> None:
        super().__init__(logger, error_mapping, max_retries, max_time)
        self.stream_name = stream_name
        self.ignore_status_codes = ignore_status_codes

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        # override default error mapping
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code in self.ignore_status_codes:
            error_message = f"Errors: {response_or_exception.json().get('errorMessages')}"

            if response_or_exception.status_code == requests.codes.BAD_REQUEST:
                error_message = f"The user doesn't have permission to the project. Please grant the user to the project. {error_message}"

            return ErrorResolution(
                error_message=f"Stream `{self.stream_name}`. An error occurred, details: {error_message}",
                response_action=ResponseAction.IGNORE,
            )

        return super().interpret_response(response_or_exception)


class JiraAvailabilityStrategy(HttpAvailabilityStrategy):
    """
    Inherit from HttpAvailabilityStrategy with slight modification to 403 and 401 error messages.
    """

    def reasons_for_unavailable_status_codes(self, stream: Stream, logger: Logger, source: Source, error: HTTPError) -> Dict[int, str]:
        reasons_for_codes: Dict[int, str] = {
            requests.codes.FORBIDDEN: "Please check the 'READ' permission(Scopes for Connect apps) and/or the user has Jira Software rights and access.",
            requests.codes.UNAUTHORIZED: "Invalid creds were provided, please check your api token, domain and/or email.",
            requests.codes.NOT_FOUND: "Please check the 'READ' permission(Scopes for Connect apps) and/or the user has Jira Software rights and access.",
        }
        return reasons_for_codes


class JiraStream(HttpStream, ABC):
    """
    Jira API Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
    """

    page_size = 50
    primary_key: Optional[str] = "id"
    extract_field: Optional[str] = None
    api_v1 = False
    # Defines the HTTP status codes for which the slice should be skipped.
    # Reference issue: https://github.com/airbytehq/oncall/issues/2133
    # we should skip the slice with `board id` which doesn't support `sprints`
    # it's generally applied to all streams that might have the same error hit in the future.
    skip_http_status_codes = [requests.codes.BAD_REQUEST]
    raise_on_http_errors = True
    transformer: TypeTransformer = DateTimeTransformer(TransformConfig.DefaultSchemaNormalization)
    # emitting state message after every page read
    state_checkpoint_interval = page_size

    def __init__(self, domain: str, projects: List[str], **kwargs):
        super().__init__(**kwargs)
        self._domain = domain
        self._projects = projects

    @property
    def url_base(self) -> str:
        if self.api_v1:
            return f"https://{self._domain}/rest/agile/1.0/"
        return f"https://{self._domain}/rest/api/{API_VERSION}/"

    @property
    def availability_strategy(self) -> HttpAvailabilityStrategy:
        return JiraAvailabilityStrategy()

    def _get_custom_error(self, response: requests.Response) -> str:
        """Method for specifying custom error messages for errors that will be skipped."""
        return ""

    @property
    def max_retries(self) -> Union[int, None]:
        """Number of retries increased from default 5 to 10, based on issues with Jira. Max waiting time is still default 10 minutes."""
        return 10

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        if isinstance(response_json, dict):
            startAt = response_json.get("startAt")
            if startAt is not None:
                startAt += response_json["maxResults"]
                if "isLast" in response_json:
                    if response_json["isLast"]:
                        return
                elif "total" in response_json:
                    if startAt >= response_json["total"]:
                        return
                return {"startAt": startAt}
        elif isinstance(response_json, list):
            if len(response_json) == self.page_size:
                query_params = dict(parse_qsl(urlparse.urlparse(response.url).query))
                startAt = int(query_params.get("startAt", 0)) + self.page_size
                return {"startAt": startAt}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"maxResults": self.page_size}
        if next_page_token:
            params.update(next_page_token)
        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json if not self.extract_field else response_json.get(self.extract_field, [])
        if isinstance(records, list):
            for record in records:
                yield self.transform(record=record, **kwargs)
        else:
            yield self.transform(record=records, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return record

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(**kwargs)
        except HTTPError as e:
            if not (self.skip_http_status_codes and e.response.status_code in self.skip_http_status_codes):
                raise e
            errors = e.response.json().get("errorMessages")
            custom_error = self._get_custom_error(e.response)
            self.logger.warning(f"Stream `{self.name}`. An error occurred, details: {errors}. Skipping for now. {custom_error}")


class FullRefreshJiraStream(JiraStream):

    """
    This is a temporary solution to avoid incorrect state handling.
    See comments below for more info:
    https://github.com/airbytehq/airbyte/pull/39558#discussion_r1695592075
    https://github.com/airbytehq/airbyte/pull/39558#discussion_r1699539669
    """

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        yield from super().read_records(**kwargs)
        self.state = FULL_REFRESH_COMPLETE_STATE


class StartDateJiraStream(JiraStream, ABC):
    def __init__(
        self,
        start_date: Optional[pendulum.DateTime] = None,
        lookback_window_minutes: pendulum.Duration = pendulum.duration(minutes=0),
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._lookback_window_minutes = lookback_window_minutes
        self._start_date = start_date


class IncrementalJiraStream(StartDateJiraStream, CheckpointMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._starting_point_cache = {}
        self._state = None

    @property
    def state(self) -> Mapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        updated_state = latest_record[self.cursor_field]
        current_stream_state = current_stream_state or {}
        stream_state_value = current_stream_state.get(self.cursor_field, {})
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state[self.cursor_field] = updated_state
        return current_stream_state

    def jql_compare_date(self, stream_state: Mapping[str, Any]) -> Optional[str]:
        compare_date = self.get_starting_point(stream_state)
        if compare_date:
            compare_date = compare_date.strftime("%Y/%m/%d %H:%M")
            return f"{self.cursor_field} >= '{compare_date}'"

    def get_starting_point(self, stream_state: Mapping[str, Any]) -> Optional[pendulum.DateTime]:
        if self.cursor_field not in self._starting_point_cache:
            self._starting_point_cache[self.cursor_field] = self._get_starting_point(stream_state=stream_state)
        return self._starting_point_cache[self.cursor_field]

    def _get_starting_point(self, stream_state: Mapping[str, Any]) -> Optional[pendulum.DateTime]:
        if stream_state:
            stream_state_value = stream_state.get(self.cursor_field)
            if stream_state_value:
                stream_state_value = pendulum.parse(stream_state_value) - self._lookback_window_minutes
                return safe_max(stream_state_value, self._start_date)
        return self._start_date

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        start_point = self.get_starting_point(stream_state=stream_state)
        for record in super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs):
            cursor_value = pendulum.parse(record[self.cursor_field])
            self.state = self._get_updated_state(self.state, record)
            if not start_point or cursor_value >= start_point:
                yield record

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        self._starting_point_cache.clear()
        yield from super().stream_slices(**kwargs)


class Issues(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
    """

    cursor_field = "updated"
    extract_field = "issues"
    use_cache = True
    _expand_fields_list = ["renderedFields", "transitions", "changelog"]

    # Issue: https://github.com/airbytehq/airbyte/issues/26712
    # we should skip the slice with wrong permissions on project level
    skip_http_status_codes = [requests.codes.FORBIDDEN, requests.codes.BAD_REQUEST]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._project_ids = []
        self.issue_fields_stream = IssueFields(authenticator=self._http_client._session.auth, domain=self._domain, projects=self._projects)
        self.projects_stream = Projects(authenticator=self._http_client._session.auth, domain=self._domain, projects=self._projects)

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return JiraErrorHandler(logger=self.logger, stream_name=self.name, ignore_status_codes=self.skip_http_status_codes)

    def path(self, **kwargs) -> str:
        return "search"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["fields"] = "*all"

        jql_parts = [self.jql_compare_date(stream_state)]
        if self._project_ids:
            jql_parts.append(f"project in ({stream_slice.get('project_id')})")
        params["jql"] = " and ".join([p for p in jql_parts if p])
        params["jql"] += f" ORDER BY {self.cursor_field} asc"

        params["expand"] = ",".join(self._expand_fields_list)
        return params

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["projectId"] = record["fields"]["project"]["id"]
        record["projectKey"] = record["fields"]["project"]["key"]
        record["created"] = record["fields"]["created"]
        record["updated"] = record["fields"]["updated"]

        # remove fields that are None
        if "renderedFields" in record:
            record["renderedFields"] = {k: v for k, v in record["renderedFields"].items() if v is not None}
        if "fields" in record:
            record["fields"] = {k: v for k, v in record["fields"].items() if v is not None}
        return record

    def get_project_ids(self):
        return [project["id"] for project in read_full_refresh(self.projects_stream)]

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        self._starting_point_cache.clear()
        self._project_ids = []
        if self._projects:
            self._project_ids = self.get_project_ids()
            if not self._project_ids:
                return
            for project_id in self._project_ids:
                yield {"project_id": project_id}
        else:
            yield from super().stream_slices(**kwargs)

    def _get_custom_error(self, response: requests.Response) -> str:
        if response.status_code == requests.codes.BAD_REQUEST:
            return "The user doesn't have permission to the project. Please grant the user to the project."
        return ""


class IssueFields(FullRefreshJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get

    This stream is a dependency for the Issue stream, which in turn is a dependency for both the IssueComments and IssueWorklogs streams.
    These latter streams cannot be migrated at the moment: https://github.com/airbytehq/airbyte-internal-issues/issues/7522
    """

    use_cache = True

    def path(self, **kwargs) -> str:
        return "field"

    def field_ids_by_name(self) -> Mapping[str, List[str]]:
        results = {}
        for f in read_full_refresh(self):
            results.setdefault(f["name"], []).append(f["id"])
        return results


class Projects(FullRefreshJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-search-get

    This stream is a dependency for the Issue stream, which in turn is a dependency for both the IssueComments and IssueWorklogs streams.
    These latter streams cannot be migrated at the moment: https://github.com/airbytehq/airbyte-internal-issues/issues/7522
    """

    extract_field = "values"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "project/search"

    def request_params(self, **kwargs):
        params = super().request_params(**kwargs)
        params["expand"] = "description,lead"
        params["status"] = ["live", "archived", "deleted"]
        return params

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        for project in super().read_records(**kwargs):
            if not self._projects or project["key"] in self._projects:
                yield project


class IssueWorklogs(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get

    Cannot be migrated at the moment: https://github.com/airbytehq/airbyte-internal-issues/issues/7522
    """

    extract_field = "worklogs"
    cursor_field = "updated"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.issues_stream = Issues(
            authenticator=self._http_client._session.auth,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"issue/{stream_slice['key']}/worklog"

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for issue in read_incremental(self.issues_stream, stream_state=stream_state):
            stream_slice = {"key": issue["key"]}
            yield from super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs)


class IssueComments(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get

    Cannot be migrated at the moment: https://github.com/airbytehq/airbyte-internal-issues/issues/7522
    """

    extract_field = "comments"
    cursor_field = "updated"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.issues_stream = Issues(
            authenticator=self._http_client._session.auth,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"issue/{stream_slice['key']}/comment"

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for issue in read_incremental(self.issues_stream, stream_state=stream_state):
            stream_slice = {"key": issue["key"]}
            yield from super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["issueId"] = stream_slice["key"]
        return record


class PullRequests(IncrementalJiraStream):
    """
    This stream uses an undocumented internal API endpoint used by the Jira
    webapp. Jira does not publish any specifications about this endpoint, so the
    only way to get details about it is to use a web browser, view a Jira issue
    that has a linked pull request, and inspect the network requests using the
    browser's developer console.
    """

    cursor_field = "updated"
    extract_field = "detail"
    raise_on_http_errors = False

    pr_regex = r"(?P<prDetails>PullRequestOverallDetails{openCount=(?P<open>[0-9]+), mergedCount=(?P<merged>[0-9]+), declinedCount=(?P<declined>[0-9]+)})|(?P<pr>pullrequest={dataType=pullrequest, state=(?P<state>[a-zA-Z]+), stateCount=(?P<count>[0-9]+)})"

    def __init__(self, issues_stream: Issues, issue_fields_stream: IssueFields, **kwargs):
        super().__init__(**kwargs)
        self.issues_stream = issues_stream
        self.issue_fields_stream = issue_fields_stream

    @property
    def url_base(self) -> str:
        return f"https://{self._domain}/rest/dev-status/1.0/"

    def path(self, **kwargs) -> str:
        return "issue/detail"

    # Currently, only GitHub pull requests are supported by this stream. The
    # requirements for supporting other systems are unclear.
    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        params["issueId"] = stream_slice["id"]
        params["applicationType"] = "GitHub"
        params["dataType"] = "branch"
        return params

    def has_pull_requests(self, dev_field) -> bool:
        if not dev_field or dev_field == "{}":
            return False
        matches = 0
        for match in re.finditer(self.pr_regex, dev_field, re.MULTILINE):
            if match.group("prDetails"):
                matches += int(match.group("open")) + int(match.group("merged")) + int(match.group("declined"))
            elif match.group("pr"):
                matches += int(match.group("count"))
        return matches > 0

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        field_ids_by_name = self.issue_fields_stream.field_ids_by_name()
        dev_field_ids = field_ids_by_name.get("Development", [])
        for issue in read_incremental(self.issues_stream, stream_state=stream_state):
            for dev_field_id in dev_field_ids:
                if self.has_pull_requests(issue["fields"].get(dev_field_id)):
                    yield from super().read_records(
                        stream_slice={"id": issue["id"], self.cursor_field: issue["fields"][self.cursor_field]}, **kwargs
                    )
                    break

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["id"] = stream_slice["id"]
        record[self.cursor_field] = stream_slice[self.cursor_field]
        return record
