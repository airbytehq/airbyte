#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import datetime
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Basic full refresh stream
class StockTickerApiV2Stream(HttpStream, ABC):
    url_base = "https://api.polygon.io/v2/aggs/"

    data_field = "results"

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update({'sort': 'asc', 'limit': 120, })
        return params


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if self.data_field in response_json:
            yield from response_json[self.data_field]

        yield from []


# Basic incremental stream
class IncrementalStockTickerApiV2Stream(StockTickerApiV2Stream, ABC):
    state_checkpoint_interval = None


class Ticker(IncrementalStockTickerApiV2Stream, IncrementalMixin):
    cursor_field = "date"
    primary_key = "date"

    def __init__(self, stock_ticker: str, start_date: datetime, **kwargs):
        self.stock_ticker = stock_ticker
        super().__init__(**kwargs)
        self.start_date = start_date
        self._cursor: Optional[datetime.date] = None

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor is not None:
            cursor = self._cursor.strftime('%Y-%m-%d')
        else:
            cursor = self.start_date.strftime('%Y-%m-%d')
        return {
            self.cursor_field: cursor,
        }

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor = datetime.datetime.strptime(value[self.cursor_field], '%Y-%m-%d').date()

    def next_page_token(self, *args, **kwargs):
        return None


    def path(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
             next_page_token: Mapping[str, Any] = None) -> str:

        # By default we fetch stock prices for the 7 day period ending with today
        today = datetime.date.today()
        to_day = today.strftime("%Y-%m-%d")
        from_day = stream_slice[self.cursor_field] if stream_slice else self.state[self.cursor_field]

        link = f"ticker/{self.stock_ticker}/range/1/day/{from_day}/{to_day}"
        return link

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for result in super().parse_response(response, **kwargs):
            record = {"date": datetime.datetime.fromtimestamp(result["t"] / 1000, tz=datetime.timezone.utc).strftime("%Y-%m-%d"),
                      "stock_ticker": self.stock_ticker, "price": result["c"]}
            yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
            Mapping[str, Any]:
        try:
            latest_state = latest_record.get(self.cursor_field)
            current_stream_state = current_stream_state or {}
            current_state = current_stream_state.get(self.cursor_field) or latest_state

            if current_state:
                return {self.cursor_field: max(latest_state, current_state)}
            return {}
        except TypeError as e:
            raise TypeError(
                f"Expected {self.cursor_field} {current_stream_state=} {latest_record=}"
            ) from e

    def read_records(self, sync_mode, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        fallback = self.start_date
        for record in super().read_records(sync_mode, *args, **kwargs):
            record_stamp = datetime.datetime.strptime(record[self.cursor_field], "%Y-%m-%d")
            self._cursor = max(record_stamp.date(), self._cursor or fallback)
            yield record


# Source
class SourceStockTickerApiV2(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        if not config.get("api_key"):
            return False, f"Missing required config fields `api_key`."
        if not config.get("stock_ticker"):
            return False, f"Missing required config fields `stock_ticker`."
        alowed_ticker = {"AAPL", "TSLA", "AMZN"}
        if config.get("stock_ticker") not in alowed_ticker:
            return False, f"Stock ticker might be one of {alowed_ticker}."
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = TokenAuthenticator(config.get('api_key'))
        today = datetime.date.today()
        from_day = (today - datetime.timedelta(days=7))
        stock_ticker = config['stock_ticker']
        return [Ticker(authenticator=auth, stock_ticker=stock_ticker, start_date=from_day), ]
