#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

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

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response

        for record in records:
            yield record


class Assignments(GlassfrogStream):
    data_field = "assignments"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class ChecklistItems(GlassfrogStream):
    data_field = "checklist_items"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class Circles(GlassfrogStream):
    data_field = "circles"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class CustomFields(GlassfrogStream):
    data_field = "custom_fields"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class Metrics(GlassfrogStream):
    data_field = "metrics"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class People(GlassfrogStream):
    data_field = "people"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class Projects(GlassfrogStream):
    data_field = "projects"
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.data_field


class Roles(GlassfrogStream):
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
