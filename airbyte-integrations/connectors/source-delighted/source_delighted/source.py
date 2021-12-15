#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import base64
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class DelightedStream(HttpStream, ABC):

    url_base = "https://api.delighted.com/v1/"

    # Page size
    limit = 100

    # Define primary key to all streams as primary key
    primary_key = "id"

    def __init__(self, since: int, **kwargs):
        super().__init__(**kwargs)
        self.since = since

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Getting next page link
        next_page = response.links.get("next", None)
        if next_page:
            return dict(parse_qsl(urlparse(next_page.get("url")).query))
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            params = {"per_page": self.limit, **next_page_token}
        else:
            params = {"per_page": self.limit, "since": self.since}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json()
        yield from records


class IncrementalDelightedStream(DelightedStream, ABC):
    # Getting page size as 'limit' from parrent class
    @property
    def limit(self):
        return super().limit

    state_checkpoint_interval = limit

    @property
    def cursor_field(self) -> str:
        return "created_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, 0), current_stream_state.get(self.cursor_field, 0))}

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        if stream_state:
            params["since"] = stream_state.get(self.cursor_field)
        return params


class People(IncrementalDelightedStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "people.json"


class Unsubscribes(IncrementalDelightedStream):
    cursor_field = "unsubscribed_at"
    primary_key = "person_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "unsubscribes.json"


class Bounces(IncrementalDelightedStream):
    cursor_field = "bounced_at"
    primary_key = "person_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "bounces.json"


class SurveyResponses(IncrementalDelightedStream):
    cursor_field = "updated_at"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "survey_responses.json"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        if stream_state:
            params["updated_since"] = stream_state.get(self.cursor_field)
        return params


# Source
class SourceDelighted(AbstractSource):
    def _get_authenticator(self, config):
        token = base64.b64encode(f"{config['api_key']}:".encode("utf-8")).decode("utf-8")
        return TokenAuthenticator(token=token, auth_method="Basic")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """

        Testing connection availability for the connector.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        try:
            auth = self._get_authenticator(config)
            args = {"authenticator": auth, "since": config["since"]}
            stream = SurveyResponses(**args)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._get_authenticator(config)
        args = {"authenticator": auth, "since": config["since"]}
        return [People(**args), Unsubscribes(**args), Bounces(**args), SurveyResponses(**args)]
