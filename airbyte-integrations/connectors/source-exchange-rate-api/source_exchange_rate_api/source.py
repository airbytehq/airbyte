#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream

from source_exchange_rate_api.authenticator import HTTPApiKeyHeaderAuth


class ExchangeRateApiStream(HttpStream, ABC):
    url_base = "https://api.apilayer.com/exchangerates_data/"

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        super(ExchangeRateApiStream, self).__init__(*args, **kwargs)
        self.config: Mapping[str, Any] = config

    @property
    @abstractmethod
    def primary_key(self) -> Union[str, List[str]]:
        pass

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"base": self.config["base"]}
        if "symbols" in self.config and self.config["symbols"]:
            params["symbols"] = self.config["symbols"]
        return params


class LatestRates(ExchangeRateApiStream):
    @property
    def primary_key(self) -> Union[str, List[str]]:
        return "timestamp"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "latest"


class IncrementalExchangeRateApiStream(ExchangeRateApiStream, IncrementalMixin, ABC):
    state_checkpoint_interval = None

    def __init__(self, *args, **kwargs):
        super(IncrementalExchangeRateApiStream, self).__init__(*args, **kwargs)
        self._cursor_value = None

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return super().cursor_field


class HistoricalRates(IncrementalExchangeRateApiStream):
    _date_format = "%Y-%m-%d"

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value or self._to_cursor_normalized_value(self.config["start_date"])}

    @state.setter
    def state(self, value: Mapping[str, Any]) -> None:
        self._cursor_value = self._to_cursor_normalized_value(value[self.cursor_field]) + datetime.timedelta(days=1)

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "date"

    @property
    def primary_key(self) -> Union[str, List[str]]:
        return "date"

    def _to_cursor_normalized_value(self, cursor_value: str) -> datetime.date:
        return datetime.datetime.strptime(cursor_value, self._date_format).date()

    def path(self, stream_state: Mapping[str, Any] = None,
             stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return stream_slice[self.cursor_field]

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            return []
        records = super(HistoricalRates, self).read_records(
            sync_mode,
            cursor_field=cursor_field,
            stream_slice=stream_slice,
            stream_state=stream_state
        )
        for record in records:
            next_cursor_value = self._to_cursor_normalized_value(record[self.cursor_field])
            self._cursor_value = max(self._cursor_value, next_cursor_value) if self._cursor_value else next_cursor_value
            yield record

    def _chunk_date_range(self, start_date: datetime.date) -> List[Mapping[str, Any]]:
        dates = []
        while start_date <= datetime.date.today():
            dates.append({self.cursor_field: start_date.strftime(self._date_format)})
            start_date += datetime.timedelta(days=1)
        return dates or [None]

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        return self._chunk_date_range(self.state[self.cursor_field])


class SourceExchangeRateApi(AbstractSource):
    @staticmethod
    def get_authenticator(config: Mapping[str, Any]) -> requests.auth.AuthBase:
        return HTTPApiKeyHeaderAuth(
            api_key_header='apikey',
            access_key=config["access_key"]
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = self.get_authenticator(config)
        stream = LatestRates(authenticator=auth, config=config)
        try:
            next(iter(stream.read_records(sync_mode=SyncMode.full_refresh)))
        except Exception as e:
            return False, str(e)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        _kwargs = {
            "authenticator": self.get_authenticator(config),
            "config": config
        }
        return [
            LatestRates(**_kwargs),
            HistoricalRates(**_kwargs),
        ]
