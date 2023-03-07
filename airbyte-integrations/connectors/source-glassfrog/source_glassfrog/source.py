#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from .auth import GlassfrogAuthenticator


# Basic full refresh stream
class GlassfrogStream(HttpStream, ABC):
    url_base = "https://api.glassfrog.com/api/v3/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response

        for record in records:
            yield record


class Assignments(GlassfrogStream):
    # https://documenter.getpostman.com/view/1014385/2SJViY?version=latest#db2934bd-8c07-1951-b273-51fbc2dc6422
    data_field = "assignments"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class ChecklistItems(GlassfrogStream):
    # https://documenter.getpostman.com/view/1014385/2SJViY?version=latest#a81716d4-b492-79ff-1348-9048fd9dc527
    data_field = "checklist_items"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class Circles(GlassfrogStream):
    # https://documenter.getpostman.com/view/1014385/2SJViY?version=latest#ed696857-c3d8-fba1-a174-fbe63de07798
    data_field = "circles"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class CustomFields(GlassfrogStream):
    # https://documenter.getpostman.com/view/1014385/2SJViY?version=latest#901f8ec2-a986-0291-2fa2-281c16622107
    data_field = "custom_fields"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class Metrics(GlassfrogStream):
    # https://documenter.getpostman.com/view/1014385/2SJViY?version=latest#00d4f5fb-d6e5-5521-a77d-bdce50a9fb84
    data_field = "metrics"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class People(GlassfrogStream):
    # https://documenter.getpostman.com/view/1014385/2SJViY?version=latest#78b74b9f-72b7-63fc-a18c-18518932944b
    data_field = "people"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class Projects(GlassfrogStream):
    # https://documenter.getpostman.com/view/1014385/2SJViY?version=latest#110bde88-a319-ae9c-077a-9752fd2f0843
    data_field = "projects"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class Roles(GlassfrogStream):
    # https://documenter.getpostman.com/view/1014385/2SJViY?version=latest#d1f31f7a-1d42-8c86-be1d-a36e640bf993
    data_field = "roles"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


# Source
class SourceGlassfrog(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            url = "https://api.glassfrog.com/api/v3/people"
            headers = {"X-Auth-Token": config["api_key"]}

            r = requests.get(url, headers=headers)
            r.raise_for_status()
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Glassfrog API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = GlassfrogAuthenticator(config=config)
        return [
            Assignments(authenticator=auth),
            ChecklistItems(authenticator=auth),
            Circles(authenticator=auth),
            CustomFields(authenticator=auth),
            Metrics(authenticator=auth),
            People(authenticator=auth),
            Projects(authenticator=auth),
            Roles(authenticator=auth),
        ]
