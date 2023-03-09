from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class GiftupStream(HttpStream, ABC):
    url_base = "https://api.giftup.app/"

    def __init__(self, config: Mapping[str, Any], data_key: str = None):
        super().__init__()

        self.apikey = config.get("apikey")
        self.start_date = config.get("start_date")
        self.batch_size = 100
        self.offset = 0
        self.data_key = data_key

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"authorization": f"Bearer {self.apikey}"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        if type(data) == list:
            return None

        if data.get("hasMore", False):
            self.offset += self.batch_size
            return {"offset": self.offset}

        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        return {"createdOnOrAfter": self.start_date, "limit": self.batch_size, "offset": self.offset}

    def request_kwargs(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        return {"verify": False}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        if type(data) == list:
            yield from data
        else:
            yield from data.get(self.data_key, [])


class IncrementalGiftupStream(GiftupStream, ABC):
    state_checkpoint_interval = 1

    @property
    def cursor_field(self) -> str:
        return "offset"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        self.offset = max(current_stream_state.get(self.cursor_field, 0), self.offset)
        return {"offset": self.offset}


class GiftCards(IncrementalGiftupStream):
    primary_key = "orderId"

    cursor_field = "offset"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "gift-cards"


class Items(IncrementalGiftupStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "items"


class SourceGiftup(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [GiftCards(config=config, data_key="giftCards"), Items(config=config)]
