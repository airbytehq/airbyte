#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import SingleUseRefreshTokenOauth2Authenticator

# Basic full refresh stream
class AmocrmStream(HttpStream, ABC):
    url_base = "https://hexlet.amocrm.ru/api/v4/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if response.status_code == 204:
            return {}

        return {
            'page': response.json()['_page'] + 1
        }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            'limit': 250,
            'with': 'contacts,loss_reason'
        }

        if next_page_token:
            params.update(**next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 204:
            return []

        data = response.json().get("_embedded").get(self.name)

        yield from data

class Leads(AmocrmStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "leads"

# Source
class SourceAmocrm(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # Check connectivity
            auth = SingleUseRefreshTokenOauth2Authenticator(
                config,
                token_refresh_endpoint="https://hexlet.amocrm.ru/oauth2/access_token",
            )
            leads_stream = Leads(
                authenticator=auth
            )

            next(leads_stream.read_records(sync_mode=SyncMode.full_refresh))

            return True, None
        except Exception as error:
            return False, error

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = SingleUseRefreshTokenOauth2Authenticator(
            config,
            token_refresh_endpoint="https://hexlet.amocrm.ru/oauth2/access_token",
        )
        return [
            Leads(authenticator=auth)
        ]
