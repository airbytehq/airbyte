#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime, timedelta
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth


class StockTickerAPIUrlManager:
    url: str = None

    def __init__(self, config: dict):
        self.api_key: str = config["api_key"]
        self.ticker: str = config["stock_ticker"]
        self.from_date: str = config["from_date"]
        self.to_date: str = config["to_date"]

        self.schema: str = "https"
        self.domain: str = "api.polygon.io"
        self.api_path: str = "v2/aggs/ticker/"
        self.api_url: str = f"{self.schema}://{self.domain}/{self.api_path}"
        self.base_url: str = "{ticker}/range/1/day/{from_day}/{to_day}?" "sort=asc&limit=120&apiKey={api_key}"
        self.query_url: str = ""

        self.url_construct(ticker=self.ticker, api_key=self.api_key)

    def url_construct(self, ticker: str = "", api_key: str = "", from_day: str = None, to_day: str = None) -> str:
        from_day = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d") if not from_day else from_day
        to_day = date.today().strftime("%Y-%m-%d") if not to_day else to_day
        self.query_url = self.base_url.format(ticker=ticker, api_key=api_key, from_day=from_day, to_day=to_day)
        return self.query_url

    def query(self) -> requests.Response:
        return requests.get(f"{self.api_url}{self.query_url}")


class SourceStockTickerAPI(AbstractSource):
    def __init__(self):
        super(SourceStockTickerAPI, self).__init__()
        self.url_manager = None
        self.stream = None

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        self.url_manager = StockTickerAPIUrlManager(config)
        try:

            response = self.url_manager.query()
            if response.status_code == 200:
                return True, None
            elif response.status_code == 403:
                return False, {
                    "status": "FAILED", "message": "API Key is incorrect."
                }
            else:
                return False, {
                    "status": "FAILED",
                    "message": "Input configuration is incorrect. " "Please verify the input stock ticker and API key.",
                }
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()

        from_date: datetime = datetime.strptime(config["from_date"], "%Y-%m-%d")
        to_date: datetime = datetime.strptime(config["to_date"], "%Y-%m-%d")

        return [
            StockPrices(
                authenticator=auth,
                config=config,
                from_date=from_date,
                to_date=to_date
            )
        ]


class StockPrices(HttpStream, IncrementalMixin):
    url_base: str = ""
    primary_key = "date"

    def __init__(self, authenticator, config, from_date: datetime = None, to_date: datetime = None):
        super().__init__(authenticator)

        self.config = config
        self.from_date = from_date if "from_date" not in config else config["from_date"]
        self.to_date = to_date if "to_date" not in config else config["to_date"]

        self._cursor_value = None

        self.url_manager = StockTickerAPIUrlManager(config)
        self.url_manager.url_construct(ticker=config["stock_ticker"], api_key=config["api_key"], from_day=from_date, to_day=to_date)
        self.url_base = self.url_manager.api_url

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime("%Y-%m-%d")}
        else:
            return {self.cursor_field: self.from_date.strftime("%Y-%m-%d")}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], "%Y-%m-%d")

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            if self._cursor_value:
                latest_record_date = datetime.strptime(record[self.cursor_field], "%Y-%m-%d")
                self._cursor_value = max(self._cursor_value, latest_record_date)
            yield record

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        t_url = self.url_manager.url_construct(
            ticker=self.url_manager.ticker,
            api_key=self.url_manager.api_key,
            from_day=self.url_manager.from_date,
            to_day=self.url_manager.to_date,
        )

        return t_url

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        return [response.json()]
