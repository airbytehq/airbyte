#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import BasicHttpAuthenticator


# Basic full refresh stream
class KlarnaStream(HttpStream, ABC):
    def __init__(self, region: str, playground: bool, authenticator: BasicHttpAuthenticator, **kwargs):
        self.region = region
        self.playground = playground
        self.kwargs = kwargs
        super().__init__(authenticator=authenticator)

    page_size = 500
    data_api_field: str

    @property
    def url_base(self) -> str:
        playground_path = "playground." if self.playground else ""
        if self.region == "eu":
            endpoint = f"https://api.{playground_path}klarna.com/"
        else:
            endpoint = f"https://api-{self.region}.{playground_path}klarna.com/"
        return endpoint

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        if "next" in response_json.get("pagination", {}).keys():
            parsed_url = urlparse(response_json["pagination"]["next"])
            query_params = parse_qs(parsed_url.query)
            # noinspection PyTypeChecker
            return query_params
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return dict(next_page_token)
        else:
            return {"offset": 0, "size": self.page_size}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        payouts = response.json().get(self.data_api_field, [])
        yield from payouts


class Payouts(KlarnaStream):
    """
    Payouts read from Klarna Settlements API https://developers.klarna.com/api/?json#settlements-api
    """

    primary_key = "payout_date"  # TODO verify
    data_api_field = "payouts"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/settlements/v1/payouts"


class Transactions(KlarnaStream):
    """
    Transactions read from Klarna Settlements API https://developers.klarna.com/api/?json#settlements-api
    """

    primary_key = "capture_id"  # TODO verify
    data_api_field = "transactions"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/settlements/v1/transactions"


# Source
class SourceKlarna(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            auth = BasicHttpAuthenticator(username=config["username"], password=config["password"])
            conn_test_stream = Transactions(authenticator=auth, **config)
            conn_test_stream.page_size = 1
            conn_test_stream.next_page_token = lambda x: None
            records = conn_test_stream.read_records(sync_mode=SyncMode.full_refresh)
            # Try to read one value from records iterator
            next(records, None)
            return True, None
        except Exception as e:
            print(e)
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = BasicHttpAuthenticator(username=config["username"], password=config["password"])
        return [Payouts(authenticator=auth, **config), Transactions(authenticator=auth, **config)]
