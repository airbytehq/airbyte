#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import parse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.auth.oauth import Oauth2Authenticator


# Basic full refresh stream
class OutreachStream(HttpStream, ABC):

    url_base = "https://api.outreach.io/api/v2"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            params = parse.parse_qs(parse.urlparse(response.authentication_url).query)
            if not params or 'page[after]' not in params:
                return {}
            return {"after": params['page[after]'][0]}
        except Exception as e:
            raise KeyError(f"error parsing next_page token: {e}")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"page[size]": 1, "count": False}
        if next_page_token and "after" in next_page_token:
            params["page[after]"] = next_page_token["after"]
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("data")
        if not data:
            return
        for element in data:
            yield element


# Basic incremental stream
class IncrementalOutreachStream(OutreachStream, ABC):
    @property
    def cursor_field(self) -> str:
        return "updatedAt"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}

        current_stream_state_date = current_stream_state.get(self.cursor_field, self.start_date)
        latest_record_date = latest_record.get('attributes', {}).get(self.cursor_field, self.start_date)

        return {self.cursor_field: max(current_stream_state_date, latest_record_date)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if self.cursor_field in stream_state:
            params["filter[updatedAt]"] = stream_state[self.cursor_field] + '..inf'
        return params


class Prospects(IncrementalOutreachStream):
    primary_key = "id"
    cursor_field = "updatedAt"

    def path(self, **kwargs) -> str:
        return "prospects"


class Sequences(IncrementalOutreachStream):
    primary_key = "id"
    cursor_field = "updatedAt"

    def path(self, **kwargs) -> str:
        return "sequences"


class SequenceStates(IncrementalOutreachStream):
    primary_key = "id"
    cursor_field = "updatedAt"

    def path(self, **kwargs) -> str:
        return "sequenceStates"


class OutreachAuthenticator(Oauth2Authenticator):
    def __init__(self, redirect_uri: str, *args, **kwargs):
        super(Oauth2Authenticator, self).__init__(*args, **kwargs)
        self.redirect_uri = redirect_uri

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload = super().get_refresh_request_body()
        payload['redirect_uri'] = self.redirect_uri
        return payload


# Source
class SourceOutreach(AbstractSource):
    def _create_authenticator(self, config):
        return OutreachAuthenticator(
            redirect_uri=config["redirect_uri"],
            token_refresh_endpoint="https://api.outreach.io/oauth/token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            access_token, _ = self._create_authenticator(config).refresh_access_token()
            response = requests.get("https://api.outreach.io/api/v2", headers={"Authorization": f"Bearer {access_token}"})
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._create_authenticator(config)
        return [
            Prospects(authenticator=auth, **config),
            Sequences(authenticator=auth, **config),
            SequenceStates(authenticator=auth, **config),
        ]
