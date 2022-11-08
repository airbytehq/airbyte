#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import random
import string
from typing import Any, Mapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from source_jira.streams import (
    Dashboards,
    Filters,
    FilterSharing,
    Groups,
    IssueComments,
    IssueFields,
    IssueRemoteLinks,
    Issues,
    IssueVotes,
    IssueWatchers,
    IssueWorklogs,
    ProjectCategories,
    ProjectComponents,
    Projects,
    ProjectVersions,
    Screens,
    Users,
    Workflows,
    WorkflowSchemes,
)


class GeneratorMixin:
    def get_generate_headers(self):
        headers = {"Accept": "application/json", "Content-Type": "application/json", **self.authenticator.get_auth_header()}
        return headers

    def generate_record(
        self,
        payload: Any,
        stream_slice: Optional[Mapping[str, Any]] = None,
    ):
        headers = self.get_generate_headers()
        args = {"method": "POST", "url": self.url_base + self.path(stream_slice=stream_slice), "headers": headers, "data": payload}
        request = requests.Request(**args).prepare()
        self._send_request(request)


class DashboardsGenerator(Dashboards, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-post
    """

    def generate(self):
        for index in range(1, 20):
            payload = json.dumps(
                {
                    "name": f"Test dashboard {index}",
                    "description": "A dashboard to help auditors identify sample of issues to check.",
                    "sharePermissions": [{"type": "loggedin"}],
                }
            )
            self.generate_record(payload)


class FiltersGenerator(Filters, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-post
    """

    def generate(self):
        for index in range(1, 20):
            payload = json.dumps(
                {"jql": "type = Bug and resolution is empty", "name": f"Test filter {index}", "description": "Lists all open bugs"}
            )
            self.generate_record(payload)


class FilterSharingGenerator(FilterSharing, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-post
    """

    def generate(self):
        filters_stream = Filters(authenticator=self.authenticator, domain=self._domain)
        for filters in filters_stream.read_records(sync_mode=SyncMode.full_refresh):
            for index in range(random.randrange(4)):
                group_name = random.choice(["Test group 0", "Test group 1", "Test group 2"])
                payload = json.dumps({"type": "group", "groupname": group_name})
                self.generate_record(payload, stream_slice={"filter_id": filters["id"]})


class GroupsGenerator(Groups, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-post
    """

    def path(self, **kwargs) -> str:
        return "group"

    def generate(self):
        for index in range(20):
            payload = json.dumps({"name": f"Test group {index}"})
            self.generate_record(payload)


class IssuesGenerator(Issues, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-post
    """

    def path(self, **kwargs) -> str:
        return "issue"

    def generate(self):
        projects = ["EX", "IT", "P2", "TESTKEY1"]
        issue_types = ["10001", "10002", "10004"]

        for index in range(1, 76):
            payload = json.dumps(
                {
                    "fields": {
                        "project": {"key": random.choice(projects)},
                        "issuetype": {"id": random.choice(issue_types)},
                        "summary": f"Test {index}",
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [{"type": "paragraph", "content": [{"type": "text", "text": f"Test description {index}"}]}],
                        },
                    }
                }
            )
            self.generate_record(payload)


class IssueCommentsGenerator(IssueComments, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-post
    """

    def generate(self):
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            for index in range(20):
                payload = json.dumps(
                    {
                        "body": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                                            "Pellentesque eget "
                                            "venenatis elit. Duis eu justo eget augue iaculis fermentum. Sed "
                                            "semper quam "
                                            "laoreet nisi egestas at posuere augue semper.",
                                            "type": "text",
                                        }
                                    ],
                                }
                            ],
                        }
                    }
                )
                self.generate_record(payload, stream_slice={"key": issue["key"]})


