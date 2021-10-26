#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import urllib.parse as urlparse
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

API_VERSION = 3


class JiraStream(HttpStream, ABC):
    """
    Jira API Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
    """

    primary_key = "id"
    parse_response_root = None

    def __init__(self, domain: str, projects: List[str], **kwargs):
        super(JiraStream, self).__init__(**kwargs)
        self._domain = domain
        self._projects = projects

    @property
    def url_base(self) -> str:
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
                max_results = response_data["maxResults"]
                total = response_data["total"]
                end_at = start_at + max_results
                if not end_at > total:
                    params["startAt"] = end_at
                    params["maxResults"] = max_results
        return params

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}

        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json if not self.parse_response_root else response_json.get(self.parse_response_root, [])
        if isinstance(records, list):
            for record in records:
                yield self.transform(record=record, **kwargs)
        else:
            yield self.transform(record=records, **kwargs)

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return record


class V1ApiJiraStream(JiraStream, ABC):
    @property
    def url_base(self) -> str:
        return f"https://{self._domain}/rest/agile/1.0/"


class StartDateJiraStream(JiraStream, ABC):
    def __init__(self, start_date: str = "", **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date

    def jql_compare_date(self, stream_state: Mapping[str, any] = {}) -> Optional[str]:
        issues_state = None
        if stream_state.get(self.cursor_field):
            issues_state = pendulum.parse(stream_state.get(self.cursor_field, self._start_date))
        elif self._start_date:
            issues_state = pendulum.parse(self._start_date)
        if issues_state:
            issues_state_row = issues_state.strftime("%Y/%m/%d %H:%M")
            return f"{self.cursor_field} > '{issues_state_row}'"
        return None


class IncrementalJiraStream(StartDateJiraStream, ABC):
    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_record_date = pendulum.parse(latest_record.get("fields", {}).get(self.cursor_field))
        if current_stream_state:
            current_stream_state = current_stream_state.get(self.cursor_field)
            if current_stream_state:
                return {self.cursor_field: str(max(latest_record_date, pendulum.parse(current_stream_state)))}
        else:
            return {self.cursor_field: str(latest_record_date)}


class ApplicationRoles(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-application-roles/#api-rest-api-3-applicationrole-key-get
    """

    def path(self, **kwargs) -> str:
        return "applicationrole"


class Avatars(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-avatars/#api-rest-api-3-avatar-type-system-get
    """

    parse_response_root = "system"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        avatar_type = stream_slice["avatar_type"]
        return f"avatar/{avatar_type}/system"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        avatar_types = ("issuetype", "project", "user")
        for avatar_type in avatar_types:
            yield from super().read_records(stream_slice={"avatar_type": avatar_type}, **kwargs)


class Boards(V1ApiJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-other-operations/#api-agile-1-0-board-get
    """

    parse_response_root = "values"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "board"

    def request_params(self, stream_slice: Mapping[str, Any], **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        params["projectKeyOrId"] = stream_slice["project_id"]
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"project_id": project["id"], "project_key": project["key"]}, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["projectId"] = stream_slice["project_id"]
        record["projectKey"] = stream_slice["project_key"]
        return record


class BoardIssues(V1ApiJiraStream, IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-agile-1-0-board-boardid-issue-get
    """

    cursor_field = "updated"
    parse_response_root = "issues"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        board_id = stream_slice["board_id"]
        return f"board/{board_id}/issue"

    def request_params(self, stream_state: Mapping[str, Any] = {}, **kwargs):
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["fields"] = ["key", "updated"]
        jql = self.jql_compare_date(stream_state)
        if jql:
            params["jql"] = jql
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        boards_stream = Boards(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for board in boards_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"board_id": board["id"]}, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["boardId"] = stream_slice["board_id"]
        return record


class Dashboards(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-get
    """

    parse_response_root = "dashboards"

    def path(self, **kwargs) -> str:
        return "dashboard"


class Epics(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
    """

    cursor_field = "updated"
    parse_response_root = "issues"

    def path(self, **kwargs) -> str:
        return "search"

    def request_params(self, stream_state: Mapping[str, Any] = {}, stream_slice: Mapping[str, Any] = None, **kwargs):
        project_id = stream_slice["project_id"]
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        params["fields"] = ["summary", "description", "status", "updated"]
        jql_parts = ["issuetype = 'Epic'", f"project = '{project_id}'", self.jql_compare_date(stream_state)]
        params["jql"] = " and ".join([p for p in jql_parts if p])
        params["expand"] = "renderedFields"
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"project_id": project["id"], "project_key": project["key"]}, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["projectId"] = stream_slice["project_id"]
        record["projectKey"] = stream_slice["project_key"]
        return record


class Filters(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-search-get
    """

    parse_response_root = "values"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "filter/search"


class FilterSharing(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-get
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        filter_id = stream_slice["filter_id"]
        return f"filter/{filter_id}/permission"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        filters_stream = Filters(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for filters in filters_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"filter_id": filters["id"]}, **kwargs)


class Groups(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-bulk-get
    """

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "group/bulk"


class Issues(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
    """

    cursor_field = "updated"
    parse_response_root = "issues"
    use_cache = True

    def __init__(self, additional_fields: List[str] = [], expand_changelog: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._additional_fields = additional_fields
        self._expand_changelog = expand_changelog

    def path(self, **kwargs) -> str:
        return "search"

    def request_params(self, stream_state: Mapping[str, Any] = {}, stream_slice: Mapping[str, Any] = None, **kwargs):
        project_id = stream_slice["project_id"]
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        params["fields"] = stream_slice["fields"]
        jql_parts = [f"project = '{project_id}'", self.jql_compare_date(stream_state)]
        params["jql"] = " and ".join([p for p in jql_parts if p])
        if self._expand_changelog:
            params["expand"] = "changelog"
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        stream_args = {"authenticator": self.authenticator, "domain": self._domain, "projects": self._projects}
        field_ids_by_name = IssueFields(**stream_args).field_ids_by_name()
        fields = [
            "assignee",
            "attachment",
            "created",
            "creator",
            "description",
            "issuelinks",
            "issuetype",
            "labels",
            "parent",
            "priority",
            "project",
            "security",
            "status",
            "subtasks",
            "summary",
            "updated",
        ]
        additional_field_names = ["Development", "Story Points", "Story point estimate", "Epic Link", "Sprint"]
        for name in additional_field_names + self._additional_fields:
            if name in field_ids_by_name:
                fields.append(field_ids_by_name[name])
        projects_stream = Projects(**stream_args)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(
                stream_slice={"project_id": project["id"], "project_key": project["key"], "fields": list(set(fields))}, **kwargs
            )

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["projectId"] = stream_slice["project_id"]
        record["projectKey"] = stream_slice["project_key"]
        return record


class IssueComments(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get
    """

    parse_response_root = "comments"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/comment"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain, projects=self._projects, start_date=self._start_date)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


class IssueFields(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get
    """

    use_cache = True

    def path(self, **kwargs) -> str:
        return "field"

    def field_ids_by_name(self) -> Mapping[str, str]:
        return {f["name"]: f["id"] for f in self.read_records(sync_mode=SyncMode.full_refresh)}


class IssueFieldConfigurations(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/#api-rest-api-3-fieldconfiguration-get
    """

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "fieldconfiguration"


class IssueCustomFieldContexts(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-contexts/#api-rest-api-3-field-fieldid-context-get
    """

    parse_response_root = "values"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        field_id = stream_slice["field_id"]
        return f"field/{field_id}/context"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        fields_stream = IssueFields(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for field in fields_stream.read_records(sync_mode=SyncMode.full_refresh):
            if field.get("custom", False):
                yield from super().read_records(stream_slice={"field_id": field["id"]}, **kwargs)


class IssueLinkTypes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-link-types/#api-rest-api-3-issuelinktype-get
    """

    parse_response_root = "issueLinkTypes"

    def path(self, **kwargs) -> str:
        return "issueLinkType"


class IssueNavigatorSettings(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-navigator-settings/#api-rest-api-3-settings-columns-get
    """

    def path(self, **kwargs) -> str:
        return "settings/columns"


class IssueNotificationSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-notification-schemes/#api-rest-api-3-notificationscheme-get
    """

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "notificationscheme"


class IssuePriorities(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-priorities/#api-rest-api-3-priority-get
    """

    def path(self, **kwargs) -> str:
        return "priority"


class IssuePropertyKeys(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-properties/#api-rest-api-3-issue-issueidorkey-properties-get
    """

    parse_response_root = "key"
    use_cache = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/properties"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issue_key = stream_slice["key"]
        yield from super().read_records(stream_slice={"key": issue_key}, **kwargs)


class IssueProperties(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-properties/#api-rest-api-3-issue-issueidorkey-properties-propertykey-get
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        issue_key = stream_slice["issue_key"]
        return f"issue/{issue_key}/properties/{key}"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain, projects=self._projects, start_date=self._start_date)
        issue_property_keys_stream = IssuePropertyKeys(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            for property_key in issue_property_keys_stream.read_records(stream_slice={"key": issue["key"]}, **kwargs):
                yield from super().read_records(stream_slice={"key": property_key["key"], "issue_key": issue["key"]}, **kwargs)


class IssueRemoteLinks(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-get
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/remotelink"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain, projects=self._projects, start_date=self._start_date)
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

    parse_response_root = "issueSecuritySchemes"

    def path(self, **kwargs) -> str:
        return "issuesecurityschemes"


class IssueTypeSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-schemes/#api-rest-api-3-issuetypescheme-get
    """

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "issuetypescheme"


class IssueTypeScreenSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-screen-schemes/#api-rest-api-3-issuetypescreenscheme-get
    """

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "issuetypescreenscheme"


class IssueVotes(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-votes/#api-rest-api-3-issue-issueidorkey-votes-get

    parse_response_root voters is commented, since it contains the <Users>
    objects but does not contain information about exactly votes. The
    original schema self, votes (number), hasVoted (bool) and list of voters.
    The schema is correct but parse_response_root should not be applied.
    """

    # parse_response_root = "voters"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/votes"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain, projects=self._projects, start_date=self._start_date)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


class IssueWatchers(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-watchers/#api-rest-api-3-issue-issueidorkey-watchers-get

    parse_response_root is commented for the same reason as issue_voters.
    """

    # parse_response_root = "watchers"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/watchers"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain, projects=self._projects, start_date=self._start_date)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


class IssueWorklogs(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get
    """

    parse_response_root = "worklogs"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/worklog"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain, projects=self._projects, start_date=self._start_date)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


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

    parse_response_root = "permissions"

    def path(self, **kwargs) -> str:
        return "permissions"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get(self.parse_response_root, {}).values()
        yield from records


class PermissionSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permission-schemes/#api-rest-api-3-permissionscheme-get
    """

    parse_response_root = "permissionSchemes"

    def path(self, **kwargs) -> str:
        return "permissionscheme"


class Projects(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-search-get
    """

    parse_response_root = "values"
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
        yield from []


class ProjectAvatars(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-avatars/#api-rest-api-3-project-projectidorkey-avatars-get
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
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

    parse_response_root = "values"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
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

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
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

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
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

    def path(self, **kwargs) -> str:
        return "project/type"


class ProjectVersions(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-versions/#api-rest-api-3-project-projectidorkey-version-get
    """

    parse_response_root = "values"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"project/{key}/version"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": project["key"]}, **kwargs)


class Screens(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/#api-rest-api-3-screens-get
    """

    parse_response_root = "values"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "screens"


class ScreenTabs(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tabs/#api-rest-api-3-screens-screenid-tabs-get
    """

    raise_on_http_errors = False
    use_cache = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        screen_id = stream_slice["screen_id"]
        return f"screens/{screen_id}/tabs"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        screens_stream = Screens(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for screen in screens_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from self.read_tab_records(stream_slice={"screen_id": screen["id"]}, **kwargs)

    def read_tab_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        screen_id = stream_slice["screen_id"]
        yield from super().read_records(stream_slice={"screen_id": screen_id}, **kwargs)


class ScreenTabFields(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/#api-rest-api-3-screens-screenid-tabs-tabid-fields-get
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
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

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "screenscheme"


class Sprints(V1ApiJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-agile-1-0-board-boardid-sprint-get
    """

    parse_response_root = "values"
    use_cache = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        board_id = stream_slice["board_id"]
        return f"board/{board_id}/sprint"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        boards_stream = Boards(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        for board in boards_stream.read_records(sync_mode=SyncMode.full_refresh):
            if board["type"] == "scrum":
                yield from super().read_records(stream_slice={"board_id": board["id"]}, **kwargs)
        yield from []


class SprintIssues(V1ApiJiraStream, IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/#api-agile-1-0-sprint-sprintid-issue-get
    """

    cursor_field = "updated"
    parse_response_root = "issues"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        sprint_id = stream_slice["sprint_id"]
        return f"sprint/{sprint_id}/issue"

    def request_params(self, stream_state: Mapping[str, Any] = {}, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["fields"] = stream_slice["fields"]
        jql = self.jql_compare_date(stream_state)
        if jql:
            params["jql"] = jql
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        stream_args = {"authenticator": self.authenticator, "domain": self._domain, "projects": self._projects}
        field_ids_by_name = IssueFields(**stream_args).field_ids_by_name()
        fields = ["key", "status", "updated"]
        for name in ["Story Points", "Story point estimate"]:
            if name in field_ids_by_name:
                fields.append(field_ids_by_name[name])
        sprints_stream = Sprints(**stream_args)
        for sprints in sprints_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"sprint_id": sprints["id"], "fields": fields}, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["sprintId"] = stream_slice["sprint_id"]
        return record


class TimeTracking(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-time-tracking/#api-rest-api-3-configuration-timetracking-list-get
    """

    def path(self, **kwargs) -> str:
        return "configuration/timetracking/list"


class Users(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/#api-rest-api-3-users-search-get
    """

    def path(self, **kwargs) -> str:
        return "user/search?query="


class Workflows(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-search-get
    """

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "workflow/search"


class WorkflowSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/#api-rest-api-3-workflowscheme-get
    """

    parse_response_root = "values"

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
