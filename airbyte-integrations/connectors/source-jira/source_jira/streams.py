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

import urllib.parse as urlparse
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional
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

    def __init__(self, domain: str, **kwargs):
        super(JiraStream, self).__init__(**kwargs)
        self._domain = domain

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
            yield from records
        else:
            yield records


class IncrementalJiraStream(JiraStream, ABC):
    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    @abstractmethod
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent
        state object and returning an updated state object.
        """
        return {}


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


class Dashboards(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-get
    """

    parse_response_root = "dashboards"

    def path(self, **kwargs) -> str:
        return "dashboard"


class Filters(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-search-get
    """

    parse_response_root = "values"

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
        filters_stream = Filters(authenticator=self.authenticator, domain=self._domain)
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

    def path(self, **kwargs) -> str:
        return "search"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["fields"] = ["attachment", "issuelinks", "security", "issuetype", "updated"]
        if stream_state.get(self.cursor_field):
            issues_state = pendulum.parse(stream_state.get(self.cursor_field))
            issues_state_row = issues_state.strftime("%Y/%m/%d %H:%M")
            params["jql"] = f"updated > '{issues_state_row}'"
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_record_date = pendulum.parse(latest_record.get("fields", {}).get(self.cursor_field))
        if current_stream_state:
            current_stream_state = current_stream_state.get(self.cursor_field)
            if current_stream_state:
                return {self.cursor_field: str(max(latest_record_date, pendulum.parse(current_stream_state)))}
        else:
            return {self.cursor_field: str(latest_record_date)}


class IssueComments(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get
    """

    parse_response_root = "comments"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/comment"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


class IssueFields(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get
    """

    def path(self, **kwargs) -> str:
        return "field"


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
        fields_stream = IssueFields(authenticator=self.authenticator, domain=self._domain)
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

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/properties"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issue_key = stream_slice["key"]
        yield from super().read_records(stream_slice={"key": issue_key}, **kwargs)


class IssueProperties(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-properties/#api-rest-api-3-issue-issueidorkey-properties-propertykey-get
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        issue_key = stream_slice["issue_key"]
        return f"issue/{issue_key}/properties/{key}"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
        issue_property_keys_stream = IssuePropertyKeys(authenticator=self.authenticator, domain=self._domain)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            for property_key in issue_property_keys_stream.read_records(stream_slice={"key": issue["key"]}, **kwargs):
                yield from super().read_records(stream_slice={"key": property_key["key"], "issue_key": issue["key"]}, **kwargs)


class IssueRemoteLinks(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-get
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/remotelink"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
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


class IssueVotes(JiraStream):
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
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


class IssueWatchers(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-watchers/#api-rest-api-3-issue-issueidorkey-watchers-get

    parse_response_root is commented for the same reason as issue_voters.
    """

    # parse_response_root = "watchers"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/watchers"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)


class IssueWorklogs(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get
    """

    parse_response_root = "worklogs"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        key = stream_slice["key"]
        return f"issue/{key}/worklog"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
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

    def path(self, **kwargs) -> str:
        return "project/search"


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
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain)
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
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain)
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
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain)
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
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain)
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
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"key": project["key"]}, **kwargs)


class Screens(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/#api-rest-api-3-screens-get
    """

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "screens"


class ScreenTabs(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tabs/#api-rest-api-3-screens-screenid-tabs-get
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        screen_id = stream_slice["screen_id"]
        return f"screens/{screen_id}/tabs"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        screens_stream = Screens(authenticator=self.authenticator, domain=self._domain)
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
        screens_stream = Screens(authenticator=self.authenticator, domain=self._domain)
        screen_tabs_stream = ScreenTabs(authenticator=self.authenticator, domain=self._domain)
        for screen in screens_stream.read_records(sync_mode=SyncMode.full_refresh):
            for tab in screen_tabs_stream.read_tab_records(stream_slice={"screen_id": screen["id"]}, **kwargs):
                yield from super().read_records(stream_slice={"screen_id": screen["id"], "tab_id": tab["id"]}, **kwargs)


class ScreenSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-schemes/#api-rest-api-3-screenscheme-get
    """

    parse_response_root = "values"

    def path(self, **kwargs) -> str:
        return "screenscheme"


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
