#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth


# Basic full refresh stream
class ExchangeRatesTutorialStream(HttpStream, ABC):
    url_base = "http://api.exchangeratesapi.io/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return [response.json()]


# Basic incremental stream
class IncrementalExchangeRatesTutorialStream(ExchangeRatesTutorialStream, ABC):
    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def _cursor_value(self) -> None:
        return None

    @property
    def cursor_field(self) -> str:
        return "date"

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime("%Y-%m-%d")}
        else:
            return {self.cursor_field: self.start_date.strftime("%Y-%m-%d")}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], "%Y-%m-%d")


class ExchangeRates(IncrementalExchangeRatesTutorialStream):
    cursor_field = "date"
    primary_key = "date"

    def __init__(self, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__()
        self.config = config
        self.start_date = start_date
        self.access_key = config["access_key"]

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"access_key": self.access_key}

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return stream_slice["date"]

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, any]]:
        dates = []
        while start_date < datetime.now():
            self.logger.info(start_date.strftime("%Y-%m-%d"))
            dates.append({"date": start_date.strftime("%Y-%m-%d")})
            start_date += timedelta(days=1)

        return dates

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        start_date = datetime.strptime(stream_state["date"], "%Y-%m-%d") if stream_state and "date" in stream_state else self.start_date
        return self._chunk_date_range(start_date)


# Source
class SourceExchangeRatesTutorial(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            params = {"access_key": config["access_key"]}
            base = config.get("base")
            if base is not None:
                params["base"] = base

            resp = requests.get(f"{ExchangeRates.url_base}{config['start_date']}", params=params)
            status = resp.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None

            error = resp.json().get("error")
            code = error.get("code")
            message = error.get("message") or error.get("info")

            if code == "base_currency_access_restricted":
                message = f"{message} (this plan doesn't support selecting the base currency)"
            return False, message
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        return [ExchangeRates(authenticator=auth, config=config, start_date=start_date)]
