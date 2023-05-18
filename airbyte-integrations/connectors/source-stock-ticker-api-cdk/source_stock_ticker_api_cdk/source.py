#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class StockPrices(HttpStream):
    url_base = "https://api.polygon.io/v2/aggs/ticker/"
    cursor_field = "date"
    primary_key = "date"

    def __init__(self, stock_ticker: str, start_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self.stock_ticker = stock_ticker
        self.start_date = start_date
        self._cursor_value = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_dict = response.json()
        return {"next_url": response_dict["next_url"]} if "next_url" in response_dict else None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return (
            next_page_token["next_url"]
            if next_page_token
            else f"{self.stock_ticker}/range/1/day/{stream_slice['start_date']}/{stream_slice['end_date']}"
        )

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include the base currency as a query param so we do that in this method
        return {"sort": "asc", "limit": 10}

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
        if response_dict.get("resultsCount"):
            for day_result in response_dict.get("results", []):
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
            end_date_str = (start_date + timedelta(days=30)).strftime("%Y-%m-%d")
            self.logger.info(f"Date range: {start_date_str} - {end_date_str}")
            dates.append({"start_date": start_date_str, "end_date": end_date_str})
            start_date += timedelta(days=31)

        return dates

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        start_date = datetime.strptime(stream_state["date"], "%Y-%m-%d") if stream_state and "date" in stream_state else self.start_date
        return self._chunk_date_range(start_date)


class SourceStockTickerApiCdk(AbstractSource):
    @staticmethod
    def _get_stream_kwargs(config: Mapping[str, Any]) -> dict:
        stream_kwargs = {"authenticator": TokenAuthenticator(token=config["api_key"]), "stock_ticker": config["stock_ticker"]}
        stream_kwargs["start_date"] = (
            datetime.strptime(config["start_date"], "%Y-%m-%d") if "start_date" in config else datetime.now() - timedelta(days=30)
        )
        return stream_kwargs

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        # Validate input configuration by attempting to get the daily closing prices of the input stock ticker
        try:
            stock_prices_stream = StockPrices(**self._get_stream_kwargs(config))
            # use the first slice from stream_slices list
            stream_slice = stock_prices_stream.stream_slices(sync_mode=SyncMode.full_refresh)[0]
            next(stock_prices_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [StockPrices(**self._get_stream_kwargs(config))]
