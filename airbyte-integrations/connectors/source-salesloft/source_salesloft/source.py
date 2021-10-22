#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.auth.oauth import Oauth2Authenticator


# Basic full refresh stream
class SalesloftStream(HttpStream, ABC):

    url_base = "https://api.salesloft.com/v2/"

    def __init__(
        self,
        authenticator: HttpAuthenticator,
        start_date: str = None,
        **kwargs,
    ):
        self.start_date = start_date
        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            next_page = response.json()["metadata"]["paging"].get("next_page")
            return None if not next_page else {"page": next_page}
        except Exception as e:
            raise KeyError(f"error parsing next_page token: {e}")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"per_page": 100, "page": 1}
        if next_page_token and "page" in next_page_token:
            params["page"] = next_page_token["page"]
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("data")
        if not data:
            return
        for element in data:
            yield element


# Basic incremental stream
class IncrementalSalesloftStream(SalesloftStream, ABC):
    @property
    def cursor_field(self) -> str:
        return "updated_at"

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
            params["updated_at[gte]"] = stream_state[self.cursor_field]
        return params


class Users(SalesloftStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "users"


class People(IncrementalSalesloftStream):
    primary_key = "id"
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "people"


class Cadences(IncrementalSalesloftStream):
    primary_key = "id"
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "cadences"


class CadenceMemberships(IncrementalSalesloftStream):
    primary_key = "id"
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "cadence_memberships"


# Source
class SourceSalesloft(AbstractSource):
    def _create_authenticator(self, config):
        return Oauth2Authenticator(
            token_refresh_endpoint="https://accounts.salesloft.com/oauth/token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            access_token, _ = self._create_authenticator(config).refresh_access_token()
            response = requests.get("https://api.salesloft.com/v2/me.json", headers={"Authorization": f"Bearer {access_token}"})
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._create_authenticator(config)
        return [
            Cadences(authenticator=auth, **config),
            CadenceMemberships(authenticator=auth, **config),
            People(authenticator=auth, **config),
            Users(authenticator=auth, **config),
        ]
