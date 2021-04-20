"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from base_python import AbstractSource, HttpStream, Stream
from pendulum import DateTime


class ExchangeRates(HttpStream):
    url_base = "https://api.ratesapi.io/"
    date_field_name = "date"

    def __init__(self, base: str, start_date: DateTime):
        super().__init__()
        # validate base is a valid symbol
        self._base = base
        self._start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        # how do we set the slices? and state? and pull this out?
        print("path")
        print(f"{stream_state}")
        print(f"{stream_slice}")
        return f"api/{stream_slice[self.date_field_name]}"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = {"base": self._base}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from [response_json]

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        print("stream_slices")
        stream_state = stream_state or {}
        start_date = pendulum.parse(stream_state.get(self.date_field_name, self._start_date))
        return chunk_date_range(start_date)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        current_stream_state = current_stream_state or {}
        print("get_updated_state")
        # how do we compare dates?
        print(f"{latest_record}")
        # okay how do we convert this from date to timestamp?
        current_stream_state[self.date_field_name] = max(
            float(latest_record[self.date_field_name]), current_stream_state.get(self.date_field_name, 0)
        )
        return {}


def chunk_date_range(start_date: DateTime) -> Iterable[Mapping[str, any]]:
    """
    Returns a list of the beginning and ending timetsamps of each day between the start date and now.
    The return value is a list of dicts {'oldest': float, 'latest': float} which can be used directly with the Slack API
    """
    print("chunk_date_range")
    days = []
    now = pendulum.now()
    while start_date <= now:
        days.append({"date": f"{start_date.year}-{start_date.month}-{start_date.day}"})
        start_date = start_date.add(days=1)
    return days


class SourceExchangeRates(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            resp = requests.get(ExchangeRates.url_base)
            status = resp.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None
            return False, resp.text
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [ExchangeRates(config["base"], config["start_date"])]
