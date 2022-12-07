#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from requests.auth import AuthBase


class ClockifyStream(HttpStream, ABC):
    url_base = "https://api.clockify.me/api/v1/"
    page_size = 50
    page = 1
    primary_key = None

    def __init__(self, workspace_id: str, **kwargs):
        super().__init__(**kwargs)
        self.workspace_id = workspace_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.json()
        self.page = self.page + 1
        if next_page:
            return {"page": self.page}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {
            "page-size": self.page_size,
        }

        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class Users(ClockifyStream):
    @property
    def use_cache(self) -> bool:
        return True

    def path(self, **kwargs) -> str:
        return f"workspaces/{self.workspace_id}/users"


class Projects(ClockifyStream):
    @property
    def use_cache(self) -> bool:
        return True

    def path(self, **kwargs) -> str:
        return f"workspaces/{self.workspace_id}/projects"


class Clients(ClockifyStream):
    def path(self, **kwargs) -> str:
        return f"workspaces/{self.workspace_id}/clients"


class Tags(ClockifyStream):
    def path(self, **kwargs) -> str:
        return f"workspaces/{self.workspace_id}/tags"


class UserGroups(ClockifyStream):
    def path(self, **kwargs) -> str:
        return f"workspaces/{self.workspace_id}/user-groups"


class TimeEntries(HttpSubStream, ClockifyStream):
    def __init__(self, authenticator: AuthBase, workspace_id: Mapping[str, Any], **kwargs):
        super().__init__(
            authenticator=authenticator,
            workspace_id=workspace_id,
            parent=Users(authenticator=authenticator, workspace_id=workspace_id, **kwargs),
        )

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        self.authenticator (which should be used as the
        authenticator for Users) is object of NoAuth()

        so self._session.auth is used instead
        """
        users_stream = Users(authenticator=self._session.auth, workspace_id=self.workspace_id)
        for user in users_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"user_id": user["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        user_id = stream_slice["user_id"]
        return f"workspaces/{self.workspace_id}/user/{user_id}/time-entries"


class Tasks(HttpSubStream, ClockifyStream):
    def __init__(self, authenticator: AuthBase, workspace_id: Mapping[str, Any], **kwargs):
        super().__init__(
            authenticator=authenticator,
            workspace_id=workspace_id,
            parent=Projects(authenticator=authenticator, workspace_id=workspace_id, **kwargs),
        )

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        self.authenticator (which should be used as the
        authenticator for Projects) is object of NoAuth()

        so self._session.auth is used instead
        """
        projects_stream = Projects(authenticator=self._session.auth, workspace_id=self.workspace_id)
        for project in projects_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"project_id": project["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        project_id = stream_slice["project_id"]
        return f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
