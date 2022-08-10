#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Full refresh stream
class Price(HttpStream, ABC):
    """
    Queries the Yahoo Finance API for the price history of the given stock.
    The length of the price history is determined by the interval parameter:
    - 1m to 90m: up to 7 days of data
    - 1h to 3mo: up to 730 days of data

    Based on the documentation found at https://stackoverflow.com/questions/44030983/yahoo-finance-url-not-working.
    """

    url_base = "https://query1.finance.yahoo.com/"
    primary_key = None

    def __init__(self, tickers: str, interval: str, range: str, **kwargs):
        super().__init__(**kwargs)
        self.tickers = tickers
        self.next_index = 0
        self.interval = interval
        self.range = range

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        next_index = next_page_token or 0  # At the first request next_page_token is None
        return f"v8/finance/chart/{self.tickers[next_index]}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        We re-use pagination functionality to get one ticker history at a time.
        Updates the next_index counter to the next ticker in the list.
        """
        self.next_index += 1
        if self.next_index >= len(self.tickers):
            return None
        return self.next_index

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        next_index = next_page_token or 0  # At the first request next_page_token is None
        return {
            "symbol": self.tickers[next_index],
            "interval": self.interval,
            "range": self.range,
        }

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        base_headers = super().request_headers(**kwargs)
        headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}  # Required to avoid 403 response
        return {**base_headers, **headers}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code != 200:
            return []
        yield from [response.json()]


# Source
class SourceYahooFinancePrice(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        # Check that the tickers are valid
        tickers = list(map(str.strip, config["tickers"].split(",")))
        if len(tickers) == 0:
            return False, "No valid tickers provided"
        for ticker in tickers:
            # Check that yahoo finance has the ticker
            response = requests.get(
                url=f"https://query1.finance.yahoo.com/v6/finance/autocomplete?query={ticker}&lang=en",
                headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},  # Required to avoid 403 response
            )
            if response.status_code != 200:
                return False, f"Ticker {ticker} not found"
            response_json = response.json()
            if "ResultSet" not in response_json:
                return False, f"Invalid check response format for ticker {ticker}"
            if "Result" not in response_json["ResultSet"]:
                return False, f"Invalid check response format for ticker {ticker}"
            if len(response_json["ResultSet"]["Result"]) == 0:
                return False, f"Ticker {ticker} not found"

        # Check that the range parameter is configured according to the interval parameter
        # If the range DOES NOT end in "d" we cannot use minute intervals (end in "m")
        if "interval" in config and "range" in config:
            if config["interval"][-1] == "m" and config["range"][-1] != "d":
                return False, "Range parameter must end in 'd' for minute intervals"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = {
            # Split tickers by comma and strip whitespaces
            "tickers": list(map(str.strip, config["tickers"].split(","))),
            "interval": config.get("interval", "7d"),
            "range": config.get("range", "1m"),
        }
        return [Price(**args)]
