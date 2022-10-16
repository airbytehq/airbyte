#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import urllib.parse
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class OrbitStream(HttpStream, ABC):
    url_base = "https://app.orbit.love/api/v1/"

    def __init__(self, workspace: str, start_date: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.workspace = workspace
        self.start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = response.json()
        records = data["data"]
        yield from records


class OrbitStreamPaginated(OrbitStream):
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, str]]:
        decoded_response = response.json()
        links = decoded_response.get("links")
        if not links:
            return None

        next = links.get("next")
        if not next:
            return None

        next_url = urllib.parse.urlparse(next)
        return {str(k): str(v) for (k, v) in urllib.parse.parse_qsl(next_url.query)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = super().request_params(stream_state, stream_slice, next_page_token)
        return {**params, **next_page_token} if next_page_token else params


class Members(OrbitStreamPaginated):
    # Docs: https://docs.orbit.love/reference/members-overview
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.workspace}/members"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["sort"] = "created_at"
        if self.start_date is not None:
            params["start_date"] = self.start_date  # The start_date parameter is filtering the last_activity_occurred_at field
        return params


class Workspace(OrbitStream):
    # Docs: https://docs.orbit.love/reference/get_workspaces-workspace-slug
    # This stream is primarily used for connnection checking.
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"workspaces/{self.workspace}"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = response.json()
        yield data["data"]
