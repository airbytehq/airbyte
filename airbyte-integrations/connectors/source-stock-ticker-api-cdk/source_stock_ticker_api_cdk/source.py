#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime
from datetime import date, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth


# Basic full refresh stream
class Prices(HttpStream, IncrementalMixin):
    url_base = 'https://api.polygon.io/v2/aggs/'
    primary_key = None
    state_checkpoint_interval = 3
    cursor_field = 'date'

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config['api_key']
        self.stock_ticker = config['stock_ticker']
        self.stock_prices_date = datetime.datetime.now() - timedelta(days=self.state_checkpoint_interval)
        self._cursor_value = None

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime('%Y-%m-%d')}
        else:
            return {self.cursor_field: self.stock_prices_date.strftime('%Y-%m-%d')}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.datetime.strptime(value[self.cursor_field], '%Y-%m-%d')

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            'sort': 'asc',
            'limit': 120,
            'apiKey': self.api_key
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        results = []
        if 'results' in response.json():
            results = response.json()['results']

        for result in results:
            yield {
                'date': date.fromtimestamp(result['t'] / 1000).isoformat(),
                'stock_ticker': self.stock_ticker,
                'price': result['c']
            }

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            yield record

            if self._cursor_value:
                latest_record_date = datetime.datetime.strptime(record[self.cursor_field], '%Y-%m-%d')
                self._cursor_value = max(self._cursor_value, latest_record_date)
            else:
                self._cursor_value = datetime.datetime.strptime(record[self.cursor_field], '%Y-%m-%d')

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, any]]:
        """
        Returns a list of each day between the start date and now.
        The return value is a list of dicts {'date': date_string}.
        """
        dates = []
        while start_date < datetime.datetime.now():
            dates.append({'date': start_date.strftime('%Y-%m-%d')})
            start_date += timedelta(days=1)
        return dates

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[
        Optional[Mapping[str, any]]]:
        start_date = datetime.datetime.strptime(stream_state['date'],
                                                '%Y-%m-%d') if stream_state and 'date' in stream_state else self.stock_prices_date
        return self._chunk_date_range(start_date)

    def path(self, **kwargs) -> str:
        day = kwargs['stream_slice']['date']

        return f'ticker/{self.stock_ticker}/range/1/day/{day}/{day}'


# Source
class SourceStockTickerApiCdk(AbstractSource):

    def _call_api(self, ticker, token):
        today = date.today()
        to_day = today.strftime('%Y-%m-%d')
        from_day = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        return requests.get(
            f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{from_day}/{to_day}?sort=asc&limit=120&apiKey={token}')

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        response = self._call_api(ticker=config['stock_ticker'], token=config['api_key'])

        if response.status_code == 200:
            result = {'status': 'SUCCEEDED'}
            return True, result
        elif response.status_code == 403:
            result = {'status': 'FAILED', 'message': 'API Key is incorrect.'}
            return False, result
        else:
            result = {'status': 'FAILED', 'message': 'Input configuration is incorrect. Please verify the input stock ticker and API key.'}
            return False, result

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        return [Prices(authenticator=auth, config=config)]
