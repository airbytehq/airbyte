#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class OneCall(HttpStream):

    cursor_field = ["current", "dt"]
    url_base = "https://api.openweathermap.org/data/3.0/"
    primary_key = None

    def __init__(self, appid: str, lat: float, lon: float, lang: str = None, units: str = None):
        super().__init__()
        self.appid = appid
        self.lat = lat
        self.lon = lon
        self.lang = lang
        self.units = units

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "onecall"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = {"appid": self.appid, "lat": self.lat, "lon": self.lon, "lang": self.lang, "units": self.units}
        params = {k: v for k, v in params.items() if v is not None}
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        data = response.json()
        if data["current"]["dt"] >= stream_state.get("dt", 0):
            return [data]
        else:
            return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        current_stream_state = current_stream_state or {"dt": 0}
        current_stream_state["dt"] = max(latest_record["current"]["dt"], current_stream_state["dt"])
        return current_stream_state

    def should_retry(self, response: requests.Response) -> bool:
        # Do not retry in case of 429 because the account is blocked for an unknown duration.
        return 500 <= response.status_code < 600
