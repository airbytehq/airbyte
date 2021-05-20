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
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
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


class AsanaStreamWorkspacePagination(AsanaStream, ABC):
    """
    Few streams (Projects, Tags and Users) require passing required `workspace` argument in request.
    So this is basically the whole point of this class - to pass `workspace` argument in request.
    """

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        workspaces_stream = Workspaces(authenticator=self.authenticator)
        for workspace in workspaces_stream.read_records(sync_mode=SyncMode.full_refresh):
            stream_state = stream_state or dict()
            pagination_complete = False

            next_page_token = None
            while not pagination_complete:
                request_headers = self.request_headers(
                    stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
                )
                request_params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                request = self._create_prepared_request(
                    path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                    headers=dict(request_headers, **self.authenticator.get_auth_header()),
                    params=dict(request_params, workspace=workspace["gid"]),
                    json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                )

                response = self._send_request(request)
                yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)

                next_page_token = self.next_page_token(response)
                if not next_page_token:
                    pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []


class CustomFields(AsanaStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        workspace_gid = stream_slice["workspace_gid"]
        return f"workspaces/{workspace_gid}/custom_fields"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        workspaces_stream = Workspaces(authenticator=self.authenticator)
        for workspace in workspaces_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"workspace_gid": workspace["gid"]}, **kwargs)


class Projects(AsanaStreamWorkspacePagination):
    def path(self, **kwargs) -> str:
        return "projects"


class Sections(AsanaStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        project_gid = stream_slice["project_gid"]
        return f"projects/{project_gid}/sections"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"project_gid": project["gid"]}, **kwargs)


class Stories(AsanaStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        task_gid = stream_slice["task_gid"]
        return f"tasks/{task_gid}/stories"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        tasks_stream = Tasks(authenticator=self.authenticator)
        for task in tasks_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"task_gid": task["gid"]}, **kwargs)


class Tags(AsanaStreamWorkspacePagination):
    def path(self, **kwargs) -> str:
        return "tags"


class Tasks(AsanaStream):
    def path(self, **kwargs) -> str:
        return "tasks"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        projects_stream = Projects(authenticator=self.authenticator)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"project_gid": project["gid"]}, **kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        params.update({"project": stream_slice["project_gid"]})

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

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        workspaces_stream = Workspaces(authenticator=self.authenticator)
        for workspace in workspaces_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"workspace_gid": workspace["gid"]}, **kwargs)


class TeamMemberships(AsanaStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        team_gid = stream_slice["team_gid"]
        return f"teams/{team_gid}/team_memberships"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        teams_stream = Teams(authenticator=self.authenticator)
        for team in teams_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"team_gid": team["gid"]}, **kwargs)


class Users(AsanaStreamWorkspacePagination):
    def path(self, **kwargs) -> str:
        return "users"

    def _handle_object_type(self, prop: str, value: MutableMapping[str, Any]) -> str:
        if prop == "photo":
            return prop

        return f"{prop}.gid"


class Workspaces(AsanaStream):
    def path(self, **kwargs) -> str:
        return "workspaces"
