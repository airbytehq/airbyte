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


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class AsanaStream(HttpStream, ABC):
    url_base = "https://app.asana.com/api/1.0/"

    primary_key = "gid"

    def backoff_time(self, response: requests.Response) -> Optional[int]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        next_page = decoded_response.get("next_page")
        if next_page:
            return {"offset": next_page["offset"]}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        # Asana pagination could be from 1 to 100.
        params = {"limit": 100}

        params.update(self.get_opt_fields())

        if next_page_token:
            params.update(next_page_token)

        return params

    def get_opt_fields(self) -> MutableMapping[str, str]:
        opt_fields = list()
        schema = self.get_json_schema()

        for prop, value in schema["properties"].items():
            if "object" in value["type"]:
                opt_fields.append(self._handle_object_type(prop, value))
            elif "array" in value["type"]:
                opt_fields.append(self._handle_array_type(prop, value.get("items", [])))
            else:
                opt_fields.append(prop)

        return {"opt_fields": ",".join(opt_fields)} if opt_fields else dict()

    def _handle_object_type(self, prop: str, value: MutableMapping[str, Any]) -> str:
        return f"{prop}.gid"

    def _handle_array_type(self, prop: str, value: MutableMapping[str, Any]) -> str:
        if "type" in value and "object" in value["type"]:
            return self._handle_object_type(prop, value)

        return prop

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("data", [])  # Asana puts records in a container array "data"


class WorkspaceRelatedStream(AsanaStream, ABC):
    """
    Few streams (Projects, Tags and Users) require passing required `workspace` argument in request.
    So this is basically the whole point of this class - to pass `workspace` argument in request.
    """
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["workspace"] = stream_slice["workspace_gid"]
        return params

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        workspaces_stream = Workspaces(authenticator=self.authenticator)
        workspaces_slices = workspaces_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for workspace_slice in workspaces_slices:
            for workspace in workspaces_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=workspace_slice):
                yield {"workspace_gid": workspace["gid"]}


class ProjectRelatedStream(AsanaStream, ABC):
    """
    Few streams (Sections and Tasks) depends on `project gid`: Sections as a part of url and Tasks as `projects`
    argument in request.
    """

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        projects_stream = Projects(authenticator=self.authenticator)
        projects_slices = projects_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for project_slice in projects_slices:
            for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=project_slice):
                yield {"project_gid": project["gid"]}


class CustomFields(AsanaStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        workspace_gid = stream_slice["workspace_gid"]
        return f"workspaces/{workspace_gid}/custom_fields"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        workspaces_stream = Workspaces(authenticator=self.authenticator)
        for workspace in workspaces_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"workspace_gid": workspace["gid"]}


class Projects(WorkspaceRelatedStream):
    def path(self, **kwargs) -> str:
        return "projects"


class Sections(ProjectRelatedStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        project_gid = stream_slice["project_gid"]
        return f"projects/{project_gid}/sections"


class Stories(AsanaStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        task_gid = stream_slice["task_gid"]
        return f"tasks/{task_gid}/stories"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        tasks_stream = Tasks(authenticator=self.authenticator)
        tasks_slices = tasks_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for task_slice in tasks_slices:
            for task in tasks_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=task_slice):
                yield {"task_gid": task["gid"]}


class Tags(WorkspaceRelatedStream):
    def path(self, **kwargs) -> str:
        return "tags"


class Tasks(ProjectRelatedStream):
    def path(self, **kwargs) -> str:
        return "tasks"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["project"] = stream_slice["project_gid"]
        return params

    def _handle_object_type(self, prop: str, value: dict) -> str:
        if prop == "custom_fields":
            return prop
        elif prop in ("hearts", "likes"):
            return f"{prop}.user.gid"
        elif prop == "memberships":
            return "memberships.(project|section).(gid)"

        return f"{prop}.gid"


class Teams(AsanaStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        workspace_gid = stream_slice["workspace_gid"]
        return f"organizations/{workspace_gid}/teams"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        workspaces_stream = Workspaces(authenticator=self.authenticator)
        workspaces_slices = workspaces_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for workspace_slice in workspaces_slices:
            for workspace in workspaces_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=workspace_slice):
                yield {"workspace_gid": workspace["gid"]}


class TeamMemberships(AsanaStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        team_gid = stream_slice["team_gid"]
        return f"teams/{team_gid}/team_memberships"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        teams_stream = Teams(authenticator=self.authenticator)
        teams_slices = teams_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for team_slice in teams_slices:
            for team in teams_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=team_slice):
                yield {"team_gid": team["gid"]}


class Users(WorkspaceRelatedStream):
    def path(self, **kwargs) -> str:
        return "users"

    def _handle_object_type(self, prop: str, value: MutableMapping[str, Any]) -> str:
        if prop == "photo":
            return prop

        return f"{prop}.gid"


class Workspaces(AsanaStream):
    def path(self, **kwargs) -> str:
        return "workspaces"
