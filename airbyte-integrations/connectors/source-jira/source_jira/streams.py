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

API_VERSION = 3


class JiraStream(HttpStream, ABC):
    """
    Jira API Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
    """

    primary_key: Optional[str] = "id"
    parse_response_root: Optional[str] = None

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
        records = response_json if not self.parse_response_root else response_json.get(self.parse_response_root, [])
        if isinstance(records, list):
            for record in records:
                yield self.transform(record=record, **kwargs)
        else:
            yield self.transform(record=records, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return record


class V1ApiJiraStream(JiraStream, ABC):
    @property
    def url_base(self) -> str:
        return f"https://{self._domain}/rest/agile/1.0/"


class StartDateJiraStream(JiraStream, ABC):
    def __init__(self, start_date: str = "", **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date

    def jql_compare_date(self, stream_state: Mapping[str, Any]) -> Optional[str]:
        issues_state = None
        cursor_exist_in_state: Any = False
        cursor_field = self.cursor_field
        if isinstance(self.cursor_field, str):
            cursor_exist_in_state = stream_state.get(self.cursor_field)
        elif isinstance(self.cursor_field, list) and self.cursor_field:
            cursor_exist_in_state = stream_state
            for cursor_part in self.cursor_field:
                cursor_exist_in_state = stream_state.get(cursor_part)
            cursor_field = cursor_field[-1]
        if cursor_exist_in_state:
            issues_state = pendulum.parse(stream_state.get(cursor_field, self._start_date))
        elif self._start_date:
            issues_state = pendulum.parse(self._start_date)
        if issues_state:
            issues_state_row = issues_state.strftime("%Y/%m/%d %H:%M")
            return f"{cursor_field} > '{issues_state_row}'"
        return None


class IncrementalJiraStream(StartDateJiraStream, ABC):
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        cursor_field = self.cursor_field
        if isinstance(cursor_field, str):
            latest_record = latest_record.get(self.cursor_field)
        elif isinstance(cursor_field, list):
            for cursor_part in cursor_field:
                latest_record = latest_record.get(cursor_part, {})
            cursor_field = cursor_field[-1]
        latest_record_date = pendulum.parse(latest_record)
        stream_state = current_stream_state.get(cursor_field)
        if stream_state:
            return {cursor_field: str(max(latest_record_date, pendulum.parse(stream_state)))}
        else:
            return {cursor_field: str(latest_record_date)}


class ApplicationRoles(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-application-roles/#api-rest-api-3-applicationrole-key-get
    """

    primary_key = None

    def path(self, **kwargs) -> str:
        return "applicationrole"


class Avatars(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-avatars/#api-rest-api-3-avatar-type-system-get
    """

    parse_response_root = "system"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
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

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
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

    cursor_field = ["fields", "updated"]
    parse_response_root = "issues"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        board_id = stream_slice["board_id"]
        return f"board/{board_id}/issue"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
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

    def __init__(self, render_fields: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._render_fields = render_fields

    cursor_field = ["fields", "updated"]
    parse_response_root = "issues"

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

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["expand"] = "description,owner,jql,viewUrl,searchUrl,favourite,favouritedCount,sharePermissions,isWritable,subscriptions"
        return params


class FilterSharing(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-get
    """

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
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
    primary_key = "groupId"

    def path(self, **kwargs) -> str:
        return "group/bulk"


class Issues(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
    """

    cursor_field = ["fields", "updated"]
    parse_response_root = "issues"
    use_cache = True

    def __init__(self, additional_fields: List[str], expand_changelog: bool = False, render_fields: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._additional_fields = additional_fields
        self._expand_changelog = expand_changelog
        self._render_fields = render_fields

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
        params["fields"] = stream_slice["fields"]
        jql_parts = [f"project = '{project_id}'", self.jql_compare_date(stream_state)]
        params["jql"] = " and ".join([p for p in jql_parts if p])
        expand = []
        if self._expand_changelog:
            expand.append("changelog")
        if self._render_fields:
            expand.append("renderedFields")
        if expand:
            params["expand"] = ",".join(expand)
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        stream_args = {"authenticator": self.authenticator, "domain": self._domain, "projects": self._projects}
        field_ids_by_name = IssueFields(**stream_args).field_ids_by_name()
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
        additional_field_names = ["Development", "Story Points", "Story point estimate", "Epic Link", "Sprint"]
        for name in additional_field_names + self._additional_fields:
            if name in field_ids_by_name:
                fields.extend(field_ids_by_name[name])
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

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/comment"

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


class IssueFields(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get
    """

    use_cache = True

    def path(self, **kwargs) -> str:
        return "field"

    def field_ids_by_name(self) -> Mapping[str, List[str]]:
        results = {}
        for f in self.read_records(sync_mode=SyncMode.full_refresh):
            if f["name"] not in results:
                results[f["name"]] = []
            results[f["name"]].append(f["id"])
        return results


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

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
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

    primary_key = None

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

    parse_response_root is commented for the same reason as issue_voters.
    """

    # parse_response_root = "watchers"
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


class IssueWorklogs(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get
    """

    parse_response_root = "worklogs"
    primary_key = None

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/worklog"

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
    primary_key = None

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

    parse_response_root = "values"

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

    parse_response_root = "levels"

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

    parse_response_root = "values"

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
    parse_response_root = "detail"
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
        for issue in self.issues_stream.read_records(sync_mode=SyncMode.full_refresh, stream_state=stream_state):
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

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "screenscheme"


class Sprints(V1ApiJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-agile-1-0-board-boardid-sprint-get
    """

    parse_response_root = "values"
    use_cache = True

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
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

    cursor_field = ["fields", "updated"]
    parse_response_root = "issues"

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
        stream_args = {"authenticator": self.authenticator, "domain": self._domain, "projects": self._projects}
        field_ids_by_name = IssueFields(**stream_args).field_ids_by_name()
        fields = ["key", "status", "updated"]
        for name in ["Story Points", "Story point estimate"]:
            if name in field_ids_by_name:
                fields.extend(field_ids_by_name[name])
        sprints_stream = Sprints(**stream_args)
        for sprints in sprints_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"sprint_id": sprints["id"], "fields": fields}, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["issueId"] = record["id"]
        record["id"] = "-".join([str(stream_slice["sprint_id"]), record["id"]])
        record["sprintId"] = stream_slice["sprint_id"]
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

    primary_key = None

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
