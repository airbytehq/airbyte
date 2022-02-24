#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#



from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
import re
from airbyte_cdk.sources.streams.http import HttpStream
from pendulum import DateTime

from airbyte_cdk.sources.utils.sentry import AirbyteSentry
from airbyte_cdk.models import (
    SyncMode
)


class IncrementalOpenExchangeRatesStream(HttpStream):
    # HttpStream related fields
    url_base = "https://openexchangerates.org/api/historical/"
    primary_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return self._request_params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()

        # remove unwanted disclaimer and licence urls
        response_json.pop("disclaimer", None)
        response_json.pop("license", None)

        yield response_json

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Overrides HttpStream::read_records to add logging
        """
        stream_state = stream_state or {}
        pagination_complete = False

        next_page_token = None
        with AirbyteSentry.start_transaction("read_records", self.name), AirbyteSentry.start_transaction_span("read_records"):
            if stream_slice is not None:
                while not pagination_complete:
                    request_headers = self.request_headers(
                        stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
                    )
                    request = self._create_prepared_request(
                        path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                        headers=dict(request_headers, **self.authenticator.get_auth_header()),
                        params=self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                        json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                        data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                    )
                    request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

                    # log request url with obfuscated app_id
                    log_request = re.sub("app_id=[^&]+&", "app_id=********&", request.url)
                    self.logger.debug(f"Sending http request {log_request}")
                    
                    if self.use_cache:
                        # use context manager to handle and store cassette metadata
                        with self.cache_file as cass:
                            self.cassete = cass
                            # vcr tries to find records based on the request, if such records exist, return from cache file
                            # else make a request and save record in cache file
                            response = self._send_request(request, request_kwargs)

                    else:
                        response = self._send_request(request, request_kwargs)
                    yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)

                    next_page_token = self.next_page_token(response)
                    if not next_page_token:
                        pagination_complete = True

            # Always return an empty generator just in case no records were ever yielded
            yield from []


class HistoricalExchangeRates(IncrementalOpenExchangeRatesStream):
    cursor_field = ["timestamp"]

    def __init__(
        self,
        app_id: str,
        start_date: DateTime,
        base: Optional[str] = None,
        symbols: Optional[str] = None,
        show_alternative: Optional[bool] = False,
        prettyprint: Optional[bool] = False,
        ignore_current_day: Optional[bool] = True,
        ignore_weekends: Optional[bool] = False,
        max_records_per_sync: Optional[int] = None
        ):
        super().__init__()

        self._request_params = {
            "app_id": app_id.strip(),
            "start_date": start_date.strip(),
            "show_alternative": show_alternative,
            "prettyprint": prettyprint
        }

        if isinstance(base, str) and base.strip() != "":
            self._request_params["base"] = base.strip()

        if isinstance(symbols, str) and symbols.strip() != "":
            self._request_params["symbols"] = symbols.strip()


        self._ignore_current_day = ignore_current_day
        self._ignore_weekends = ignore_weekends
        self._max_records_per_sync = max_records_per_sync
        

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{stream_slice['date']}.json"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_state = stream_state or {}

        # we compute the last date to fetch, either the current or previous day
        now = pendulum.now(pendulum.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = now if self._ignore_current_day else now.add(days=1)

        # we get the start date from the start_date user input or from the stream state
        start_date = pendulum.parse(self._request_params["start_date"])
        if stream_state.get(self.cursor_field[0]) is not None:
            start_date_stream_state = pendulum.from_timestamp(stream_state.get(self.cursor_field[0])).add(days=1)
        
            if start_date_stream_state > start_date:
                start_date = start_date_stream_state

        # we return no slices if the start date is greater than the max date
        slices = []
        if start_date >= max_date:
            return [None]

        # we override the last date to fetch, if the user has specified a max of records per sync
        if isinstance(self._max_records_per_sync, int) and self._max_records_per_sync > 0:
            diff = max_date.diff(start_date).in_days()
            if diff > self._max_records_per_sync:
                
                max_date = min(start_date.add(days=self._max_records_per_sync), max_date)

        # we generate the slices, either with weekend rates or not
        while start_date < max_date:
            day_of_week = start_date.day_of_week
            if day_of_week != pendulum.SATURDAY and day_of_week != pendulum.SUNDAY or not self._ignore_weekends:
                slices.append({"date": start_date.to_date_string()})
            start_date = start_date.add(days=1)

        # we log days to be synced
        days = [slice["date"] for slice in slices]
        self.logger.info(f"Remaining exchange rates to sync: {str(len(days))} days from {days[0]} to {days[-1]}")

        return slices

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        current_stream_state = current_stream_state or {}
        current_stream_state[self.cursor_field[0]] = max(
            latest_record[self.cursor_field[0]], current_stream_state.get(self.cursor_field[0], pendulum.parse(self._request_params["start_date"]).timestamp())
        )
        return current_stream_state


    def chunk_date_range(self, start_date: DateTime, ignore_current_day: bool, ignore_weekends: bool) -> Iterable[Mapping[str, Any]]:
        """
        Returns a list of each day between the start date and now. Ignore weekends since exchanges don't run on weekends.
        The return value is a list of dicts {'date': date_string}.
        """
        days = []
        now = pendulum.now(pendulum.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = now if ignore_current_day else now.add(days=1)

        while start_date < max_date:
            day_of_week = start_date.day_of_week
            if day_of_week != pendulum.SATURDAY and day_of_week != pendulum.SUNDAY or not ignore_weekends:
                days.append({"date": start_date.to_date_string()})
            start_date = start_date.add(days=1)

        return days

