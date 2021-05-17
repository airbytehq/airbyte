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


from functools import partial
from json.decoder import JSONDecodeError
from typing import Any, Dict, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.sources.deprecated.client import BaseClient
from airbyte_cdk.entrypoint import logger
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
        self._state = {"issues": {"state": None, "state_pk": "created"}, "issue_worklogs": {"state": None, "state_pk": "startedAfter"}}
        super().__init__()

    @staticmethod
    def get_next_page(response: requests.Response, url: str, params: Dict):
        next_page = None
        response_data = response.json()
        if "nextPage" in response_data:
            next_page = response_data["nextPage"]
        else:
            if all(paging_metadata in response_data for paging_metadata in ("startAt", "maxResults", "total")):
                start_at = response_data["startAt"]
                max_results = response_data["maxResults"]
                total = response_data["total"]
                end_at = start_at + max_results
                if not end_at > total:
                    next_page = url
                    params["startAt"] = end_at
                    params["maxResults"] = max_results
        return next_page, params

    def lists(self, name, url, params, extractor, **kwargs):
        next_page = None
        request_params = params
        while True:
            if next_page:
                response = requests.get(next_page, params=request_params, auth=self.auth)
            else:
                response = requests.get(f"{self.base_api_url}{url}", params=request_params, auth=self.auth)
            if response.status_code == 404:
                data = []
            else:
                data = extractor(response.json())
            yield from data
            next_page, request_params = self.get_next_page(response, f"{self.base_api_url}{url}", params)
            if not next_page:
                break

    def get_stream_state(self, name: str) -> Any:
        stream_state = self._state.get(name)
        if stream_state["state"]:
            return {stream_state.get("state_pk"): str(stream_state["state"])}
        return None

    def set_stream_state(self, name: str, state: Any):
        stream_state = self._state.get(name)
        stream_state["state"] = pendulum.parse(state[stream_state.get("state_pk")])

    def stream_has_state(self, name: str) -> bool:
        return name in self._state

    def _enumerate_methods(self) -> Mapping[str, callable]:
        # Many streams are just a wrapper around a call to lists() with some preconfigured params.
        # However, more complicated streams require a custom implementation, which is expressed via
        # a stream__XYZ method. The latter streams are captured via super's _enumerate_methods(),
        # and the former streams are added here via a partial over lists().
        mapping = super(Client, self)._enumerate_methods()
        for entity, value in ENTITIES_MAP.items():
            if entity not in mapping:
                mapping[entity] = partial(self.lists, name=entity, **value)
        return mapping

    @staticmethod
    def _update_cursor(cursor, stream_state):
        if cursor:
            new_state = max(cursor, stream_state["state"]) if stream_state["state"] else cursor
            if new_state != stream_state["state"]:
                logger.info(f"Advancing bookmark for Issues stream from {stream_state['state']} to {new_state}")
                stream_state["state"] = new_state

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
            issues_configs = ENTITIES_MAP.get("issues").copy()
            issues_configs["params"] = {}
            for issue in self.lists(name="issues", **issues_configs):
                self._issue_keys.append(issue.get("key"))
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

    def _get_issues_related(self, name, params=None):
        params = params or {}
        issue_keys = self._get_issue_keys()
        for issue_key in issue_keys:
            configs = {**ENTITIES_MAP.get(f"issue_{name}"), "url": ENTITIES_MAP.get(f"issue_{name}").get("url").format(key=issue_key)}
            if params:
                configs["params"].update(params)
            for item in self.lists(name=f"issue_{name}", **configs):
                yield item

    def _get_projects_related(self, name, query_param="key"):
        project_keys = self._get_project_keys()
        for project_key in project_keys:
            query_value = project_key.get(query_param)
            configs = {
                **ENTITIES_MAP.get(f"project_{name}"),
                "url": ENTITIES_MAP.get(f"project_{name}").get("url").format(**{query_param: query_value}),
            }
            for item in self.lists(name=f"project_{name}", **configs):
                yield item

    def _get_screen_tabs(self):
        for screen in self.lists(name="screens", **ENTITIES_MAP.get("screens")):
            screen_id = screen.get("id")
            screen_tabs_configs = {
                **ENTITIES_MAP.get("screen_tabs"),
                "url": ENTITIES_MAP.get("screen_tabs").get("url").format(id=screen_id),
            }
            for tab in self.lists(name="screen_tabs", **screen_tabs_configs):
                yield {"screen": screen, "tab": tab}

    def stream__avatars(self, fields):
        avatar_types = ("issuetype", "project", "user")
        for avatar_type in avatar_types:
            avatar_configs = {**ENTITIES_MAP.get("avatars"), "url": ENTITIES_MAP.get("avatars").get("url").format(type=avatar_type)}
            for data in self.lists(name="avatars", **avatar_configs):
                yield data

    def stream__filter_sharing(self, fields):
        for filter_item in self.lists(name="filters", **ENTITIES_MAP.get("filters")):
            filter_item_id = filter_item.get("id")
            filter_sharing_configs = {
                **ENTITIES_MAP.get("filter_sharing"),
                "url": ENTITIES_MAP.get("filter_sharing").get("url").format(id=filter_item_id),
            }
            for permission in self.lists(name="filter_sharing", **filter_sharing_configs):
                yield permission

    def stream__issues(self, fields):
        cursor = None
        issues_config = {**ENTITIES_MAP.get("issues")}
        stream_state = self._state.get("issues")
        if stream_state["state"]:
            issues_state_row = stream_state["state"].format("YYYY/MM/DD HH:mm")
            issues_config["params"]["jql"] = f"created > '{issues_state_row}'"
        for issue in self.lists(name="issues", **issues_config):
            "Jira API returns records from newest to oldest"
            if not cursor:
                cursor = pendulum.parse(issue["fields"][stream_state["state_pk"]])
            yield issue

        self._update_cursor(cursor, stream_state)

    def stream__issue_comments(self, fields):
        for comment in self._get_issues_related("comments"):
            yield comment

    def stream__issue_custom_field_contexts(self, fields):
        for field in self._get_custom_fields():
            issue_custom_field_contexts_configs = {
                **ENTITIES_MAP.get("issue_custom_field_contexts"),
                "url": ENTITIES_MAP.get("issue_custom_field_contexts").get("url").format(id=field.get("id")),
            }
            for context in self.lists(name="issue_custom_field_contexts", **issue_custom_field_contexts_configs):
                yield context

    def stream__issue_properties(self, fields):
        issue_keys = self._get_issue_keys()
        for issue_key in issue_keys:
            for issue_property_key_item in self.lists(
                name="issue_property_keys", url=f"/issue/{issue_key}/properties", extractor=lambda v: v["keys"], params={}
            ):
                issue_property_key = issue_property_key_item.get("key")
                issue_properties_configs = {
                    **ENTITIES_MAP.get("issue_properties"),
                    "url": ENTITIES_MAP.get("issue_properties").get("url").format(issue_key=issue_key, property_key=issue_property_key),
                }
                for issue_property in self.lists(name="issue_properties", **issue_properties_configs):
                    yield issue_property

    def stream__issue_remote_links(self, fields):
        for remote_link in self._get_issues_related("remote_links"):
            yield remote_link

    def stream__issue_votes(self, fields):
        for vote in self._get_issues_related("votes"):
            yield vote

    def stream__issue_watchers(self, fields):
        for watcher in self._get_issues_related("watchers"):
            yield watcher

    def stream__issue_worklogs(self, fields):
        cursor = None
        params = {}
        stream_state = self._state.get("issue_worklogs")
        if stream_state["state"]:
            state_row = int(stream_state["state"].timestamp() * 1000)
            params["startedAfter"] = state_row
        for worklog in self._get_issues_related("worklogs", params):
            cursor = pendulum.parse(worklog["created"])
            yield worklog

        self._update_cursor(cursor, stream_state)

    def stream__project_avatars(self, fields):
        for avatar in self._get_projects_related("avatars"):
            yield avatar

    def stream__project_components(self, fields):
        for component in self._get_projects_related("components"):
            yield component

    def stream__project_email(self, fields):
        for email in self._get_projects_related("email", query_param="id"):
            yield email

    def stream__project_permission_schemes(self, fields):
        for schema in self._get_projects_related("permission_schemes"):
            yield schema

    def stream__project_versions(self, fields):
        for version in self._get_projects_related("versions"):
            yield version

    def stream__screen_tabs(self, fields):
        for item in self._get_screen_tabs():
            yield item.get("tab")

    def stream__screen_tab_fields(self, fields):
        for item in self._get_screen_tabs():
            screen_id = item.get("screen").get("id")
            tab_id = item.get("tab").get("id")
            screen_tab_fields_configs = {
                **ENTITIES_MAP.get("screen_tab_fields"),
                "url": ENTITIES_MAP.get("screen_tab_fields").get("url").format(id=screen_id, tab_id=tab_id),
            }
            for field in self.lists(name="screen_tab_fields", **screen_tab_fields_configs):
                yield field

    def stream__workflow_scheme_project_associations(self, fields):
        project_keys = self._get_project_keys()
        for project_key in project_keys:
            project_id = project_key.get("id")
            configs = ENTITIES_MAP.get("workflow_scheme_project_associations")
            configs["params"] = {"projectId": project_id}
            for item in self.lists(name="workflow_scheme_project_associations", **configs):
                return item
