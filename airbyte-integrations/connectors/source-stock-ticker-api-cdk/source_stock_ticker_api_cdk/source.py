#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from requests import Response

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

    def next_page_token(self, response: Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_state = stream_state or {}
        start_date = stream_state.get(self.cursor_field, self.start_date)
        return f"aggs/ticker/{self.stock_ticker}/range/{self.multiplier}/{self.timespan}/{start_date}/{self.end_date}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"sort": "asc", "apiKey": self.api_key}

    def parse_response(self, response: Response, **kwargs: Mapping[str, Any]) -> Iterable[Mapping]:
        content = response.json() or {}
        if content and content.get("resultsCount", 0) > 0:
            for result in content["results"]:
                record = {
                    "date": datetime.fromtimestamp(result["t"] / 1000, tz=timezone.utc).strftime(DATE_FORMAT),
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

    def backoff_time(self, response: Response) -> Optional[float]:
        # In basic subscription, only 5 requests per minute allowed
        return 61

    def should_retry(self, response: Response) -> bool:
        if response.status_code in (HTTPStatus.FORBIDDEN, HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST):
            self.logger.error(f"Stream {self.name}: permission denied or entity is unprocessable. Skipping.")
            self._raise_on_http_errors = False
            return False
        return super().should_retry(response)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            self.cursor_field: max(
                current_stream_state.get(self.cursor_field, self.start_date),
                latest_record.get(self.cursor_field, self.start_date),
            )
        }


class SourceStockTickerApiCDK(AbstractSource):
    def check_connection(self, logger: Any, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            stream = StockPrices(config=config)
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        return [StockPrices(config=config, authenticator=auth)]
