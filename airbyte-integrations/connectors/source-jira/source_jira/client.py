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

from functools import partial
from json.decoder import JSONDecodeError
from typing import Mapping, Tuple

import requests
from base_python import BaseClient
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError

from .entities import ENTITIES_MAP


class Client(BaseClient):
    """
    Jira API Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
    """

    API_VERSION = 3

    def __init__(self, api_token, domain, email):
        self.auth = HTTPBasicAuth(email, api_token)
        self.base_api_url = f"https://{domain}/rest/api/{self.API_VERSION}"
        self._issue_keys = []
        self._project_keys = []
        self._workflow_scheme_keys = []
        super().__init__()

    def lists(self, name, url, params, func, **kwargs):
        next_page = None
        while True:
            if next_page:
                response = requests.get(next_page, params=params, auth=self.auth)
            else:
                response = requests.get(f"{self.base_api_url}{url}", params=params, auth=self.auth)
            data = func(response.json())
            yield from data
            if "nextPage" in response.json():
                next_page = response.json()["nextPage"]
            else:
                break

    def _enumerate_methods(self) -> Mapping[str, callable]:
        mapping = super(Client, self)._enumerate_methods()
        for entity, value in ENTITIES_MAP.items():
            if entity not in mapping:
                mapping[entity] = partial(self.lists, name=entity, **value)
        return mapping

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            next(self.lists(name="issue_resolutions", **ENTITIES_MAP["issue_resolutions"]))

        except ConnectionError as error:
            alive, error_msg = False, str(error)
        # If the input domain is incorrect or doesn't exist, then the response would be empty, resulting in a JSONDecodeError
        except JSONDecodeError:
            alive, error_msg = (
                False,
                "Unable to connect to the Jira API with the provided credentials. Please make sure the input credentials and environment are correct.",
            )

        return alive, error_msg

    def _get_issue_keys(self):
        if not self._issue_keys:
            issues_configs = ENTITIES_MAP.get("issues")
            issues_configs["params"] = {}
            for issue in self.lists(name="issues", **issues_configs):
                self._issue_keys.append({"id": issue.get("id"), "key": issue.get("key")})
        return self._issue_keys

    def _get_project_keys(self):
        if not self._project_keys:
            for project in self.lists(name="projects", **ENTITIES_MAP.get("projects")):
                self._project_keys.append({"id": project.get("id"), "key": project.get("key")})
        return self._project_keys

    def _get_workflow_scheme_keys(self):
        if not self._workflow_scheme_keys:
            for workflow in self.lists(name="workflow_schemes", **ENTITIES_MAP.get("workflow_schemes")):
                self._workflow_scheme_keys.append(
                    {
                        "id": workflow.get("id"),
                    }
                )
        return self._workflow_scheme_keys

    def _get_custom_fields(self):
        for field in self.lists(name="issue_fields", **ENTITIES_MAP.get("issue_fields")):
            if field.get("custom"):
                yield field

    def _get_projects_related(self, name, url_name="", query_param="key"):
        url_name = url_name or name
        project_keys = self._get_project_keys()
        for project_key in project_keys:
            query_value = project_key.get(query_param)
            for item in self.lists(name=f"project_{name}", url=f"/project/{query_value}/{url_name}", **ENTITIES_MAP.get(f"project_{name}")):
                yield item

    def stream__avatars(self, fields):
        avatar_types = ("issuetype", "project", "user")
        avatar_configs = ENTITIES_MAP.get("avatars")
        for avatar_type in avatar_types:
            for data in self.lists(name="avatars", url=f"/avatar/{avatar_type}/system", **avatar_configs):
                yield data

    def stream__filter_sharing(self, fields):
        filter_sharing_configs = ENTITIES_MAP.get("filter_sharing")
        for filter_item in self.lists(name="filters", **ENTITIES_MAP.get("filters")):
            filter_item_id = filter_item.get("id")
            for permission in self.lists(name="filter_sharing", url=f"/filter/{filter_item_id}/permission", **filter_sharing_configs):
                yield permission

    def stream__issue_comments(self, fields):
        issue_keys = self._get_issue_keys()
        for item in issue_keys:
            issue_key = item.get("key")
            for comment in self.lists(name="issue_comments", url=f"/issue/{issue_key}/comment", **ENTITIES_MAP.get("issue_comments")):
                yield comment

    def stream__issue_custom_field_contexts(self, fields):
        for field in self._get_custom_fields():
            for context in self.lists(
                name="issue_custom_field_contexts",
                url=f"/field/{field.get('id')}/context",
                **ENTITIES_MAP.get("issue_custom_field_contexts"),
            ):
                yield context

    def stream__issue_properties(self, fields):
        issue_keys = self._get_issue_keys()
        for item in issue_keys:
            issue_key = item.get("key")
            for issue_property_key_item in self.lists(
                name="issue_property_keys", url=f"/issue/{issue_key}/properties", func=lambda v: v["keys"], params={}
            ):
                issue_property_key = issue_property_key_item.get("key")
                for issue_property in self.lists(
                    name="issue_properties",
                    url=f"/issue/{issue_key}/properties/{issue_property_key}",
                    **ENTITIES_MAP.get("issue_properties"),
                ):
                    yield issue_property

    def stream__issue_remote_links(self, fields):
        issue_keys = self._get_issue_keys()
        for item in issue_keys:
            issue_key = item.get("key")
            for comment in self.lists(
                name="issue_remote_links", url=f"/issue/{issue_key}/remotelink", **ENTITIES_MAP.get("issue_remote_links")
            ):
                yield comment

    def stream__issue_votes(self, fields):
        issue_keys = self._get_issue_keys()
        for item in issue_keys:
            issue_key = item.get("key")
            for voter in self.lists(name="issue_votes", url=f"/issue/{issue_key}/votes", **ENTITIES_MAP.get("issue_votes")):
                yield voter

    def stream__issue_watchers(self, fields):
        issue_keys = self._get_issue_keys()
        for item in issue_keys:
            issue_key = item.get("key")
            for watcher in self.lists(name="issue_watchers", url=f"/issue/{issue_key}/watchers", **ENTITIES_MAP.get("issue_watchers")):
                yield watcher

    def stream__issue_worklogs(self, fields):
        issue_keys = self._get_issue_keys()
        for item in issue_keys:
            issue_key = item.get("key")
            for worklog in self.lists(name="issue_watchers", url=f"/issue/{issue_key}/worklog", **ENTITIES_MAP.get("issue_worklogs")):
                yield worklog

    def stream__project_avatars(self, fields):
        for avatar in self._get_projects_related("avatars"):
            yield avatar

    def stream__project_components(self, fields):
        for component in self._get_projects_related("components", url_name="component"):
            yield component

    def stream__project_email(self, fields):
        for email in self._get_projects_related("email", query_param="id"):
            yield email

    def stream__project_permission_schemes(self, fields):
        for schema in self._get_projects_related("permission_schemes", url_name="issuesecuritylevelscheme"):
            yield schema

    def stream__project_versions(self, fields):
        for version in self._get_projects_related("versions", url_name="version"):
            yield version

    def stream__screen_tabs(self, fields):
        for screen in self.lists(name="screens", **ENTITIES_MAP.get("screens")):
            screen_id = screen.get("id")
            for tab in self.lists(name="screen_tabs", url=f"/screens/{screen_id}/tabs", **ENTITIES_MAP.get("screen_tabs")):
                yield tab

    def stream__screen_tab_fields(self, fields):
        for screen in self.lists(name="screens", **ENTITIES_MAP.get("screens")):
            screen_id = screen.get("id")
            for tab in self.lists(name="screen_tabs", url=f"/screens/{screen_id}/tabs", **ENTITIES_MAP.get("screen_tabs")):
                for field in self.lists(
                    name="screen_tab_fields",
                    url=f"/screens/{screen_id}/tabs/{tab.get('id')}/fields",
                    **ENTITIES_MAP.get("screen_tab_fields"),
                ):
                    yield field

    def stream__workflow_scheme_project_associations(self, fields):
        project_keys = self._get_project_keys()
        for project_key in project_keys:
            project_id = project_key.get("id")
            configs = ENTITIES_MAP.get("workflow_scheme_project_associations")
            configs["params"] = {"projectId": project_id}
            for item in self.lists(name="workflow_scheme_project_associations", **configs):
                return item

    def stream__workflow_scheme_drafts(self, fields):
        workflow_keys = self._get_workflow_scheme_keys()
        for workflow_key in workflow_keys:
            workflow_id = workflow_key.get("id")
            for draft in self.lists(
                name="workflow_scheme_drafts", url=f"/workflowscheme/{workflow_id}/draft", **ENTITIES_MAP.get("workflow_scheme_drafts")
            ):
                yield draft
