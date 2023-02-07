#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth


class ExchangeRates(HttpStream):
    url_base = "https://api.apilayer.com/exchangerates_data/"
    cursor_field = "date"
    primary_key = "date"

    def __init__(self, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__()
        self.base = config["base"]
        self.access_key = config["access_key"]
        self.start_date = start_date
        self._cursor_value = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination, so we return None to indicate there are no more pages in the response
        return None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return stream_slice["date"]

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # The api requires that we include apikey as a header so we do that in this method
        return {'apikey': self.apikey}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include the base currency as a query param so we do that in this method
        return {'base': self.base}

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

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        # This method is called once for each record returned from the API to compare the cursor field value in that record with the current state
        # we then return an updated state object. If this is the first time we run a sync or no state was passed, current_stream_state will be None.
        if current_stream_state is not None and "date" in current_stream_state:
            current_parsed_date = datetime.strptime(current_stream_state["date"], "%Y-%m-%d")
            latest_record_date = datetime.strptime(latest_record["date"], "%Y-%m-%d")
            return {"date": max(current_parsed_date, latest_record_date).strftime("%Y-%m-%d")}
        else:
            return {"date": self.start_date.strftime("%Y-%m-%d")}

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, any]]:
        """
        Returns a list of each day between the start date and now.
        The return value is a list of dicts {'date': date_string}.
        """
        dates = []
        while start_date < datetime.now():
            self.logger.info(start_date.strftime("%Y-%m-%d"))
            dates.append({"date": start_date.strftime("%Y-%m-%d")})
            start_date += timedelta(days=1)

        return dates

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        start_date = datetime.strptime(stream_state["date"], "%Y-%m-%d") if stream_state and "date" in stream_state else self.start_date
        return self._chunk_date_range(start_date)


class SourcePythonHttpTutorial(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        accepted_currencies = {
            "USD",
            "JPY",
            "BGN",
            "CZK",
            "DKK",
        }  # there are more currencies but let's assume these are the only allowed ones
        input_currency = config["base"]
        if input_currency not in accepted_currencies:
            return False, f"Input currency {input_currency} is invalid. Please input one of the following currencies: {accepted_currencies}"
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API. It's only included for completeness
        # of the example, but if you don't need authentication, you don't need to pass an authenticator at all.
        # Other authenticators are available for API token-based auth and Oauth2.
        auth = NoAuth()
        # Parse the date from a string into a datetime object
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        return [ExchangeRates(authenticator=auth, config=config, start_date=start_date)]
