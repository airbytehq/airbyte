#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class OrbitStream(HttpStream, ABC):
    url_base = "https://app.orbit.love/api/v1/"

    def __init__(self, workspace: str, **kwargs):
        super().__init__(**kwargs)
        self.workspace = workspace

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        yield response.json()


"""
class OrbitStreamPaginated(OrbitStream):
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if response.links["next"]["url"] != None:
            return {"next_url": response.links["next"]["url"]}
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = super().request_params(stream_state, stream_slice, next_page_token)
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()
"""


class Members(OrbitStream):
    # Docs: https://docs.orbit.love/reference/members-overview

    # TODO: Write a function to access "id" in the "data" array in the schema.
    primary_key = ""

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.workspace}/members"


class Workspace(OrbitStream):
    # Docs: https://docs.orbit.love/reference/get_workspaces-workspace-slug
    # This stream is primarily used for connnection checking.

    # TODO: Write a function to access "id" in the "data" object in the schema.
    primary_key = ""

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"workspaces/{self.workspace}"
