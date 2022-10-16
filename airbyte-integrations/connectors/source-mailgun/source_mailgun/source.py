#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import logging
import time
from abc import ABC
from numbers import Number
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urljoin

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from pydantic import HttpUrl
from requests.auth import HTTPBasicAuth

DOMAIN_BY_REGION = {"EU": "https://api.eu.mailgun.net/", "US": "https://api.mailgun.net/"}


class MailgunStream(HttpStream, ABC):
    """
    Base class for Mailgun streams.
    Provides common streams' functionality.
    """

    primary_key: str = None

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        region = config.get("domain_region", "US")
        self._url_base: HttpUrl = urljoin(DOMAIN_BY_REGION[region], "v3/")

    @property
    def url_base(self) -> HttpUrl:
        return self._url_base

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, HttpUrl]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        next_page: Optional[HttpUrl] = response.json().get("paging", {}).get("next")
        return {"url": next_page} if next_page and self._pre_parse_response(response) else None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Optional[Mapping[str, HttpUrl]] = None,
    ) -> str:
        return next_page_token["url"] if next_page_token else ""

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from self._pre_parse_response(response)

    @staticmethod
    def _pre_parse_response(response: requests.Response) -> List:
        return response.json()["items"]


class Domains(MailgunStream):
    """
    "Domains" stream.
    API reference is here: https://documentation.mailgun.com/en/latest/api-domains.html
    """

    primary_key: str = "name"

    def path(self, *args, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return super().path(*args, next_page_token=next_page_token, **kwargs) or "domains"


class IncrementalMailgunStream(MailgunStream, ABC):
    """
    Base class for incremental Mailgun streams.
    Provides common functionality for incremental streams.
    """

    # Messages are stored for 3 days, so it prevents occasional attempt to read from the start of the Epoch
    default_shift: datetime.datetime = pendulum.duration(3)

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        super().__init__(*args, config=config, **kwargs)

        try:
            if "start_date" in config:
                start_date = pendulum.parse(config["start_date"])
            else:
                start_date = pendulum.now() - self.default_shift

        except pendulum.parsing.exceptions.ParserError as e:
            raise ValueError(f"Unrecognized date format. {e}")

        self.start_timestamp: Number = start_date.timestamp()

    @staticmethod
    def chunk_timestamps_range(start_timestamp: Number, interval: Number = 60 * 60 * 24) -> Iterable[Tuple[Number]]:
        """
        Yield a tuple of beginning and ending timestamps of each day between the start timestamp and end timestamp.
        """
        end: Number = time.time()
        if start_timestamp > end:
            yield start_timestamp, start_timestamp

        while start_timestamp <= end:
            end_timestamp = start_timestamp + interval
            yield start_timestamp, end_timestamp
            start_timestamp = end_timestamp


class Events(IncrementalMailgunStream):
    """
    "Events" stream.
    API reference is here: https://documentation.mailgun.com/en/latest/api-events.html
    """

    # TODO: Event Polling. See https://documentation.mailgun.com/en/latest/api-events.html#event-polling

    cursor_field: str = "timestamp"

    primary_key: str = "id"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_timestamp = latest_record.get(self.cursor_field, self.start_timestamp)
        if current_stream_state and self.cursor_field in current_stream_state:
            latest_timestamp = max(latest_timestamp, current_stream_state[self.cursor_field])

        return {self.cursor_field: latest_timestamp}

    def path(self, *args, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return super().path(*args, next_page_token=next_page_token, **kwargs) or "events"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params: MutableMapping[str, Any] = super().request_params(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )
        params.update(stream_slice)
        if stream_state:
            params["begin"] = stream_state[self.cursor_field]

        # If "end" parameter is not provided, it's required to define a search direction.
        # See https://documentation.mailgun.com/en/latest/api-events.html#time-range
        if "end" not in params:
            params["ascending"] = "yes"
        return params

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, float]]]:
        """
        Provide a generator of date_slices in such format:
        {"begin": 1636411500.0, "end": 1636497900.0}
        """
        stream_state = stream_state or {}
        start_date = stream_state.get(self.cursor_field, self.start_timestamp)
        for period in self.chunk_timestamps_range(start_date):
            yield {"begin": period[0], "end": period[1]}


class SourceMailgun(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            region = config.get("domain_region", "US")
            try:
                url = urljoin(DOMAIN_BY_REGION[region], "v3/domains")
            except KeyError:
                return False, f"'domain_region' has to be one of {list(DOMAIN_BY_REGION)} or to be omitted"

            response = requests.get(url, auth=("api", config["private_key"]))
            if response.status_code == 200:
                return True, None
            else:
                message = "Connection check failed. "
                try:
                    message += response.json()["message"]
                except json.JSONDecodeError:
                    message += f"Unexpected response format from the server. It returns:\n{response.text}"
                finally:
                    return False, message
        except requests.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = HTTPBasicAuth("api", config["private_key"])

        return [Domains(config=config, authenticator=auth), Events(config=config, authenticator=auth)]
