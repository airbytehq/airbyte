#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from pendulum import DateTime


class OpenExchangeRates(HttpStream, ABC):
    url_base = "https://openexchangerates.org/api/"

    primary_key = None
    cursor_field = "timestamp"

    def __init__(self, base: Optional[str], start_date: str, app_id: str, **kwargs: dict) -> None:
        super().__init__(**kwargs)

        self.base = base
        self.start_date = pendulum.parse(start_date)
        self.app_id = app_id
        self._cursor_value = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {}

        if self.base is not None:
            params["base"] = self.base

        return params

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self.start_date.timestamp()}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        response_json = response.json()

        latest_record_timestamp = response_json["timestamp"]
        if self._cursor_value and latest_record_timestamp <= self._cursor_value:
            return
        if self._cursor_value:
            self._cursor_value = max(self._cursor_value, latest_record_timestamp)
        else:
            self._cursor_value = latest_record_timestamp

        yield response_json

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = stream_state[self.cursor_field] if stream_state and self.cursor_field in stream_state else self.start_date

        if isinstance(start_date, int):
            start_date = pendulum.from_timestamp(start_date)

        return self._chunk_date_range(start_date)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"historical/{stream_slice['date']}.json"

    def _chunk_date_range(self, start_date: DateTime) -> List[Mapping[str, Any]]:
        """
        Returns a list of each day between the start date and now.
        The return value is a list of dicts {'date': date_string}.
        """
        dates = []

        while start_date < pendulum.now():
            dates.append({"date": start_date.to_date_string()})
            start_date = start_date.add(days=1)
        return dates


# Source
class SourceOpenExchangeRates(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Checks the connection by sending a request to /usage and checks the remaining quota

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            auth = TokenAuthenticator(token=config["app_id"], auth_method="Token").get_auth_header()

            resp = requests.get(f"{OpenExchangeRates.url_base}usage.json", headers=auth)
            status = resp.status_code

            logger.info(f"Ping response code: {status}")
            response_dict = resp.json()

            if status == 200:
                quota_remaining = response_dict["data"]["usage"]["requests_remaining"]

                if quota_remaining > 0:
                    return True, None

                return False, "Quota exceeded"
            else:
                description = response_dict.get("description")
                return False, description
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = TokenAuthenticator(token=config["app_id"], auth_method="Token")

        return [OpenExchangeRates(base=config["base"], start_date=config["start_date"], app_id=config["app_id"], authenticator=auth)]
