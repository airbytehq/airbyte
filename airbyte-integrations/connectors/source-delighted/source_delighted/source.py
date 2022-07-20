#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import base64
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import pendulum
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
    page = 1

    # Define primary key to all streams as primary key
    primary_key = "id"

    def __init__(self, since: pendulum.datetime, **kwargs):
        super().__init__(**kwargs)
        self.since = since

    @property
    def since_ts(self) -> int:
        return int(self.since.timestamp())

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        if len(response_data) == self.limit:
            self.page += 1
            return {"page": self.page}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"per_page": self.limit, "since": self.since_ts}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class IncrementalDelightedStream(DelightedStream, ABC):
    # Getting page size as 'limit' from parent class
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

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response=response, stream_state=stream_state, **kwargs):
            if self.cursor_field not in stream_state or record[self.cursor_field] > stream_state[self.cursor_field]:
                yield record


class People(IncrementalDelightedStream):
    """
    API docs: https://app.delighted.com/docs/api/listing-people
    """

    def path(self, **kwargs) -> str:
        return "people.json"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Getting next page link
        next_page = response.links.get("next", None)
        if next_page:
            return {"page_info": dict(parse_qsl(urlparse(next_page.get("url")).query)).get("page_info")}


class Unsubscribes(IncrementalDelightedStream):
    """
    API docs: https://app.delighted.com/docs/api/listing-unsubscribed-people
    """

    cursor_field = "unsubscribed_at"
    primary_key = "person_id"

    def path(self, **kwargs) -> str:
        return "unsubscribes.json"


class Bounces(IncrementalDelightedStream):
    """
    API docs: https://app.delighted.com/docs/api/listing-bounced-people
    """

    cursor_field = "bounced_at"
    primary_key = "person_id"

    def path(self, **kwargs) -> str:
        return "bounces.json"


class SurveyResponses(IncrementalDelightedStream):
    """
    API docs: https://app.delighted.com/docs/api/listing-survey-responses
    """

    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "survey_responses.json"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)

        if "since" in params:
            params["updated_since"] = params.pop("since")

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
            stream = SurveyResponses(authenticator=auth, since=pendulum.parse(config["since"]))
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._get_authenticator(config)
        stream_kwargs = {"authenticator": auth, "since": pendulum.parse(config["since"])}
        return [
            Bounces(**stream_kwargs),
            People(**stream_kwargs),
            SurveyResponses(**stream_kwargs),
            Unsubscribes(**stream_kwargs),
        ]
