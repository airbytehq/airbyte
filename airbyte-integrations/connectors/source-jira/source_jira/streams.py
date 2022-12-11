#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import re
import urllib.parse as urlparse
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from requests.exceptions import HTTPError

from .utils import call_once, read_full_refresh, read_incremental, safe_max

API_VERSION = 3


class JiraStream(HttpStream, ABC):
    """
    Jira API Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
    """

    primary_key: Optional[str] = "id"
    extract_field: Optional[str] = None
    api_v1 = False

    def __init__(self, domain: str, projects: List[str], **kwargs):
        super(JiraStream, self).__init__(**kwargs)
        self._domain = domain
        self._projects = projects

    @property
    def url_base(self) -> str:
        if self.api_v1:
            return f"https://{self._domain}/rest/agile/1.0/"
        return f"https://{self._domain}/rest/api/{API_VERSION}/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        params = {}
        response_data = response.json()
        if "nextPage" in response_data:
            next_page = response_data["nextPage"]
            params = parse_qs(urlparse.urlparse(next_page).query)
        else:
            if all(paging_metadata in response_data for paging_metadata in ("startAt", "maxResults", "total")):
                start_at = response_data["startAt"]
                max_results = int(response_data["maxResults"])
                total = response_data["total"]
                end_at = start_at + max_results
                if not end_at > total:
                    params["startAt"] = end_at
                    params["maxResults"] = max_results
        return params

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params: Dict[str, str] = {}

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


class StartDateJiraStream(JiraStream, ABC):
    def __init__(self, start_date: Optional[pendulum.DateTime] = None, **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date


class IncrementalJiraStream(StartDateJiraStream, ABC):
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        updated_state = latest_record[self.cursor_field]
        stream_state_value = current_stream_state.get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state[self.cursor_field] = updated_state
        return current_stream_state

    def jql_compare_date(self, stream_state: Mapping[str, Any]) -> Optional[str]:
        compare_date = self.get_starting_point(stream_state)
        if compare_date:
            compare_date = compare_date.strftime("%Y/%m/%d %H:%M")
            return f"{self.cursor_field} >= '{compare_date}'"

    @call_once
    def get_starting_point(self, stream_state: Mapping[str, Any]) -> Optional[pendulum.DateTime]:
        if stream_state:
            stream_state_value = stream_state.get(self.cursor_field)
            if stream_state_value:
                stream_state_value = pendulum.parse(stream_state_value)
                return safe_max(stream_state_value, self._start_date)
        return self._start_date

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        start_point = self.get_starting_point(stream_state=stream_state)
        for record in super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs):
            cursor_value = pendulum.parse(record[self.cursor_field])
            if not start_point or cursor_value >= start_point:
                yield record


