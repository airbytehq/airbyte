#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

_TOKEN_REFRESH_ENDPOINT = "https://api.outreach.io/oauth/token"
_URL_BASE = "https://api.outreach.io/api/v2/"


# Basic full refresh stream
class OutreachStream(HttpStream, ABC):

    url_base = _URL_BASE
    primary_key = "id"

    def __init__(
        self,
        authenticator: HttpAuthenticator,
        start_date: str = None,
        **kwargs,
    ):
        self.start_date = start_date
        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Returns the token for the next page as per https://api.outreach.io/api/v2/docs#pagination.
        It uses cursor-based pagination, by sending the 'page[size]' and 'page[after]' parameters.
        """
        try:
            next_page_url = response.json().get("links").get("next")
            params = parse.parse_qs(parse.urlparse(next_page_url).query)
            if not params or "page[after]" not in params:
                return {}
            return {"after": params["page[after]"][0]}
        except Exception as e:
            raise KeyError(f"error parsing next_page token: {e}")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"page[size]": 100, "count": "false"}
        if next_page_token and "after" in next_page_token:
            params["page[after]"] = next_page_token["after"]
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("data")
        if not data:
            return
        for element in data:
            yield {**element.get("attributes"), **{self.primary_key: element[self.primary_key]}}


# Basic incremental stream
class IncrementalOutreachStream(OutreachStream, ABC):
    @property
    def cursor_field(self) -> str:
        return "updatedAt"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}

        current_stream_state_date = current_stream_state.get(self.cursor_field, self.start_date)
        latest_record_date = latest_record.get(self.cursor_field, self.start_date)

        return {self.cursor_field: max(current_stream_state_date, latest_record_date)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if self.cursor_field in stream_state:
            params[f"filter[{self.cursor_field}]"] = stream_state[self.cursor_field] + "..inf"
        return params


class Prospects(IncrementalOutreachStream):
    """
    Prospect stream. Yields data from the GET /prospects endpoint.
    See https://api.outreach.io/api/v2/docs#prospect
    """

    def path(self, **kwargs) -> str:
        return "prospects"


class Sequences(IncrementalOutreachStream):
    """
    Sequence stream. Yields data from the GET /sequences endpoint.
    See https://api.outreach.io/api/v2/docs#sequence
    """

    def path(self, **kwargs) -> str:
        return "sequences"


class SequenceStates(IncrementalOutreachStream):
    """
    Sequence stream. Yields data from the GET /sequences endpoint.
    See https://api.outreach.io/api/v2/docs#sequenceState
    """

    def path(self, **kwargs) -> str:
        return "sequenceStates"


class OutreachAuthenticator(Oauth2Authenticator):
    def __init__(self, redirect_uri: str, token_refresh_endpoint: str, client_id: str, client_secret: str, refresh_token: str):
        super().__init__(
            token_refresh_endpoint=token_refresh_endpoint, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
        )
        self.redirect_uri = redirect_uri

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload = super().get_refresh_request_body()
        payload["redirect_uri"] = self.redirect_uri
        return payload


# Source
class SourceOutreach(AbstractSource):
    def _create_authenticator(self, config):
        return OutreachAuthenticator(
            redirect_uri=config["redirect_uri"],
            token_refresh_endpoint=_TOKEN_REFRESH_ENDPOINT,
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            access_token, _ = self._create_authenticator(config).refresh_access_token()
            response = requests.get(_URL_BASE, headers={"Authorization": f"Bearer {access_token}"})
            response.raise_for_status()
            return True, None
        except Exception as e:
            logger.error(f"Failed to check connection. Error: {e}")
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._create_authenticator(config)
        return [
            Prospects(authenticator=auth, **config),
            Sequences(authenticator=auth, **config),
            SequenceStates(authenticator=auth, **config),
        ]
