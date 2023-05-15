#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth


class StockPrices(HttpStream):
    url_base = "https://api.polygon.io/v2/aggs/ticker/"
    cursor_field = "date"
    primary_key = "date"

    def __init__(self, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.stock_ticker = config["stock_ticker"]
        self.start_date = start_date
        self._cursor_value = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination, so we return None to indicate there are no more pages in the response
        return None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.stock_ticker}/range/1/day/{stream_slice['start_date']}/{stream_slice['end_date']}"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # The api requires that we include apikey as a header so we do that in this method
        return {"Authorization": f"Bearer {self.api_key}"}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include the base currency as a query param so we do that in this method
        return {"sort": "asc", "limit": 120}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # The response is a simple JSON whose schema matches our stream's schema exactly,
        # so we just return a list containing the response
        response_dict = response.json()
        data = []
        if response_dict["resultsCount"]:
            for day_result in response_dict["results"]:
                data.append(
                    {
                        "date": datetime.fromtimestamp(day_result["t"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
                        "stock_ticker": self.stock_ticker,
                        "price": day_result["c"],
                    }
                )
        return data

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        # This method is called once for each record returned from the API to compare the cursor field value in that record with the current state
        # we then return an updated state object. If this is the first time we run a sync or no state was passed, current_stream_state will be None.
        if current_stream_state is not None and "date" in current_stream_state:
            current_parsed_date = datetime.strptime(current_stream_state["date"], "%Y-%m-%d")
            latest_record_date = datetime.strptime(latest_record["date"], "%Y-%m-%d")
            return {"date": max(current_parsed_date, latest_record_date).strftime("%Y-%m-%d")}
        else:
            return {"date": self.start_date.strftime("%Y-%m-%d")}

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, str]]:
        """
        Returns a list of dicts with start and end date for each week between the start date and now.
        The return value is a list of dicts {'start_date': date_string, 'end_date': date_string}.
        """
        dates = []
        while start_date < datetime.now():
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = (start_date + timedelta(days=7)).strftime("%Y-%m-%d")
            self.logger.info(f"Date range: {start_date_str} - {end_date_str}")
            dates.append({"start_date": start_date_str, "end_date": end_date_str})
            start_date += timedelta(days=8)

        return dates

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        start_date = datetime.strptime(stream_state["date"], "%Y-%m-%d") if stream_state and "date" in stream_state else self.start_date
        return self._chunk_date_range(start_date)


def _call_api(ticker, token, from_day, to_day):
    return requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{from_day}/{to_day}?sort=asc&limit=120&apiKey={token}")


class SourceStockTickerApiCdk(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        # Validate input configuration by attempting to get the daily closing prices of the input stock ticker
        response = _call_api(
            ticker=config["stock_ticker"],
            token=config["api_key"],
            from_day=datetime.now().date() - timedelta(days=1),
            to_day=datetime.now().date(),
        )
        if response.status_code == 200:
            return True, None
        elif response.status_code == 403:
            # HTTP code 403 means authorization failed so the API key is incorrect
            return False, "API Key is incorrect."
        else:
            return False, "Input configuration is incorrect. Please verify the input stock ticker and API key."

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API. It's only included for completeness
        # of the example, but if you don't need authentication, you don't need to pass an authenticator at all.
        # Other authenticators are available for API token-based auth and Oauth2.
        auth = NoAuth()
        # Parse the date from a string into a datetime object
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d") if "start_date" in config else datetime.now()
        return [StockPrices(authenticator=auth, config=config, start_date=start_date)]
