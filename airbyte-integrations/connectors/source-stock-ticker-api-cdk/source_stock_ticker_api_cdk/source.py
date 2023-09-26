#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, date, timezone
from http import HTTPStatus
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth

DATE_FORMAT = "%Y-%m-%d"


class StockPrices(HttpStream, IncrementalMixin):
    url_base = "https://api.polygon.io/v2/"
    primary_key = "date"
    cursor_field = "date"

    def __init__(self, config: Mapping[str, Any], **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_key: str = config["api_key"]
        self.stock_ticker: str = config["stock_ticker"]
        self.start_date: str = config["start_date"]
        self.end_date: str = config["end_date"]
        self.multiplier: int = config["multiplier"]
        self.timespan: str = config["timespan"]
        self._raise_on_http_errors: bool = True
        self._cursor_value: Optional[str] = None

    @property
    def raise_on_http_errors(self) -> bool:
        return self._raise_on_http_errors

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"aggs/ticker/{self.stock_ticker}/range/{self.multiplier}/{self.timespan}/{stream_slice['date']}/{self.end_date}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"sort": "asc", "apiKey": self.api_key}

    def parse_response(self, response: requests.Response, **kwargs: Mapping[str, Any]) -> Iterable[Mapping]:
        content = response.json() or {}
        if content and content.get("resultsCount", 0) > 0:
            for result in content["results"]:
                record = {
                    "date": datetime.fromtimestamp(result["t"]/1000, tz=timezone.utc).strftime(DATE_FORMAT),
                    "stock_ticker": content["ticker"],
                    "price": result["c"],
                }
                self.state = record
                yield record

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value if self._cursor_value else self.start_date}

    @state.setter
    def state(self, value: Mapping[str, Any]) -> None:
        if not self._cursor_value:
            self._cursor_value = value.get(self.cursor_field)
        else:
            latest_record_date = value[self.cursor_field]
            current_value = value.get(self.cursor_field) or self.start_date
            self._cursor_value = max(current_value, latest_record_date)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        # In basic subscription, only 5 requests per minute allowed
        return 61

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, Any]]:
        """
        Returns a list of each day between the start date and end date.
        The return value is a list of dicts {'date': date_string}.
        """
        dates = []
        while start_date <= datetime.strptime(self.end_date, DATE_FORMAT):
            dates.append({self.cursor_field: start_date.strftime(DATE_FORMAT)})
            start_date += timedelta(days=1)
        return dates

    def stream_slices(
        self, sync_mode: str, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if stream_state and self.cursor_field in stream_state:
            start_date = datetime.strptime(stream_state[self.cursor_field], DATE_FORMAT)
        else:
            start_date = datetime.strptime(self.start_date, DATE_FORMAT)
        return self._chunk_date_range(start_date)

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code in (HTTPStatus.FORBIDDEN, HTTPStatus.UNPROCESSABLE_ENTITY):
            self.logger.error(f"Stream {self.name}: permission denied or entity is unprocessable. Skipping.")
            self._raise_on_http_errors = False
            return False
        return super().should_retry(response)


class SourceStockTickerApiCDK(AbstractSource):
    def check_connection(self, logger: Any, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        response = self._call_api(
            ticker=config["stock_ticker"],
            token=config["api_key"],
            from_day=datetime.now().date() - timedelta(days=1),
            to_day=datetime.now().date(),
        )

        if response.status_code == HTTPStatus.OK:
            return True, None

        return False, "Input configuration is incorrect. Please verify the input stock ticker and API key."

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        return [StockPrices(config=config, authenticator=auth)]

    @staticmethod
    def _call_api(ticker: str, token: str, from_day: Union[str, date], to_day: Union[str, date]) -> requests.Response:
        return requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{from_day}/{to_day}?sort=asc&limit=1&apiKey={token}"
        )