class IssueFieldsGenerator(IssueFields, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-post
    """

    def generate(self):
        for index in range(1, random.randrange(2, 11)):
            payload = json.dumps(
                {
                    "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:grouppickersearcher",
                    "name": f"New custom field {index}",
                    "description": "Custom field for picking groups",
                    "type": "com.atlassian.jira.plugin.system.customfieldtypes:grouppicker",
                }
            )
            self.generate_record(payload)


class IssueRemoteLinksGenerator(IssueRemoteLinks, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-post
    """

    def generate(self):
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            payload = json.dumps(
                {
                    "application": {"name": "My Acme Tracker", "type": "com.acme.tracker"},
                    "globalId": "system=https://www.mycompany.com/support&id=1",
                    "relationship": "causes",
                    "object": {
                        "summary": "Customer support issue",
                        "icon": {"url16x16": "https://www.mycompany.com/support/ticket.png", "title": "Support Ticket"},
                        "title": "TSTSUP-111",
                        "url": "https://www.mycompany.com/support?id=1",
                        "status": {
                            "icon": {
                                "url16x16": "https://www.mycompany.com/support/resolved.png",
                                "link": "https://www.mycompany.com/support?id=1&details=closed",
                                "title": "Case Closed",
                            },
                            "resolved": True,
                        },
                    },
                }
            )
            self.generate_record(payload, stream_slice={"key": issue["key"]})


class IssueVotesGenerator(IssueVotes, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-votes/#api-rest-api-3-issue-issueidorkey-votes-post
    """

    def generate(self):
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            payload = None
            self.generate_record(payload, stream_slice={"key": issue["key"]})


class IssueWatchersGenerator(IssueWatchers, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-watchers/#api-rest-api-3-issue-issueidorkey-watchers-post
    """

    def generate(self):
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            payload = None
            self.generate_record(payload, stream_slice={"key": issue["key"]})


class IssueWorklogsGenerator(IssueWorklogs, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-id-get
    """

    def generate(self):
        issues_stream = Issues(authenticator=self.authenticator, domain=self._domain)
        for issue in issues_stream.read_records(sync_mode=SyncMode.full_refresh):
            for index in range(random.randrange(1, 6)):
                payload = json.dumps(
                    {
                        "timeSpentSeconds": random.randrange(600, 12000),
                        "comment": {
                            "type": "doc",
                            "version": 1,
                            "content": [{"type": "paragraph", "content": [{"text": f"I did some work here. {index}", "type": "text"}]}],
                        },
                        "started": "2021-04-15T01:48:52.747+0000",
                    }
                )
                self.generate_record(payload, stream_slice={"key": issue["key"]})


class ProjectsGenerator(Projects, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-post
    """

    def path(self, **kwargs) -> str:
        return "project"

    def generate(self):
        for index in range(1, 51):
            payload = json.dumps(
                {
                    "key": f"TESTKEY{index}",
                    "name": f"Test project {index}",
                    "projectTypeKey": "software",
                    "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic",
                    "description": f"Test project {index} description",
                    "leadAccountId": "5fc9e78d2730d800760becc4",
                    "assigneeType": "PROJECT_LEAD",
                }
            )
            self.generate_record(payload)


class ProjectCategoriesGenerator(ProjectCategories, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-categories/#api-rest-api-3-projectcategory-post
    """

    def generate(self):
        for index in range(10):
            payload = json.dumps({"name": f"Test category {index}", "description": f"Test Project Category {index}"})
            self.generate_record(payload)


class ProjectComponentsGenerator(ProjectComponents, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/#api-rest-api-3-component-post
    """

    def path(self, **kwargs) -> str:
        return "component"

    def generate(self):
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            for index in range(random.randrange(6)):
                payload = json.dumps(
                    {
                        "isAssigneeTypeValid": False,
                        "name": f"Component {index}",
                        "description": "This is a Jira component",
                        "project": project.get("key"),
                        "assigneeType": "PROJECT_LEAD",
                        "leadAccountId": "5fc9e78d2730d800760becc4",
                    }
                )
                self.generate_record(payload)


class ProjectVersionsGenerator(ProjectVersions, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-versions/#api-rest-api-3-version-post
    """

    def path(self, **kwargs) -> str:
        return "version"

    def generate(self):
        projects_stream = Projects(authenticator=self.authenticator, domain=self._domain)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            for index in range(random.randrange(6)):
                payload = json.dumps(
                    {
                        "archived": False,
                        "releaseDate": "2010-07-06",
                        "name": f"New Version {index}",
                        "description": "An excellent version",
                        "projectId": project.get("id"),
                        "released": True,
                    }
                )
                self.generate_record(payload)


class ScreensGenerator(Screens, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/#api-rest-api-3-screens-post
    """

    def generate(self):
        for index in range(1, 20):
            payload = json.dumps({"name": f"Test screen {index}", "description": f"Test screen {index}"})
            self.generate_record(payload)


class UsersGenerator(Users, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/#api-rest-api-3-screens-post
    """

    def path(self, **kwargs) -> str:
        return "user"

    def generate(self):
        for index in range(50):
            letters = string.ascii_lowercase
            password = "".join(random.choice(letters) for i in range(12))
            payload = json.dumps(
                {
                    "password": password,
                    "emailAddress": f"test.mail{index}@test.com",
                    "displayName": f"Test user {index}",
                    "name": f"user_{index}",
                }
            )
            self.generate_record(payload)


class WorkflowsGenerator(Workflows, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/#api-rest-api-3-workflowscheme-post
    """

    def path(self, **kwargs) -> str:
        return "workflow"

    def generate(self):
        for index in range(30):
            payload = json.dumps(
                {
                    "name": f"Test workflow {index}",
                    "description": "This is a workflow used for Stories and Tasks",
                    "statuses": [{"id": "1"}],
                    "transitions": [{"name": "Created", "from": [], "to": "1", "type": "initial"}],
                }
            )
            self.generate_record(payload)


class WorkflowSchemesGenerator(WorkflowSchemes, GeneratorMixin):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-post
    """

    def generate(self):
        for index in range(30):
            payload = json.dumps(
                {
                    "defaultWorkflow": "jira",
                    "name": f"Test workflow scheme {index}",
                    "description": "The description of the example workflow scheme.",
                }
            )
            self.generate_record(payload)
