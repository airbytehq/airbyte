#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, NoAuth, HttpAuthenticator


def format_date(value, formatter='%Y-%m-%d'):
    if isinstance(value, str):
        return datetime.strptime(value, formatter)
    if isinstance(value, datetime):
        return value.strftime(formatter)


class APIKeyAuthenticator(HttpAuthenticator):
    def __init__(self, token, auth_header):
        self.auth_header = auth_header
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: self._token}


class ExchangeRates(HttpStream, IncrementalMixin):
    url_base = "http://api.exchangeratesapi.io/v1"

    cursor_field = "date"
    primary_key = "timestamp"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.base = config['base']
        self.access_key = config['access_key']
        self.start_date = format_date(config['start_date'])
        self._cursor_value = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination,
        # so we return None to indicate there are no more pages in the response
        return None

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return stream_slice['date']

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include access_key as a query param so we do that in this method
        return {'access_key': self.access_key, 'base': self.base}

    def parse_response(
            self,
            response: requests.Response,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # The response is a simple JSON whose schema matches our stream's schema exactly,
        # so we just return a list containing the response
        return [response.json()]

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            if self._cursor_value:
                latest_record_date = format_date(record[self.cursor_field])
                self._cursor_value = max(self._cursor_value, latest_record_date)
            yield record

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, Any]]:
        """
        Returns a list of each day between the start date and now.
        The return value is a list of dicts {'date': date_string}.
        """
        dates = []
        while start_date < datetime.now() and format_date(start_date) != format_date(datetime.now()):
            dates.append({self.cursor_field: format_date(start_date)})
            start_date += timedelta(days=1)
        return dates

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = format_date(stream_state[self.cursor_field]) if stream_state and self.cursor_field in stream_state else self.start_date
        return self._chunk_date_range(start_date)

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: format_date(self._cursor_value)}
        else:
            return {self.cursor_field: format_date(self.start_date)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = format_date(value[self.cursor_field])


# Source
class SourcePythonHttpExample(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = APIKeyAuthenticator(token=config['access_key'], auth_header="apikey")
            stream = ExchangeRates(authenticator=auth, config=config)
            records = stream.read_records(sync_mode=SyncMode.incremental)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}")

        auth = APIKeyAuthenticator(token=config['access_key'], auth_header="apikey")
        return [ExchangeRates(authenticator=auth, config=config)]
