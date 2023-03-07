#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class YouniumStream(HttpStream, ABC):
    # url_base = "https://apisandbox.younium.com"

    # https://api.younium.com
    def __init__(self, authenticator=TokenAuthenticator, playground: bool = False, *args, **kwargs):
        super().__init__(authenticator=authenticator)
        self.page_size = 100
        self.playground: bool = playground

    @property
    def url_base(self) -> str:
        if self.playground:
            endpoint = "https://apisandbox.younium.com"
        else:
            endpoint = "https://api.younium.com"
        return endpoint

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response = response.json()
        current_page = response.get("pageNumber", 1)
        total_rows = response.get("totalCount", 0)

        total_pages = total_rows // self.page_size

        if current_page <= total_pages:
            return {"pageNumber": current_page + 1}
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return {"pageNumber": next_page_token["pageNumber"], "PageSize": self.page_size}
        else:
            return {"PageSize": self.page_size}

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        response_results = response.json()
        yield from response_results.get("data", [])


class Invoice(YouniumStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Invoices"


class Product(YouniumStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Products"


class Subscription(YouniumStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Subscriptions"


class SourceYounium(AbstractSource):
    def get_auth(self, config):
        scope = "openid youniumapi profile"

        if config.get("playground"):
            url = "https://younium-identity-server-sandbox.azurewebsites.net/connect/token"
        else:
            url = "https://younium-identity-server.azurewebsites.net/connect/token"

        payload = f"grant_type=password&client_id=apiclient&username={config['username']}&password={config['password']}&scope={scope}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        access_token = response.json()["access_token"]

        auth = TokenAuthenticator(token=access_token)
        return auth

    def check_connection(self, logger, config) -> Tuple[bool, any]:

        try:
            stream = Invoice(authenticator=self.get_auth(config), **config)
            stream.next_page_token = lambda response: None
            stream.page_size = 1
            # auth = self.get_auth(config)
            _ = list(stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            logger.error(e)
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = self.get_auth(config)
        return [Invoice(authenticator=auth, **config), Product(authenticator=auth, **config), Subscription(authenticator=auth, **config)]
