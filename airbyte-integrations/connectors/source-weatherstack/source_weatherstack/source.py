#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth

from .constants import url_base


class CurrentWeather(HttpStream):
    url_base = "https://api.weatherstack.com/"

    # Set this as a noop.
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.query = config["query"]
        self.access_key = config["access_key"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        # The "/current" path gives us the latest current city weather
        return "current"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include api_key as a query param so we do that in this method
        return {"access_key": self.access_key, "query": self.query}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination,
        # so we return None to indicate there are no more pages in the response
        return None


class Weatherstack(HttpStream):
    url_base = "https://api.weatherstack.com/"

    # Set this as a noop.
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.query = config["query"]
        self.access_key = config["access_key"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        # The "/current" path gives us the latest current city weather
        return "current"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include api_key as a query param so we do that in this method
        return {"access_key": self.access_key, "query": self.query}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination,
        # so we return None to indicate there are no more pages in the response
        return None


class IncrementalWeatherstack(HttpStream):
    url_base = "https://api.weatherstack.com/"

    # Set this as a noop.
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.query = config["query"]
        self.access_key = config["access_key"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        # The "/current" path gives us the latest current city weather
        return "current"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include api_key as a query param so we do that in this method
        return {"access_key": self.access_key, "query": self.query}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination,
        # so we return None to indicate there are no more pages in the response
        return None


class Forecast(HttpStream):
    url_base = "https://api.weatherstack.com/"

    # Set this as a noop.
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.query = config["query"]
        self.access_key = config["access_key"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        # The "/current" path gives us the latest current city weather
        return "forecast"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include api_key as a query param so we do that in this method
        return {"access_key": self.access_key, "query": self.query}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination,
        # so we return None to indicate there are no more pages in the response
        return None


class Historical(HttpStream):
    url_base = "https://api.weatherstack.com/"

    # Set this as a noop.
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.query = config["query"]
        self.access_key = config["access_key"]
        self.historical_date = config["historical_date"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "historical"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include api_key as a query param so we do that in this method
        return {"access_key": self.access_key, "query": self.query, "historical_date": self.historical_date}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination,
        # so we return None to indicate there are no more pages in the response
        return None


class LocationLookup(HttpStream):
    url_base = "https://api.weatherstack.com/"

    # Set this as a noop.
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.query = config["query"]
        self.access_key = config["access_key"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "autocomplete"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include api_key as a query param so we do that in this method
        return {"access_key": self.access_key, "query": self.query}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination,
        # so we return None to indicate there are no more pages in the response
        return None


# Source
class SourceWeatherstack(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        try:
            query = config["query"]
            access_key = config["access_key"]

            response = requests.get(f"{url_base}/current?access_key={access_key}&query={query}")
            response = response.text

            if response.find('"success": false') != -1:
                return False, "Check Query and Access Key"
            else:
                return True, None
        except requests.exceptions.RequestException as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        streams = [
            CurrentWeather(authenticator=auth, config=config),
            Forecast(authenticator=auth, config=config),
        ]

        # Historical stream is only supported by paid accounts
        if config["is_paid_account"] is not False:
            streams.append(LocationLookup(authenticator=auth, config=config))
            streams.append(Historical(authenticator=auth, config=config))

        return streams
