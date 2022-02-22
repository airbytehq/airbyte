#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Full refresh stream
class Price(HttpStream, ABC):


    url_base = "https://query1.finance.yahoo.com/"
    primary_key = None

    def __init__(self, ticker: str, interval: str, **kwargs):
        super().__init__(**kwargs)
        self.ticker = ticker
        self.interval = interval

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v8/finance/chart/{self.ticker}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # YF does not offer pagination
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "symbol": self.ticker,
            "interval": self.interval
        }

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        base_headers = super().request_headers(**kwargs)
        headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
        return {**base_headers, **headers}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        return [response.json()]

# Basic incremental stream
class IncrementalPriceStream(Price, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
        if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


# Source
class SourceYahooFinance(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        # No parameter validation required (?)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Price(ticker=config['ticker'], interval=config.get('interval', '1m'))]
