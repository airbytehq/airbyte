#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from base64 import b64encode
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

DEFAULT_CURSOR = "modified_at"


# Basic full refresh stream
class DclLogisticsStream(HttpStream, ABC):
    url_base = "https://api.dclcorp.com/api/v1/"

    def __init__(self, **args):
        super(DclLogisticsStream, self).__init__(**args)

        self.next_page = 1
        self.has_more_pages = True

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Returns the next page from DCL

        :return: The token for the next page from the input response object. Returning `None` means there are no more pages.
        """
        if self.has_more_pages:
            self.next_page += 1
            return {"page": self.next_page}
        else:
            return None


# Basic incremental stream
class IncrementalDclLogisticsStream(DclLogisticsStream, ABC):
    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return DEFAULT_CURSOR

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_updated_at = (current_stream_state or {}).get(self.cursor_field, "")
        latest_record_updated_at = latest_record[self.cursor_field]

        return {self.cursor_field: max(latest_record_updated_at, current_updated_at)}


class Orders(IncrementalDclLogisticsStream):
    primary_key = ["order_number", "account_number"]

    def __init__(self, modified_from: str = None, modified_to: str = None, **args):
        super(Orders, self).__init__(**args)

        self.modified_from = modified_from
        self.modified_to = modified_to

    def path(self, **kwargs) -> str:
        return "orders"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        page = next_page_token.get("page", 1) if next_page_token else 1

        params = {"page": page, "page_size": 100, "extended_date": True}

        self.modified_from = (stream_state and stream_state[self.cursor_field]) or self.modified_from

        if self.modified_from:
            params.update({"modified_from": self.modified_from})

        if self.modified_to:
            params.update({"modified_to": self.modified_to})

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        orders = response.json().get("orders")
        if orders:
            for order in orders:
                yield order
        else:
            self.has_more_pages = False


# Source
class SourceDclLogistics(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            orders = Orders(authenticator=self.token(config=config))

            test_url = f"{orders.url_base}{orders.path()}"
            response = requests.request("GET", url=test_url, headers=orders.authenticator.get_auth_header())

            if response.ok:
                return True, None
            else:
                response.raise_for_status()
        except Exception as exception:
            return False, exception

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        modified_from = config.get("modified_from")
        modified_to = config.get("modified_to")
        return [Orders(authenticator=self.token(config=config), modified_from=modified_from, modified_to=modified_to)]

    @staticmethod
    def token(config: Mapping[str, Any]) -> TokenAuthenticator:
        """
        Returns the Basic Authentication Base64 encoded token

        :param config: the user-input config object conforming to the connector's spec.json

        :return TokenAuthenticator: The TokenAuthenticator
        """
        token = b64encode(f"{config['username']}:{config['password']}".encode()).decode()
        return TokenAuthenticator(token=token, auth_method="Basic")