class ApplicationRoles(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-application-roles/#api-rest-api-3-applicationrole-get
    """

    primary_key = "key"

    def path(self, **kwargs) -> str:
        return "applicationrole"

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(**kwargs)
        except HTTPError as e:
            # Application access permissions can only be edited or viewed by administrators.
            if e.response.status_code != requests.codes.FORBIDDEN:
                raise e


class Avatars(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-avatars/#api-rest-api-3-avatar-type-system-get
    """

    extract_field = "system"
    avatar_types = ("issuetype", "project", "user")

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"avatar/{stream_slice['avatar_type']}/system"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for avatar_type in self.avatar_types:
            yield {"avatar_type": avatar_type}


class Boards(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-other-operations/#api-agile-1-0-board-get
    """

    extract_field = "values"
    use_cache = True
    api_v1 = True

    def path(self, **kwargs) -> str:
        return "board"

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        for board in super().read_records(**kwargs):
            if not self._projects or board["location"]["projectKey"] in self._projects:
                yield board

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["projectId"] = str(record["location"]["projectId"])
        record["projectKey"] = record["location"]["projectKey"]
        return record


class BoardIssues(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-rest-agile-1-0-board-boardid-issue-get
    """

    cursor_field = "updated"
    extract_field = "issues"
    api_v1 = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boards_stream = Boards(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"board/{stream_slice['board_id']}/issue"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["fields"] = ["key", "created", "updated"]
        jql = self.jql_compare_date(stream_state)
        if jql:
            params["jql"] = jql
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for board in read_full_refresh(self.boards_stream):
            yield from super().read_records(stream_slice={"board_id": board["id"]}, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["boardId"] = stream_slice["board_id"]
        record["created"] = record["fields"]["created"]
        record["updated"] = record["fields"]["updated"]
        return record


class Dashboards(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-get
    """

    extract_field = "dashboards"

    def path(self, **kwargs) -> str:
        return "dashboard"


class Epics(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
    """

    cursor_field = "updated"
    extract_field = "issues"

    def __init__(self, render_fields: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._render_fields = render_fields
        self.projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, **kwargs) -> str:
        return "search"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        project_id = stream_slice["project_id"]
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["fields"] = ["summary", "description", "status", "updated"]
        jql_parts = ["issuetype = 'Epic'", f"project = '{project_id}'", self.jql_compare_date(stream_state)]
        params["jql"] = " and ".join([p for p in jql_parts if p])
        if self._render_fields:
            params["expand"] = "renderedFields"
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for project in read_full_refresh(self.projects_stream):
            stream_slice = {"project_id": project["id"], "project_key": project["key"]}
            yield from super().read_records(stream_slice=stream_slice, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["projectId"] = stream_slice["project_id"]
        record["projectKey"] = stream_slice["project_key"]
        issue_fields = record["fields"]
        record["created"] = issue_fields.get("created")
        record["updated"] = issue_fields.get("updated") or issue_fields.get("created")
        return record


class Filters(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-search-get
    """

    extract_field = "values"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "filter/search"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["expand"] = "description,owner,jql,viewUrl,searchUrl,favourite,favouritedCount,sharePermissions,isWritable,subscriptions"
        return params


class FilterSharing(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-get
    """

    def __init__(self, render_fields: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.filters_stream = Filters(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"filter/{stream_slice['filter_id']}/permission"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for filters in read_full_refresh(self.filters_stream):
            yield from super().read_records(stream_slice={"filter_id": filters["id"]}, **kwargs)


class Groups(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-bulk-get
    """

    extract_field = "values"
    primary_key = "groupId"

    def path(self, **kwargs) -> str:
        return "group/bulk"


class Issues(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
    """

    cursor_field = "updated"
    extract_field = "issues"
    use_cache = True

    def __init__(self, additional_fields: List[str], expand_changelog: bool = False, render_fields: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._additional_fields = additional_fields
        self._expand_changelog = expand_changelog
        self._render_fields = render_fields
        self._fields = []
        self._project_ids = []
        self.issue_fields_stream = IssueFields(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        self.projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, **kwargs) -> str:
        return "search"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["fields"] = self._fields
        jql_parts = [self.jql_compare_date(stream_state)]
        if self._project_ids:
            project_ids = ", ".join([f"'{project_id}'" for project_id in self._project_ids])
            jql_parts.append(f"project in ({project_ids})")
        params["jql"] = " and ".join([p for p in jql_parts if p])
        expand = []
        if self._expand_changelog:
            expand.append("changelog")
        if self._render_fields:
            expand.append("renderedFields")
        if expand:
            params["expand"] = ",".join(expand)
        return params

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        self._fields = self.get_fields()
        self._project_ids = []
        if self._projects:
            self._project_ids = self.get_project_ids()
            if not self._project_ids:
                return
        yield from super().read_records(**kwargs)

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["projectId"] = record["fields"]["project"]["id"]
        record["projectKey"] = record["fields"]["project"]["key"]
        record["created"] = record["fields"]["created"]
        record["updated"] = record["fields"]["updated"]
        return record

    def get_project_ids(self):
        return [project["id"] for project in read_full_refresh(self.projects_stream)]

    def get_fields(self):
        fields = [
            "assignee",
            "attachment",
            "components",
            "created",
            "creator",
            "description",
            "issuelinks",
            "issuetype",
            "labels",
            "parent",
            "priority",
            "project",
            "resolutiondate",
            "security",
            "status",
            "subtasks",
            "summary",
            "updated",
        ]
        field_ids_by_name = self.issue_fields_stream.field_ids_by_name()
        additional_field_names = ["Development", "Story Points", "Story point estimate", "Epic Link", "Sprint"]
        for name in additional_field_names + self._additional_fields:
            if name in field_ids_by_name:
                fields.extend(field_ids_by_name[name])
        return fields


class IssueComments(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get
    """

    extract_field = "comments"
    cursor_field = "updated"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.issues_stream = Issues(
            additional_fields=[],
            authenticator=self.authenticator,
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


class IssueFields(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get
    """

    use_cache = True

    def path(self, **kwargs) -> str:
        return "field"

    def field_ids_by_name(self) -> Mapping[str, List[str]]:
        results = {}
        for f in read_full_refresh(self):
            results.setdefault(f["name"], []).append(f["id"])
        return results


class IssueFieldConfigurations(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/#api-rest-api-3-fieldconfiguration-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "fieldconfiguration"


class IssueCustomFieldContexts(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-contexts/#api-rest-api-3-field-fieldid-context-get
    """

    extract_field = "values"
    SKIP_STATUS_CODES = [
        # https://community.developer.atlassian.com/t/get-custom-field-contexts-not-found-returned/48408/2
        # /rest/api/3/field/{fieldId}/context - can return 404 if project style is not "classic"
        requests.codes.NOT_FOUND,
        # Only Jira administrators can access custom field contexts.
        requests.codes.FORBIDDEN,
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.issue_fields_stream = IssueFields(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"field/{stream_slice['field_id']}/context"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for field in read_full_refresh(self.issue_fields_stream):
            if field.get("custom", False):
                try:
                    yield from super().read_records(stream_slice={"field_id": field["id"]}, **kwargs)
                except HTTPError as e:
                    if e.response.status_code not in self.SKIP_STATUS_CODES:
                        raise e


class IssueLinkTypes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-link-types/#api-rest-api-3-issuelinktype-get
    """

    extract_field = "issueLinkTypes"

    def path(self, **kwargs) -> str:
        return "issueLinkType"


class IssueNavigatorSettings(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-navigator-settings/#api-rest-api-3-settings-columns-get
    """

    primary_key = None

    def path(self, **kwargs) -> str:
        return "settings/columns"


class IssueNotificationSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-notification-schemes/#api-rest-api-3-notificationscheme-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "notificationscheme"


class IssuePriorities(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-priorities/#api-rest-api-3-priority-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "priority/search"


class IssuePropertyKeys(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-properties/#api-rest-api-3-issue-issueidorkey-properties-get
    """

    extract_field = "key"
    use_cache = True

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/properties"

    def read_records(self, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping[str, Any]]:
        issue_key = stream_slice["key"]
        yield from super().read_records(stream_slice={"key": issue_key}, **kwargs)


class IssueProperties(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-properties/#api-rest-api-3-issue-issueidorkey-properties-propertykey-get
    """

    primary_key = "key"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        issue_key = stream_slice["issue_key"]
        return f"issue/{issue_key}/properties/{key}"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(
            additional_fields=[],
            authenticator=self.authenticator,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )
        issue_property_keys_stream = IssuePropertyKeys(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            for property_key in issue_property_keys_stream.read_records(stream_slice={"key": issue["key"]}, **kwargs):
                yield from super().read_records(stream_slice={"key": property_key["key"], "issue_key": issue["key"]}, **kwargs)


class IssueRemoteLinks(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-get
    """

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/remotelink"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(
            additional_fields=[],
            authenticator=self.authenticator,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


class IssueResolutions(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-resolutions/#api-rest-api-3-resolution-get
    """

    def path(self, **kwargs) -> str:
        return "resolution"


class IssueSecuritySchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-security-schemes/#api-rest-api-3-issuesecurityschemes-get
    """

    extract_field = "issueSecuritySchemes"

    def path(self, **kwargs) -> str:
        return "issuesecurityschemes"


class IssueTypeSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-schemes/#api-rest-api-3-issuetypescheme-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "issuetypescheme"


class IssueTypeScreenSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-screen-schemes/#api-rest-api-3-issuetypescreenscheme-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "issuetypescreenscheme"


class IssueVotes(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-votes/#api-rest-api-3-issue-issueidorkey-votes-get

    extract_field voters is commented, since it contains the <Users>
    objects but does not contain information about exactly votes. The
    original schema self, votes (number), hasVoted (bool) and list of voters.
    The schema is correct but extract_field should not be applied.
    """

    # extract_field = "voters"
    primary_key = None

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/votes"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(
            additional_fields=[],
            authenticator=self.authenticator,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


class IssueWatchers(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-watchers/#api-rest-api-3-issue-issueidorkey-watchers-get

    extract_field is commented for the same reason as issue_voters.
    """

    # extract_field = "watchers"
    primary_key = None

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/watchers"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(
            additional_fields=[],
            authenticator=self.authenticator,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


class IssueWorklogs(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get
    """

    extract_field = "worklogs"
    cursor_field = "updated"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.issues_stream = Issues(
            additional_fields=[],
            authenticator=self.authenticator,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/worklog"

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for issue in read_incremental(self.issues_stream, stream_state=stream_state):
            stream_slice = {"key": issue["key"]}
            yield from super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs)


class JiraSettings(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-jira-settings/#api-rest-api-3-application-properties-get
    """

    def path(self, **kwargs) -> str:
        return "application-properties"


class Labels(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-labels/#api-rest-api-3-label-get
    """

    def path(self, **kwargs) -> str:
        return "application-properties"


class Permissions(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/#api-rest-api-3-permissions-get
    """

    extract_field = "permissions"
    primary_key = None

    def path(self, **kwargs) -> str:
        return "permissions"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get(self.extract_field, {}).values()
        yield from records


class PermissionSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permission-schemes/#api-rest-api-3-permissionscheme-get
    """

    extract_field = "permissionSchemes"

    def path(self, **kwargs) -> str:
        return "permissionscheme"


class Projects(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-search-get
    """

    extract_field = "values"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "project/search"

    def request_params(self, **kwargs):
        params = super().request_params(**kwargs)
        params["expand"] = "description"
        return params

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        for project in super().read_records(**kwargs):
            if not self._projects or project["key"] in self._projects:
                yield project


class ProjectAvatars(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-avatars/#api-rest-api-3-project-projectidorkey-avatars-get
    """

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"project/{key}/avatars"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        for type_key, records in response_json.items():
            yield from records

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": project["key"]}, **kwargs)


class ProjectCategories(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-categories/#api-rest-api-3-projectcategory-get
    """

    def path(self, **kwargs) -> str:
        return "projectCategory"


class ProjectComponents(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/#api-rest-api-3-project-projectidorkey-component-get
    """

    extract_field = "values"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"project/{key}/component"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": project["key"]}, **kwargs)


class ProjectEmail(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-email/#api-rest-api-3-project-projectid-email-get
    """

    primary_key = None

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        project_id = stream_slice["project_id"]
        return f"project/{project_id}/email"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"project_id": project["id"]}, **kwargs)


class ProjectPermissionSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-permission-schemes/#api-rest-api-3-project-projectkeyorid-securitylevel-get
    """

    extract_field = "levels"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"project/{key}/securitylevel"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": project["key"]}, **kwargs)


class ProjectTypes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-types/#api-rest-api-3-project-type-get
    """

    primary_key = None

    def path(self, **kwargs) -> str:
        return "project/type"


class ProjectVersions(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-versions/#api-rest-api-3-project-projectidorkey-version-get
    """

    extract_field = "values"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"project/{key}/version"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": project["key"]}, **kwargs)


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
                if self.has_pull_requests(issue["fields"][dev_field_id]):
                    yield from super().read_records(
                        stream_slice={"id": issue["id"], self.cursor_field: issue["fields"][self.cursor_field]}, **kwargs
                    )
                    break

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["id"] = stream_slice["id"]
        record[self.cursor_field] = stream_slice[self.cursor_field]
        return record


class Screens(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/#api-rest-api-3-screens-get
    """

    extract_field = "values"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "screens"


class ScreenTabs(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tabs/#api-rest-api-3-screens-screenid-tabs-get
    """

    raise_on_http_errors = False
    use_cache = True

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        screen_id = stream_slice["screen_id"]
        return f"screens/{screen_id}/tabs"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        screens_stream = Screens(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for screen in screens_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from self.read_tab_records(stream_slice={"screen_id": screen["id"]}, **kwargs)

    def read_tab_records(self, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping[str, Any]]:
        screen_id = stream_slice["screen_id"]
        yield from super().read_records(stream_slice={"screen_id": screen_id}, **kwargs)


class ScreenTabFields(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/#api-rest-api-3-screens-screenid-tabs-tabid-fields-get
    """

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        screen_id = stream_slice["screen_id"]
        tab_id = stream_slice["tab_id"]
        return f"screens/{screen_id}/tabs/{tab_id}/fields"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        screens_stream = Screens(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        screen_tabs_stream = ScreenTabs(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for screen in screens_stream.read_records(sync_mode=SyncMode.full_refresh):
            for tab in screen_tabs_stream.read_tab_records(stream_slice={"screen_id": screen["id"]}, **kwargs):
                if id in tab:  # Check for proper tab record since the ScreenTabs stream doesn't throw http errors
                    yield from super().read_records(stream_slice={"screen_id": screen["id"], "tab_id": tab["id"]}, **kwargs)


class ScreenSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-schemes/#api-rest-api-3-screenscheme-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "screenscheme"


class Sprints(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-rest-agile-1-0-board-boardid-sprint-get
    """

    extract_field = "values"
    use_cache = True
    api_v1 = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boards_stream = Boards(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        board_id = stream_slice["board_id"]
        return f"board/{board_id}/sprint"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for board in read_full_refresh(self.boards_stream):
            if board["type"] == "scrum":
                yield from super().read_records(stream_slice={"board_id": board["id"]}, **kwargs)


class SprintIssues(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/#api-rest-agile-1-0-sprint-sprintid-issue-get
    """

    cursor_field = "updated"
    extract_field = "issues"
    api_v1 = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.issue_fields_stream = IssueFields(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        self.sprints_stream = Sprints(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        sprint_id = stream_slice["sprint_id"]
        return f"sprint/{sprint_id}/issue"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["fields"] = stream_slice["fields"]
        jql = self.jql_compare_date(stream_state)
        if jql:
            params["jql"] = jql
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        field_ids_by_name = self.issue_fields_stream.field_ids_by_name()
        fields = ["key", "status", "updated"]
        for name in ["Story Points", "Story point estimate"]:
            if name in field_ids_by_name:
                fields.extend(field_ids_by_name[name])
        for sprint in read_full_refresh(self.sprints_stream):
            stream_slice = {"sprint_id": sprint["id"], "fields": fields}
            yield from super().read_records(stream_slice=stream_slice, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["issueId"] = record["id"]
        record["id"] = "-".join([str(stream_slice["sprint_id"]), record["id"]])
        record["sprintId"] = stream_slice["sprint_id"]
        issue_fields = record["fields"]
        record["created"] = issue_fields.get("created")
        record["updated"] = issue_fields.get("updated") or issue_fields.get("created")
        return record


class TimeTracking(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-time-tracking/#api-rest-api-3-configuration-timetracking-list-get
    """

    primary_key = None

    def path(self, **kwargs) -> str:
        return "configuration/timetracking/list"


class Users(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/#api-rest-api-3-users-search-get
    """

    primary_key = "accountId"
    use_cache = True

    def __init__(self, domain: str, projects: List[str], **kwargs):
        super(JiraStream, self).__init__(**kwargs)
        self._domain = domain
        self._projects = projects
        self._max_results = 100
        self._total = self._max_results
        self._startAt = 0

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        params = {}
        response_data = response.json()

        if users_returned := len(response_data):
            self._total = self._total + users_returned
            self._startAt = self._startAt + users_returned
            params["startAt"] = self._startAt
            params["maxResults"] = self._max_results

        return params

    def path(self, **kwargs) -> str:
        return "users/search"


class UsersGroupsDetailed(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get
    """

    primary_key = "accountId"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["accountId"]
        return f"user?accountId={key}&expand=groups,applicationRoles"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        users_stream = Users(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for user in users_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"accountId": user["accountId"]}, **kwargs)


class Workflows(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-search-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "workflow/search"


class WorkflowSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/#api-rest-api-3-workflowscheme-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "workflowscheme"


class WorkflowStatuses(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-statuses/#api-rest-api-3-status-get
    """

    def path(self, **kwargs) -> str:
        return "status"


class WorkflowStatusCategories(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-status-categories/#api-rest-api-3-statuscategory-get
    """

    def path(self, **kwargs) -> str:
        return "statuscategory"
